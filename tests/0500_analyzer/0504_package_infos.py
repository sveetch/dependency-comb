import datetime

import pytest

from freezegun import freeze_time

from packaging.requirements import Requirement, SpecifierSet
from packaging.version import Version

from dependency_comb.analyzer import DependenciesAnalyzer
from dependency_comb.models.package import PackageRequirement


@pytest.mark.parametrize("source, expected", [
    (
        "diskette>=0.1.0,<0.3.4",
        {
            "number": Version("0.3.3"),
            "published_at": datetime.datetime(2024, 3, 28, 15, 46, 54),
        }
    ),
    (
        "diskette>=2.0.0",
        None
    ),
    (
        "diskette",
        {
            "number": Version("0.3.6"),
            "published_at": datetime.datetime(2024, 9, 1, 20, 1, 50),
        }
    )
])
def test_get_latest_specified_release(settings, source, expected):
    """
    Method should return the latest release matching specifier if any else None.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    pkg = PackageRequirement(source)
    data = analyzer.get_package_data(pkg.name)
    versions = analyzer.get_package_releases(pkg.name, data)

    assert analyzer.get_latest_specified_release(pkg.specifier, versions) == expected


def test_get_package_urls(settings):
    """
    Method should not fail when there is not enough info and should returns the proper
    data when useful infos are available.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    assert analyzer.get_package_urls({}) == {"package": None, "repository": None}

    data = {"info": None}
    assert analyzer.get_package_urls(data) == {"package": None, "repository": None}

    data = {"info": {"project_urls": None}}
    assert analyzer.get_package_urls(data) == {"package": None, "repository": None}

    data = {
        "info": {
            "project_urls": {"repository": "repository", "source code": "source code"}
        }
    }
    assert analyzer.get_package_urls(data) == {
        "package": None,
        "repository": "repository"
    }

    data = {
        "info": {
            "package_url": "package_url",
            "project_urls": {"repository": "repository", "source code": "source code"}
        }
    }
    assert analyzer.get_package_urls(data) == {
        "package": "package_url",
        "repository": "repository"
    }


@freeze_time("2024-10-25 10:00:00.000000")
def test_complete_package_informations_with_requirement(settings):
    """
    Method should set computed informations on given package name and version
    requirement specifiers that lead to a proper lateness computation.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    pkg = PackageRequirement("diskette>=0.1.0,<0.3.4")
    analyzer.complete_package_informations(pkg)

    assert pkg.serialize() == {
        "source": "diskette>=0.1.0,<0.3.4",
        "origin": None,
        "lineno": 0,
        "extras": set(),
        "highest_published": datetime.datetime(2024, 9, 1, 20, 1, 50),
        "highest_version": Version("0.3.6"),
        "highest_delta": datetime.timedelta(days=53, seconds=50290),
        "lateness": [
            (
                "0.3.4",
                datetime.datetime(2024, 3, 30, 12, 38, 29),
                datetime.timedelta(days=208, seconds=76891),
            ),
            (
                "0.3.5",
                datetime.datetime(2024, 3, 31, 2, 27, 8),
                datetime.timedelta(days=208, seconds=27172),
            ),
            (
                "0.3.6",
                datetime.datetime(2024, 9, 1, 20, 1, 50),
                datetime.timedelta(days=53, seconds=50290),
            ),
        ],
        "marker": None,
        "name": "diskette",
        "parsed": Requirement("diskette<0.3.4,>=0.1.0"),
        "pypi_url": "https://pypi.org/project/diskette/",
        "repository_url": "https://github.com/emencia/diskette",
        "specifier": SpecifierSet("<0.3.4,>=0.1.0"),
        "status": "analyzed",
        "url": None,
        "resolved_version": Version("0.3.3"),
        "resolved_published": datetime.datetime(2024, 3, 28, 15, 46, 54),
        "resolved_delta": datetime.timedelta(days=210, seconds=65586),
        "parsing_error": None
    }


@freeze_time("2024-10-25 10:00:00.000000")
def test_complete_package_informations_without_requirement(settings):
    """
    Method should return computed informations for given package name without any
    requirement specifier that lead to no lateness (since without requirement the
    package elligible version is assumed to be last released one)
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    pkg = PackageRequirement("diskette")
    analyzer.complete_package_informations(pkg)

    data = pkg.serialize()
    assert data["name"] == "diskette"
    assert data["status"] == "analyzed"
    assert data["source"] == "diskette"
    assert data["specifier"] == SpecifierSet("")
    assert data["lateness"] is None
    assert data["resolved_version"] is None


@freeze_time("2024-10-25 10:00:00.000000")
def test_complete_package_informations_with_younger_requirement(settings):
    """
    If specifiers resolve to version higher than releases available on Pypi, no
    latest version can be found and lateness will be empty.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    pkg = PackageRequirement("diskette>0.4.0")
    analyzer.complete_package_informations(pkg)

    data = pkg.serialize()
    assert data["name"] == "diskette"
    assert data["status"] == "analyzed"
    assert data["highest_version"] == Version("0.3.6")
    assert data["source"] == "diskette>0.4.0"
    assert data["specifier"] == SpecifierSet(">0.4.0")
    assert data["lateness"] is None
    assert data["resolved_version"] is None


def test_complete_package_informations_status_check(settings):
    """
    Given PackageRequirement object must have a valid status to be processed. Also
    package object express validity through a property "is_valid"
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    pkg = PackageRequirement("diskette>0.4.0")
    analyzer.complete_package_informations(pkg)
    assert pkg.name == "diskette"
    assert pkg.status == "analyzed"
    assert pkg.is_valid is True

    pkg = PackageRequirement("-r dev.txt")
    analyzer.complete_package_informations(pkg)
    assert pkg.name is None
    assert pkg.status == "unsupported-argument"
    assert pkg.is_valid is False
