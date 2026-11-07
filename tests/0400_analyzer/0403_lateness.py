import datetime

from freezegun import freeze_time

from packaging.version import Version

from dependency_comb.analyzer import DependenciesAnalyzer


@freeze_time("2024-10-25 10:00:00.000000")
def test_compute_lateness(settings):
    """
    Computed lateness should return a list of release versions with a higher version
    number than the target one.

    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    versions = [
        {"number": Version("1.0.0"), "published_at": datetime.datetime(2020, 3, 11)},
        {"number": Version("0.3.3"), "published_at": datetime.datetime(2020, 4, 11)},
        {"number": Version("0.0.1"), "published_at": datetime.datetime(2020, 1, 11)},
        {"number": Version("0.3.5"), "published_at": datetime.datetime(2020, 2, 11)},
        {"number": Version("0.3.4"), "published_at": datetime.datetime(2020, 2, 11)},
    ]

    informations = analyzer.compute_lateness(target="0.3.4", versions=versions)

    assert informations == [
        (
            "1.0.0",
            datetime.datetime(2020, 3, 11, 0, 0),
            datetime.timedelta(days=1689, seconds=36000),

        ),
        (
            "0.3.5",
            datetime.datetime(2020, 2, 11, 0, 0),
            datetime.timedelta(days=1718, seconds=36000),
        ),
    ]
