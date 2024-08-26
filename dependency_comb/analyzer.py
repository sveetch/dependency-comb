import json
import datetime
import time

from operator import itemgetter

import requests
from packaging.version import Version, InvalidVersion

from .exceptions import AnalyzerError, AnalyzerAPIError
from .parser import RequirementParser
from .utils.logger import NoOperationLogger
from . import __pkgname__, __version__


class DependenciesAnalyzer(RequirementParser):
    """
    Analyzer is able to request libraries.io API to get informations for requirements.
    """
    PACKAGE_DETAIL_ENDPOINT = (
        "https://libraries.io/api/{plateform}/{name}?api_key={key}"
    )

    def __init__(self, api_key, cachedir=None, api_pause=1, api_timeout=None,
                 logger=None, ignores=None):
        self.api_key = api_key
        self.cachedir = cachedir
        self.logger = logger or NoOperationLogger()
        # Time in seconds to pause before an API request (to embrace limit of 60
        # requests max per minute)
        self.api_pause = api_pause
        # Time in seconds for timeout limit on API request
        self.api_timeout = api_timeout
        # TODO: Currently not implemented, it should be a list of package names to
        # ignore from analyze, dont know the state it will end in. It will be helpful
        # to bypass some erroneous requirements without break the whole analyze.
        self.ignores = ignores or []

    def request_headers(self):
        """
        Define the custom headers to use in requests to the API.
        """
        return {
            "user-agent": "{name}/{version}".format(
                name=__pkgname__,
                version=__version__,
            ),
        }

    def endpoint_package_info(self, name):
        """
        Request package detail API endpoint for given package name.
        """
        if self.api_pause:
            time.sleep(self.api_pause)

        endpoint_url = self.PACKAGE_DETAIL_ENDPOINT.format(
            plateform="Pypi",
            name=name,
            key=self.api_key,
        )
        response = requests.get(
            endpoint_url,
            headers=self.request_headers(),
            timeout=self.api_timeout,
        )

        # Manage custom error message for some well known errors
        if response.status_code == 403:
            raise AnalyzerAPIError(
                "API responded a 403 error, your API key is probably invalid.",
                http_status=403
            )
        elif response.status_code == 404:
            raise AnalyzerAPIError(
                (
                    "API responded a 404 error, package name '{}' is probably "
                    "invalid or not available on Pypi."
                ).format(name),
                http_status=404
            )
        elif response.status_code == 429:
            raise AnalyzerAPIError(
                "Analyzer exceeded API limit of 60 request per minute.",
                http_status=429
            )

        # In case we an error status that is not taken in charge before
        response.raise_for_status()

        return response

    def get_package_data(self, name):
        """
        Get package detail either from API or from cache if any.
        """
        self.logger.info("Processing package: {name}".format(
            name=name or "Unknow"
        ))

        if not name:
            raise AnalyzerError("Package without name can not be requested.")

        # Build expected cache file name if cache is enabled
        cache_file = None
        if self.cachedir:
            cache_file = self.cachedir / "{}.json".format(name)

        # Use cache if exists without any condition
        if cache_file and cache_file.exists():
            self.logger.debug("Loading data from cache")
            output = json.loads(cache_file.read_text())
        else:
            # Get payload from API
            response = self.endpoint_package_info(name)

            # Debug API url without API key
            self.logger.debug("[{status}] API response from {url}".format(
                status=response.status_code,
                url=response.url.split("?")[0],
            ))
            output = response.json()

            # Build cache if cache is enabled
            if self.cachedir:
                self.logger.debug("Writing cache: {}".format(cache_file))
                cache_file.write_text(json.dumps(output, indent=4))

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
            item["published_at"] = datetime.datetime.fromisoformat(
                item["published_at"].split(".")[0]
            )
            # Coerce original number to a Version object
            try:
                number = Version(item["number"])
            except InvalidVersion:
                msg = (
                    "Ignored package '{name}' invalid release version number "
                    "'{version}'"
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
            requirement.status = "analyzed"

            requirement.pypi_url = data["package_manager_url"]
            requirement.repository_url = data["repository_url"]
            requirement.highest_version = Version(data["latest_release_number"])

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

        for item in parsed_requirements:
            pkginfos = self.build_package_informations(item)
            if not strict or (strict and pkginfos.is_valid):
                yield pkginfos
