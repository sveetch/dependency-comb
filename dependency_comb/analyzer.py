import json
import time

from operator import itemgetter

import requests
from packaging.version import Version, InvalidVersion

from .exceptions import AnalyzerError, AnalyzerAPIError
from .parser import RequirementParser
from .utils.lists import split_to_chunks
from .utils.logger import NoOperationLogger
from .utils.dates import safe_isoformat_parse
from . import __pkgname__, __version__


class DependenciesAnalyzer(RequirementParser):
    """
    Analyzer to get and compute package informations from Pypi for requirements.

    This will need to make 2 requests to get needed informations for each package since
    the package detail endpoint from new "JSON API" has releases informations but it
    is deprecated in profit of the Legacy API.

    Legacy API (also known as the "Simple API") return either a HTML or JSON response,
    depending value of request header "Accept:".

    Attributes:
        PACKAGE_DETAIL_ENDPOINT (string): Template string to build URL to the Pypi
            JSON API to get package details.
        PACKAGE_RELEASES_ENDPOINT (string): Template string to build URL to the Pypi
            Legacy API to get package releases.
    """
    PACKAGE_DETAIL_ENDPOINT = "https://pypi.org/pypi/{name}/json"
    PACKAGE_RELEASES_ENDPOINT = "https://pypi.org/simple/{name}/"

    def __init__(self, cachedir=None, api_pause=1, api_timeout=None, api_chunk=None,
                 logger=None, ignores=None):
        self.cachedir = cachedir
        self.logger = logger or NoOperationLogger()
        # Amount of requirements to analyze by chunk
        self.api_chunk = api_chunk or 10
        # Time in seconds to pause before an API request
        # Pause time between chunks
        self.api_pause = api_pause
        # Time in seconds for timeout limit on API request
        self.api_timeout = api_timeout
        # TODO: Currently not implemented, it should be a list of package names to
        # ignore from analyze, dont know the state it will end in. It could be helpful
        # for bypassing some erroneous requirements without breaking the whole analyze.
        self.ignores = ignores or []

    def request_headers(self):
        """
        Define the custom headers to use in requests to the API.

        Returns:
            dict: Dictionnary of headers to use in a request.
        """
        return {
            "user-agent": "{name}/{version}".format(
                name=__pkgname__,
                version=__version__,
            ),
            # This specific 'accept' header (application/json won't work) is only
            # required from Legacy API but JSON API ignores it, so let it be a global
            # header
            "Accept": "application/vnd.pypi.simple.v1+json",
        }

    def endpoint_package_detail(self, name):
        """
        Request package detail API endpoint for given package name.

        Arguments:
            name (string): The package name to search for.

        Returns:
            requests.Response: Response object from request.
        """
        endpoint_url = self.PACKAGE_DETAIL_ENDPOINT.format(name=name)
        response = requests.get(
            endpoint_url,
            headers=self.request_headers(),
            timeout=self.api_timeout,
        )

        if response.status_code == 404:
            raise AnalyzerAPIError(
                (
                    "API responded a 404 error, package name '{}' is probably "
                    "invalid or not available on Pypi."
                ).format(name),
                http_status=404
            )

        # In case we have an error status that is not taken in charge before
        response.raise_for_status()

        return response

    def endpoint_releases_detail(self, name):
        """
        Request package releases API endpoint for given package name.

        Arguments:
            name (string): The package name to search for.

        Returns:
            requests.Response: Response object from request.
        """
        endpoint_url = self.PACKAGE_RELEASES_ENDPOINT.format(name=name)
        response = requests.get(
            endpoint_url,
            headers=self.request_headers(),
            timeout=self.api_timeout,
        )

        if response.status_code == 404:
            raise AnalyzerAPIError(
                (
                    "API responded a 404 error, package name '{}' is probably "
                    "invalid or not available on Pypi."
                ).format(name),
                http_status=404
            )

        # In case we have an error status that is not taken in charge before
        response.raise_for_status()

        return response

    def get_cache_or_request(self, name, filename, method, label):
        """
        Helper to search for a cache before making request if there is none.

        Arguments:
            name (string): The package name to search for.
            filename (string): Filename to write cache. It should include the label to
                ensure they won't overwrite each other.
            method (callable): Callable that will perform a request to get JSON
                payload. The callable is expected to accept a single argument which is
                a package name to request.
            label (string): Label of informations kind. Commonly it is ``detail`` or
                ``releases``.

        Returns:
            dict: Returned payload from API or from stored cache.
        """
        self.logger.debug("Get package {label} for '{name}'".format(
            label=label,
            name=name or "Unknow"
        ))

        # Mostly impossible to be there but just in case there is an unexpected issue
        if not name:
            raise AnalyzerError("Package without name can not be requested.")

        # Build expected cache file name if cache is enabled
        cache_file = None
        if self.cachedir:
            cache_file = self.cachedir / filename

        # Return cache if it exists
        if cache_file and cache_file.exists():
            self.logger.debug("Loading data from cache")
            return json.loads(cache_file.read_text())

        # Use given method name to request payload from API
        response = method(name)

        self.logger.debug("[{status}] API response from {url}".format(
            status=response.status_code,
            url=response.url.split("?")[0],
        ))
        output = response.json()

        # Build cache file if cache is enabled
        if self.cachedir:
            self.logger.debug("Writing cache: {}".format(cache_file))
            cache_file.write_text(json.dumps(output, indent=4))

        return output

    def format_releases_payload(self, payload):
        """
        Format package release payload to an useful one.

        This means we just need each version with its uploading date, everything else
        is useless from this application view.

        .. Note::
            Version data is only available from the files, since release tarball is
            standardized well enough we naively parsing the file name to extract the
            version number.

        Arguments:
            payload (dict): The package releases payload as returned from Legacy API
                endpoint. For true we just need about the ``files`` item from this
                dict.

        Returns:
            list: List of dictionnaries for all version, each one contain the ``number``
            and ``published_at`` items.
        """
        return [
            {
                "number": item["filename"].replace(
                    "-reupload",
                    ""
                ).split(
                    "-"
                )[-1].replace(
                    ".tar.gz",
                    ""
                ),
                "published_at": item["upload-time"],
            }
            for item in payload["files"]
            if item["filename"].endswith(".tar.gz")
        ]

    def get_package_data(self, name):
        """
        Get package informations (detail and releases)

        Arguments:
            name (string): The package name to search for.

        Returns:
            dict: A dictionnary that contain all useful package informations (detail
            and releases).
        """
        self.logger.info("Processing package: {name}".format(
            name=name or "Unknow"
        ))

        if not name:
            raise AnalyzerError("Package without name can not be requested.")

        # Patch detail to inject released versions
        output = self.get_cache_or_request(
            name,
            "{}.detail.json".format(name),
            self.endpoint_package_detail,
            "detail",
        )
        output["versions"] = self.format_releases_payload(
            self.get_cache_or_request(
                name,
                "{}.releases.json".format(name),
                self.endpoint_releases_detail,
                "releases",
            )
        )

        return output

    def compute_package_releases(self, name, data):
        """
        Build a list of released versions from API patched with some values in useful
        types.

        Arguments:
            name (string): Parsed package name.
            data (dict): Dictionnary of package data as retrieved from API.

        Returns:
            list: List of dictionnary for computed releases.
        """
        versions = []

        # Rebuild the version list to patch some values in useful types
        for item in data["versions"]:
            # Enforce real datetime
            item["published_at"] = safe_isoformat_parse(item["published_at"])

            # Coerce original number to a Version object if possible
            try:
                number = Version(item["number"])
            except InvalidVersion:
                msg = (
                    "Ignored invalid version number '{version}' for package '{name}'"
                )
                self.logger.warning(msg.format(name=name, version=item["number"]))
                continue
            else:
                item["number"] = number
                versions.append(item)

        return sorted(versions, key=itemgetter("number"))

    def get_latest_specified_release(self, specifiers, releases):
        """
        Get the latest release that match given specifiers on given release list.

        Pre releases are always ignored.

        Arguments:
            specifiers (packaging.SpecifierSet): Version specifiers to match against
                releases.
            releases (list): List of dict for releases as built from
                ``DependenciesAnalyzer.compute_package_releases()``.

        Returns:
            dict: Dictionnary of release data taken from given releases if it matched
            specifier. Else returns a null value.
        """
        indexed = {
            str(item["number"]): item
            for item in releases
        }
        matched = sorted(
            specifiers.filter(
                [str(item["number"]) for item in releases],
                prereleases=False
            ),
        )

        if not matched:
            return None

        return indexed[matched[-1]]

    def compute_lateness(self, target, versions):
        """
        Compute version lateness for a given version target.

        Lateness is only about version higher than targeted version and that are not
        build releases or pre releases

        Arguments:
            target (string or packaging.version.Version): The targeted version
                to check against package released versions. If a string it will be
                coerced to a ``Version`` object.
            versions (list): List of dictionnaries (as computed from
                ``build_package_informations()``) for all existing release versions.

        Returns:
            list: A list of tuples for all existing version higher
                than given target release version. Tuple first item is the version
                number (as a ``Version`` object and second item is its
                release publishing datetime.
        """
        if not isinstance(target, Version):
            target = Version(target)

        return [
            (str(item["number"]), item["published_at"])
            for item in versions
            if (
                item["number"] > target and
                item["number"].is_prerelease is False and
                item["number"].is_postrelease is False and
                item["number"].is_devrelease is False
            )
        ]

    def get_package_urls(self, data):
        """
        This should try to get the relevant URLs from package metadatas.

        However the ``project_urls`` item from package metadatas is not normalized
        enough to quickly get relevant infos so here we should try to get them.

        Arguments:
            data (dict): Dictionnary of package informations as returned from
            ``Analyzer.get_package_data()``.

        Returns:
            dict: A dictionnary that contains useful URLs.
        """
        informations = data["info"]
        urls = informations.get("project_urls", {})

        repository_url = None
        elligible_repo_url_names = ["repository", "source", "source code"]
        for name, value in urls.items():
            if name.lower() in elligible_repo_url_names:
                repository_url = value
                break

        return {
            "package": informations["package_url"],
            "repository": repository_url,
        }

    def build_package_informations(self, requirement):
        """
        Compute and set informations in a ``PackageRequirement`` object.

        Arguments:
            requirement (PackageRequirement): The package object for to search
                informations from Pypi.

        Returns:
            PackageRequirement: The package object.
        """
        if requirement.status == "parsed":
            data = self.get_package_data(requirement.name)
            urls = self.get_package_urls(data)

            requirement.status = "analyzed"
            requirement.pypi_url = urls["package"]
            requirement.repository_url = urls["repository"]
            requirement.highest_version = Version(data["info"]["version"])

            # Once numbers have been coerced they can be used to reorder versions
            # properly on number
            versions = self.compute_package_releases(requirement.name, data)

            if requirement.specifier:
                # Match the highest elligible release
                resolved = self.get_latest_specified_release(
                    requirement.specifier,
                    versions
                )
                if resolved:
                    requirement.resolved_version = resolved["number"]
                    requirement.resolved_published = resolved["published_at"]

            # Highest released version
            requirement.highest_published = versions[-1]["published_at"]

            # Compute version lateness if a version has been given
            if requirement.resolved_version:
                requirement.lateness = self.compute_lateness(
                    requirement.resolved_version,
                    versions
                )

        return requirement

    def inspect(self, requirements, environment=None, strict=False, basepath=None):
        """
        Inspect given requirement to get their informations.

        Arguments:
            requirements (string or Path): Either a Path object for a file to open or
                directly requirements content as a string.

        Keyword Arguments:
            environment (dict): Optionnal dictionnary of environment variables to use
            with possible specifier marker resolution.
            strict (boolean): If True only the valid requirements (see
                ``dependency_comb.package.PackageRequirement.is_valid``) are returned.
                Default is False, all requirements are returned and you need to check
                their status yourself if needed.
            basepath (Path): A directory path where to search for requirement
                inclusions (directive ``-r foo.txt``) from requirements file.

        Returns:
            iterator: Iterator of PackageRequirement objects for given requirements.
        """
        parsed_requirements = self.parse_requirements(
            requirements,
            environment=environment,
            basepath=basepath,
        )

        #
        if self.api_chunk:
            chunks = list(split_to_chunks(parsed_requirements, self.api_chunk))
        else:
            chunks = [parsed_requirements]

        for i, chunk in enumerate(chunks, start=1):
            for item in chunk:
                pkginfos = self.build_package_informations(item)
                if not strict or (strict and pkginfos.is_valid):
                    yield pkginfos

            if self.api_pause and i < len(chunks):
                self.logger.debug("Making pause of {} second(s)".format(self.api_pause))
                time.sleep(self.api_pause)
