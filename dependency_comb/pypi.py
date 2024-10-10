import json
import datetime
import time
from pathlib import Path

from operator import itemgetter

import requests
from packaging.version import Version, InvalidVersion

from dependency_comb.exceptions import AnalyzerError, AnalyzerAPIError
from dependency_comb.parser import RequirementParser
from dependency_comb.utils.logger import NoOperationLogger
from dependency_comb import __pkgname__, __version__


class DependenciesAnalyzer(RequirementParser):
    """
    TODO:
    Analyzer that should be able to required package info from Pypi (instead of
    libraries.io)

    Opposed to the "libraries.io" analyzer, this one will need to make 2 requests to
    get needed infos, since the package detail endpoint from new "JSON API" has
    releases informations but it is deprecated in profit of the Legacy API.

    Legacy API (also known as the "Simple API") return either a HTML or JSON response,
    depending value of request header "Accept:".

    Globally, the JSON API is a little bit more complicated to use but bring useful
    data opposed to libraries.io that have also useful data but also many useless one,
    and further more it is slow to respond and need an API key with usage limitations.

    Finally, Pypi APIs may have some limitations but there far away from libraries.io
    since it is more an human action after seeing a huge serie of requests.
    """
    PACKAGE_DETAIL_ENDPOINT = "https://pypi.org/pypi/{name}/json"
    PACKAGE_RELEASES_ENDPOINT = "https://pypi.org/simple/{name}/"

    def __init__(self, cachedir=None, api_pause=1, api_timeout=None,
                 logger=None, ignores=None):
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
            # This specific 'accept' header (application/json won't work) is only
            # required from Legacy API but JSON API ignores it
            "Accept": "application/vnd.pypi.simple.v1+json",
        }

    def endpoint_package_detail(self, name):
        """
        Request package detail API endpoint for given package name.
        """
        # This should not be done here anymore, it would be prefered on a more top
        # level where we can decide to apply pause after one or more packages
        # if self.api_pause:
        #     time.sleep(self.api_pause)

        endpoint_url = self.PACKAGE_DETAIL_ENDPOINT.format(name=name)
        print()
        print("detail request:", endpoint_url)
        response = requests.get(
            endpoint_url,
            headers=self.request_headers(),
            timeout=self.api_timeout,
        )
        print("- response:", response)
        print()

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
        """
        # This should not be done here anymore, it would be prefered on a more top
        # level where we can decide to apply pause after one or more packages
        # if self.api_pause:
        #     time.sleep(self.api_pause)

        endpoint_url = self.PACKAGE_RELEASES_ENDPOINT.format(name=name)
        print()
        print("releases request:", endpoint_url)
        response = requests.get(
            endpoint_url,
            headers=self.request_headers(),
            timeout=self.api_timeout,
        )
        print("- response:", response)
        print()

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

    def get_cache_or_request(self, name, filename, method):
        """
        Helper to search for a cache before making request if there is none.
        """
        self.logger.info("Processing package: {name}".format(
            name=name or "Unknow"
        ))

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
        response = getattr(self, method)(name)

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
        TODO: Release payload from Legacy API is not ready to use.

        There is files and versions, but versions does not include date but files have
        it, but files have no version string, only the tarball filename which seems
        to have the proper version in it.

        So we need to walk on files to parse file name, extract the version so we can
        rebuild a proper list of dictionnaries with 'number' and 'published_at' items.

        WARNING: Package like html5lib have a tarball ending with 1.0-reupload.tar.gz,
        that lead to parsing issue, we assume -reupload is part added from pypi itself
        and we ignore it for version number parsing.
        """
        for item in payload["files"]:
            # Only care about tarball (ignore wheels or else)
            if item["filename"].endswith(".tar.gz"):
                parts = item["filename"].replace("-reupload", "").split("-")[-1]
                print(item["filename"], "->\t\t", parts.replace(".tar.gz", ""))
        return {}

    def get_package_data(self, name):
        """
        Get package informations (detail and releases)

        TODO: We have to get package detail first then the package release and finally
        merge them in returned output. The release data will probably overwrite the
        currently existing but deprecated 'releases' item from detail.
        """
        self.logger.info("Processing package: {name}".format(
            name=name or "Unknow"
        ))

        if not name:
            raise AnalyzerError("Package without name can not be requested.")

        detail_payload = self.get_cache_or_request(
            name,
            "{}.detail.json".format(name),
            "endpoint_package_detail",
        )
        releases_payload = self.get_cache_or_request(
            name,
            "{}.releases.json".format(name),
            "endpoint_releases_detail",
        )

        # Path detail to inject releases
        output = detail_payload
        output["releases"] = self.format_releases_payload(releases_payload)

        return output


if __name__ == "__main__":
    cachedir = Path("./pypi_cachecli").resolve()
    analyzer = DependenciesAnalyzer(cachedir=cachedir)
    output = analyzer.get_package_data("html5lib")
    output = analyzer.get_package_data("boussole")
    output = analyzer.get_package_data("django-urls-map")
    output = analyzer.get_package_data("django")

    #print()
    #print(json.dumps(output, indent=4))
    #print()