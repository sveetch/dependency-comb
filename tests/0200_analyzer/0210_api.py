import pytest

from dependency_comb.analyzer import DependenciesAnalyzer
from dependency_comb.exceptions import AnalyzerAPIError

from tests.utils import skip_api_condition


# Skip marker decorator for tests depending on a API key usage
api_allowed = pytest.mark.skipif(skip_api_condition, reason="API request is disabled")


@api_allowed
def test_get_package_data_invalid_name():
    """
    Request to API with a non existing package name should lead to an error from
    API
    """
    analyzer = DependenciesAnalyzer(api_pause=None)

    with pytest.raises(AnalyzerAPIError) as excinfo:
        analyzer.get_package_data("combabcdenope")

    assert str(excinfo.value) == (
        "API responded a 404 error, package name 'combabcdenope' is probably invalid "
        "or not available on Pypi."
    )
    assert excinfo.value.http_status == 404


@api_allowed
def test_get_package_data_from_api():
    """
    Request to API for given package name should return proper JSON payload.
    """
    analyzer = DependenciesAnalyzer(api_pause=None)

    # Currently the analyzer does not check for response status. It should do it
    # instead of coercing any response to json that lead to missunderstood issue
    payload = analyzer.get_package_data("project-composer")

    assert payload["info"]["name"] == "project-composer"
    assert payload["info"]["home_page"] == "https://github.com/sveetch/project-composer"
