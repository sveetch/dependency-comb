import pytest

from packaging.version import Version

from dependency_comb.analyzer import DependenciesAnalyzer


def test_get_package_data_from_cache(settings):
    """
    When cache file exists with the given package name it should be used without
    performing any request.

    Here we use dummy key so any request should fails if cache system would not work
    well.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer("dummy-key", cachedir=cachedir)

    payload = analyzer.get_package_data("diskette")

    assert payload["name"] == "diskette"
    assert payload["latest_release_number"] == "0.3.5"
