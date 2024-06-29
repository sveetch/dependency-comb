import json
import datetime

import pytest

from packaging.version import Version
from requests.exceptions import HTTPError

from dependency_comb.analyzer import DependenciesAnalyzer
from dependency_comb.exceptions import AnalyzerAPIError

from tests.utils import API_FILEKEY_FILENAME, get_api_key


# Skip marker decorator for tests depending on a API key usage
api_allowed = pytest.mark.skipif(
    get_api_key() is None,
    reason="No API key found from file '{}'".format(API_FILEKEY_FILENAME)
)


@api_allowed
def test_get_package_data_invalid_key(settings):
    """
    When given api key is invalid, the API respond with a Http 403 response
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer("dummy-key", api_pause=None)

    # Currently the analyzer does not check for response status. It should do it
    # instead of coercing any response to json that lead to missunderstood issue
    with pytest.raises(AnalyzerAPIError) as excinfo:
        analyzer.get_package_data("project-composer")

    assert str(excinfo.value) == (
        "API responded a 403 error, your API key is probably invalid."
    )
    assert excinfo.value.http_status == 403


@api_allowed
def test_get_package_data_invalid_name(settings):
    """
    Request to API with a non existing package name should lead to an error from
    API
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(settings.api_key(), api_pause=None)

    with pytest.raises(AnalyzerAPIError) as excinfo:
        analyzer.get_package_data("combabcdenope")

    assert str(excinfo.value) == (
        "API responded a 404 error, package name is probably invalid."
    )
    assert excinfo.value.http_status == 404


@api_allowed
def test_get_package_data_from_api(settings):
    """
    Request to API for given package name should return proper JSON payload.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(settings.api_key(), api_pause=None)

    # Currently the analyzer does not check for response status. It should do it
    # instead of coercing any response to json that lead to missunderstood issue
    payload = analyzer.get_package_data("project-composer")

    assert payload["name"] == "project-composer"
    assert payload["homepage"] == "https://github.com/sveetch/project-composer"
