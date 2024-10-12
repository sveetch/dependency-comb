from dependency_comb.new_analyzer import DependenciesAnalyzer


def test_get_package_data_from_cache(settings):
    """
    When cache file exists with the given package name it should be used without
    performing any request.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    payload = analyzer.get_package_data("diskette")

    assert payload["info"]["name"] == "diskette"
    assert payload["info"]["version"] == "0.3.6"
