import logging

from dependency_comb import __pkgname__
from dependency_comb.utils.logger import LoggerBase
from dependency_comb.analyzer import DependenciesAnalyzer


def test_get_cache_or_request_cached(caplog, settings):
    """
    Ensure cache is used when related file exists.
    """
    caplog.set_level(logging.DEBUG)

    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir, logger=LoggerBase().log)

    # Dummy function that won't be called
    def fake(name):
        return "Nope"

    payload = analyzer.get_cache_or_request(
        "diskette",
        "diskette.detail.json",
        fake,
        "payload"
    )

    assert payload["info"]["name"] == "diskette"
    # We can safely assert on version since it should have been frozen in cache and
    # should not change
    assert payload["info"]["version"] == "0.3.6"

    assert caplog.record_tuples == [
        (__pkgname__, 10, "Get package payload for 'diskette'"),
        (__pkgname__, 10, "Loading data from cache"),
    ]


def test_get_cache_or_request_requested(caplog, settings, tmp_path):
    """
    Ensure request method is executed when there is no related cache file.
    """
    caplog.set_level(logging.DEBUG)

    analyzer = DependenciesAnalyzer(cachedir=tmp_path, logger=LoggerBase().log)

    # Fake response object to simulate requests.Response and avoid a real request
    class FakeResponse:
        url = "http://dummy"
        status_code = 200

        def json(self, *args, **kwargs):
            return "Ping API"

    # Dummy function that should be called and return a Dummy response
    def fake(name):
        return FakeResponse()

    payload = analyzer.get_cache_or_request(
        "dummycomb",
        "dummycomb.detail.json",
        fake,
        "payload"
    )

    assert payload == "Ping API"

    assert caplog.record_tuples == [
        (__pkgname__, 10, "Get package payload for 'dummycomb'"),
        (__pkgname__, 10, "[200] API response from http://dummy"),
        (__pkgname__, 10, "Writing cache: {}/dummycomb.detail.json".format(tmp_path)),
    ]


def test_get_package_data_from_cache(caplog, settings):
    """
    When cache file exists with the given package name it should be used without
    performing any request.
    """
    caplog.set_level(logging.DEBUG)

    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir, logger=LoggerBase().log)

    payload = analyzer.get_package_data("diskette")

    assert payload["info"]["name"] == "diskette"
    # We can safely assert on version since it should have been frozen in cache and
    # should not change
    assert payload["info"]["version"] == "0.3.6"

    assert caplog.record_tuples == [
        (__pkgname__, 20, "Processing package: diskette"),
        (__pkgname__, 10, "Get package detail for 'diskette'"),
        (__pkgname__, 10, "Loading data from cache"),
        (__pkgname__, 10, "Get package releases for 'diskette'"),
        (__pkgname__, 10, "Loading data from cache"),
    ]
