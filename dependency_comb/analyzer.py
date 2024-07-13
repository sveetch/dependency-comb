import json
import datetime
import time

from operator import itemgetter
from pathlib import Path

import humanize
import requests
from packaging.requirements import Requirement, SpecifierSet
from packaging.version import Version

from .exceptions import AnalyzerError, AnalyzerAPIError
from .parser import RequirementParser
from . import __pkgname__, __version__


class DependenciesAnalyzer:
    """
    Analyzer is able to request libraries.io API to get informations for requirements.
    """
    PACKAGE_DETAIL_ENDPOINT = (
        "https://libraries.io/api/{plateform}/{name}?api_key={key}"
    )

    def __init__(self, api_key, cachedir=None, api_pause=None, logger=None):
        self.api_key = api_key
        self.cachedir = cachedir
        self.logger = logger
        self.now_date = datetime.datetime.now()
        # Time in seconds to pause before an API request (to embrace limit of 60
        # requests max per minute)
        self.api_pause = api_pause or 1

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
        time.sleep(self.api_pause)
        endpoint_url = self.PACKAGE_DETAIL_ENDPOINT.format(
            plateform="Pypi",
            name=name,
            key=self.api_key,
        )
        response = requests.get(endpoint_url, headers=self.request_headers())

        if response.status_code == 403:
            raise AnalyzerAPIError(
                "API responded a 403 error, your API key is probably invalid.",
                http_status=403
            )
        if response.status_code == 404:
            raise AnalyzerAPIError(
                "API responded a 404 error, package name is probably invalid.",
                http_status=404
            )
        elif response.status_code == 429:
            raise AnalyzerAPIError(
                "Analyzer exceeded API limit of 60 request per minute.",
                http_status=429
            )

        response.raise_for_status()

        return response

    def get_package_data(self, name):
        """
        Get package detail either from API or from cache if any.
        """
        print("🐛 Package:", name)

        if not name:
            raise AnalyzerError("Package without name can not be requested.")

        # Build expected cache file name if cache is enabled
        cache_file = None
        if self.cachedir:
            cache_file = self.cachedir / "{}.json".format(name)

        # Use cache if exists without any condition
        if cache_file and cache_file.exists():
            print("  - Loading data from cache")
            output = json.loads(cache_file.read_text())
        else:
            # Get payload from API
            response = self.endpoint_package_info(name)

            print("  [{}]".format(response.status_code), "GET", response.url)
            output = response.json()

            # Build cache if cache is enabled
            if self.cachedir:
                print("  - Writing cache:", str(cache_file))
                cache_file.write_text(json.dumps(output, indent=4))

        return output

    def build_package_versions(self, data):
        """
        Build version list from API patched with some values in useful types.

        Arguments:
            data (dict):

        Returns:
            list:
        """
        # Rebuild the version list to patch some values in useful types
        versions = []
        for item in data["versions"]:
            # Enforce real datetime
            item["published_at"] = datetime.datetime.fromisoformat(
                item["published_at"].split(".")[0]
            )
            # Coerce original number to a Version object
            item["number"] = Version(item["number"])

            versions.append

        return sorted(data["versions"], key=itemgetter("number"))

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

    def get_latest_version(self, specifiers, versions):
        """
        Get the latest version number from given version list that match given
        specifier.

        Arguments:
            specifiers (packaging.SpecifierSet):
            versions (list): List of dict for versions as built from
                ``DependenciesAnalyzer.build_package_versions()``.

        Returns:
            string: Version number if there is latest version. In some case there can
            be no found latest version when specifiers resolve to versions higher than
            the released ones (commonly if specifiers are invalid or using releases
            not published on Pypi).
        """
        releases = sorted(specifiers.filter(
            [str(item["number"]) for item in versions],
            prereleases=False
        ))

        if not releases:
            return None

        return releases[-1]

    def build_package_informations(self, requirement):
        """
        Compute and set informations onto a ``PackageRequirement`` object.

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

            # Once numbers have been coerced they can be used to reorder versions properly
            # on number
            versions = self.build_package_versions(data)

            if requirement.specifier:
                # Match the highest elligible version from specifiers against built
                # versions
                requirement.resolved_version = self.get_latest_version(
                    requirement.specifier,
                    versions
                )

            # Highest released version
            requirement.highest_published = versions[-1]["published_at"]
            # Delta time from that highest released version
            requirement.latest_activity = humanize.naturaldelta(
                self.now_date - requirement.highest_published
            )

            # Compute version lateness if a version has been given
            if requirement.resolved_version:
                requirement.lateness = self.compute_lateness(
                    requirement.resolved_version,
                    versions
                )

        return requirement

    def inspect(self, requirements, environment=None, strict=False):
        """
        Inspect given requirement to get their informations.

        Arguments:
            requirements (string or Path): Either a Path object for a file to open or
                directly requirements content as a string.

        Keyword Arguments:
            environment (dict):
            strict (boolean): If True only the valid requirements (see
                ``dependency_comb.package.PackageRequirement.is_valid``) are returned.
                Default is False, all requirements are returned and you need to check
                their status yourself if needed.

        Returns:
            iterator: Iterator of PackageRequirement objects for given requirements.
        """
        parser = RequirementParser()

        for item in parser.parse_requirements(requirements, environment=environment):
            pkginfos =  self.build_package_informations(item)
            if not strict or (strict and pkginfos.is_valid):
                yield pkginfos
