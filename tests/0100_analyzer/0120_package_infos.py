import datetime
import json

import pytest

from packaging.requirements import Requirement, SpecifierSet
from packaging.version import Version
from packaging.markers import Marker

from dependency_comb.analyzer import DependenciesAnalyzer
from dependency_comb.package import PackageRequirement
from dependency_comb.utils.jsons import ExtendedJsonEncoder


def test_build_package_informations_with_requirement(settings):
    """
    Method should return computed informations for given package name and version
    requirement specifiers that lead to a proper lateness computation.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer("dummy-key", cachedir=cachedir)

    pkg = PackageRequirement("diskette>=0.1.0,<0.3.4")
    analyzer.build_package_informations(pkg)

    # print(json.dumps(pkg.data(), indent=4, cls=ExtendedJsonEncoder))

    assert pkg.data() == {
        "extras": set(),
        "highest_published": datetime.datetime(2024, 3, 31, 2, 27, 8),
        "highest_version": Version("0.3.5"),
        "lateness": [
            (
                "0.3.4",
                datetime.datetime(2024, 3, 30, 12, 38, 29),
            ),
            (
                "0.3.5",
                datetime.datetime(2024, 3, 31, 2, 27, 8),
            ),
        ],
        "latest_activity": "2 months",
        "marker": None,
        "name": "diskette",
        "parsed": Requirement("diskette<0.3.4,>=0.1.0"),
        "pypi_url": "https://pypi.org/project/diskette/",
        "repository_url": "https://github.com/emencia/diskette",
        "source": "diskette>=0.1.0,<0.3.4",
        "specifier": SpecifierSet("<0.3.4,>=0.1.0"),
        "status": "analyzed",
        "url": None,
        "resolved_version": "0.3.3"
    }


def test_build_package_informations_without_requirement(settings):
    """
    Method should return computed informations for given package name without any
    requirement specifier that lead to no lateness (since without requirement the
    package elligible version is assumed to be last released one)
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer("dummy-key", cachedir=cachedir)

    pkg = PackageRequirement("diskette")
    analyzer.build_package_informations(pkg)

    assert pkg.data() == {
        "extras": set(),
        "highest_published": datetime.datetime(2024, 3, 31, 2, 27, 8),
        "highest_version": Version("0.3.5"),
        "lateness": None,
        "latest_activity": "2 months",
        "marker": None,
        "name": "diskette",
        "parsed": Requirement("diskette"),
        "pypi_url": "https://pypi.org/project/diskette/",
        "repository_url": "https://github.com/emencia/diskette",
        "source": "diskette",
        "specifier": SpecifierSet(""),
        "status": "analyzed",
        "url": None,
        "resolved_version": None,
    }


def test_build_package_informations_with_exceed_requirement(settings):
    """
    If specifiers resolve to version higher than releases available on Pypi, no
    latest version can be found and lateness will be empty.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer("dummy-key", cachedir=cachedir)

    pkg = PackageRequirement("diskette>0.4.0")
    analyzer.build_package_informations(pkg)

    assert pkg.data() == {
        "extras": set(),
        "highest_published": datetime.datetime(2024, 3, 31, 2, 27, 8),
        "highest_version": Version("0.3.5"),
        "lateness": None,
        "latest_activity": "2 months",
        "marker": None,
        "name": "diskette",
        "parsed": Requirement("diskette>0.4.0"),
        "pypi_url": "https://pypi.org/project/diskette/",
        "repository_url": "https://github.com/emencia/diskette",
        "source": "diskette>0.4.0",
        "specifier": SpecifierSet(">0.4.0"),
        "status": "analyzed",
        "url": None,
        "resolved_version": None,
    }


def test_build_package_informations_status_check(settings):
    """
    Given PackageRequirement object must have a "valid" status to be processed else
    analyzer would try to request invalid packages (like unsupported stuff without a
    package name). Also package object express validity through a property "is_valid"
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer("dummy-key", cachedir=cachedir)

    pkg = PackageRequirement("diskette>0.4.0")
    result = analyzer.build_package_informations(pkg)
    assert pkg.name == "diskette"
    assert pkg.status == "analyzed"
    assert pkg.is_valid is True

    pkg = PackageRequirement("-r dev.txt")
    result = analyzer.build_package_informations(pkg)
    assert pkg.name == None
    assert pkg.status == "unsupported-argument"
    assert pkg.is_valid is False
