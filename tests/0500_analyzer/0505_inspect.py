import datetime

import pytest

from freezegun import freeze_time

from dependency_comb.analyzer import DependenciesAnalyzer


@pytest.mark.parametrize("source, strict, environment, expected", [
    (
        (
            "diskette\n"
            "-r dev.txt\n"
            "project-composer\n"
            "# Niet\n"
            "project-composer==0.7.0\n"
            "django>3.1,<=3.2\n"
            "foo>1,foo<=2\n"
            "boussole ; python_version < \"2.7\"\n"
        ),
        False,
        {},
        [
            ("diskette", "diskette", "analyzed"),
            ("-r dev.txt", None, "unsupported-argument"),
            ("project-composer", "project-composer", "analyzed"),
            ("project-composer==0.7.0", "project-composer", "duplicate"),
            ("django>3.1,<=3.2", "django", "analyzed"),
            ("foo>1,foo<=2", None, "invalid"),
            ("boussole ; python_version < \"2.7\"", "boussole", "analyzed"),
        ],
    ),
    (
        (
            "diskette\n"
            "-r dev.txt\n"
            "# Niet\n"
            "project-composer==0.7.0\n"
            "django>3.1,<=3.2\n"
            "foo>1,foo<=2\n"
            "boussole ; python_version < \"2.7\"\n"
        ),
        True,
        {},
        [
            ("diskette", "diskette", "analyzed"),
            ("project-composer==0.7.0", "project-composer", "analyzed"),
            ("django>3.1,<=3.2", "django", "analyzed"),
            ("boussole ; python_version < \"2.7\"", "boussole", "analyzed"),
        ],
    ),
    (
        (
            "diskette\n"
            "-r dev.txt\n"
            "# Niet\n"
            "project-composer==0.7.0\n"
            "django>3.1,<=3.2\n"
            "foo>1,foo<=2\n"
            "boussole ; python_version < \"2.7\"\n"
        ),
        False,
        {"python_version": "3.4"},
        [
            ("diskette", "diskette", "analyzed"),
            ("-r dev.txt", None, "unsupported-argument"),
            ("project-composer==0.7.0", "project-composer", "analyzed"),
            ("django>3.1,<=3.2", "django", "analyzed"),
            ("foo>1,foo<=2", None, "invalid"),
            ("boussole ; python_version < \"2.7\"", "boussole", "marker-reject"),
        ],
    ),
    (
        (
            "diskette\n"
            "-r dev.txt\n"
            "# Niet\n"
            "project-composer==0.7.0\n"
            "django>3.1,<=3.2\n"
            "foo>1,foo<=2\n"
            "boussole ; python_version < \"2.7\"\n"
        ),
        True,
        {"python_version": "3.4"},
        [
            ("diskette", "diskette", "analyzed"),
            ("project-composer==0.7.0", "project-composer", "analyzed"),
            ("django>3.1,<=3.2", "django", "analyzed"),
        ],
    ),
])
def test_inspect(settings, source, strict, environment, expected):
    """
    Analyzer should return an iterator of PackageRequirement objects with proper status
    from given requirements and possible strict option and possible environment.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    packages = analyzer.inspect(source, environment=environment, strict=strict)

    assert [(item.source, item.name, item.status) for item in packages] == expected


@freeze_time("2024-07-25 10:00:00.000000")
def test_statistics(settings):
    """
    Once all packages have been enumerated from inspect, statistics should have been
    correctly computed.
    """
    source = (
        "diskette\n"
        "-r dev.txt\n"
        "project-composer\n"
        "project-composer==0.7.0\n"
        "django>3.1,<=3.2\n"
        "foo>1,foo<=2\n"
        "boussole ; python_version < \"2.7\"\n"
    )

    analyzer = DependenciesAnalyzer(cachedir=(settings.fixtures_path / "api_cache"))

    # With environment, some marker may be rejected and so some package maybe assumed
    # invalid
    list(analyzer.inspect(source, environment={"python_version": "3.4"}))
    assert analyzer.statistics == {
        "creation_date": datetime.datetime(2024, 7, 25, 10),
        "packages": {
            "analyzed": 3,
            "duplicate": 1,
            "invalid": 3,
            "lates": 2,
            "total": 7,
        },
        "project": {
            "status": "late",
            "python_version": "3.4",
        }
    }

    # Without environment, marker are ignored and all valid packages are counted
    list(analyzer.inspect(source))
    assert analyzer.statistics == {
        "creation_date": datetime.datetime(2024, 7, 25, 10),
        "packages": {
            "analyzed": 4,
            "duplicate": 1,
            "invalid": 2,
            "lates": 2,
            "total": 7,
        },
        "project": {
            "status": "late",
            "python_version": None,
        }
    }
