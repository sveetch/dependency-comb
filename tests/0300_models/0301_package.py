import json

import pytest

from packaging.requirements import Requirement, SpecifierSet

from dependency_comb.models.package import PackageRequirement


def test_basic():
    """
    Before post processing from analyzer, the package object has only basic informations
    from parser 'packaging.requirements.Requirement'.
    """
    pkg = PackageRequirement("diskette>=0.1.0,<0.3.4")

    assert pkg.serialize() == {
        "source": "diskette>=0.1.0,<0.3.4",
        "origin": None,
        "lineno": 0,
        "extras": set(),
        "highest_published": None,
        "highest_version": None,
        "highest_delta": None,
        "lateness": None,
        "marker": None,
        "name": "diskette",
        "parsed": Requirement("diskette<0.3.4,>=0.1.0"),
        "pypi_url": None,
        "repository_url": None,
        "specifier": SpecifierSet("<0.3.4,>=0.1.0"),
        "status": "parsed",
        "url": None,
        "resolved_version": None,
        "resolved_published": None,
        "resolved_delta": None,
        "parsing_error": None
    }


def test_as_json():
    """
    Model object can be serialized to JSON
    """
    pkg = PackageRequirement("diskette>=0.1.0,<0.3.4")

    assert json.loads(pkg.as_json()) == {
        "source": "diskette>=0.1.0,<0.3.4",
        "origin": None,
        "lineno": 0,
        "extras": [],
        "highest_published": None,
        "highest_version": None,
        "highest_delta": None,
        "lateness": None,
        "marker": None,
        "name": "diskette",
        "parsed": "diskette<0.3.4,>=0.1.0",
        "pypi_url": None,
        "repository_url": None,
        "specifier": "<0.3.4,>=0.1.0",
        "status": "parsed",
        "url": None,
        "resolved_version": None,
        "resolved_published": None,
        "resolved_delta": None,
        "parsing_error": None
    }


@pytest.mark.parametrize("source, parsed_name, parsed_url", [
    ("djangorestframework", "djangorestframework", None),
    ("django>=1.11,<1.12", "django", None),
    ("django-lotus==2.0.0 # a comment", "django-lotus", None),
    (
        "requests [security] >= 2.8.1, == 2.8.* ; python_version < \"2.7\"",
        "requests",
        None
    ),
    (
        "MyProject[extra] @ git+https:/git.example.com/MyProject",
        "MyProject",
        "git+https:/git.example.com/MyProject"
    ),
    (
        "urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip",
        "urllib3",
        "https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip"
    ),
    (
        "pkg @ vcs+protocol://repo_url/#subdirectory=pkg_dir",
        "pkg",
        "vcs+protocol://repo_url/#subdirectory=pkg_dir"
    ),
    (
        "paquet @ vcs+protocol://repo_url/#subdirectory=paquet_dir # comment",
        "paquet",
        "vcs+protocol://repo_url/#subdirectory=paquet_dir"
    ),
])
def test_parser_valid(source, parsed_name, parsed_url):
    """
    All expected valid requirement line formats should be successfuly parsed.
    """
    pkg = PackageRequirement(source)
    assert pkg.status == "parsed"
    assert pkg.name == parsed_name
    assert pkg.url == parsed_url
    assert pkg.is_valid is True


@pytest.mark.parametrize("source, parsed_name", [
    ("./downloads/numpy-1.9.2-cp34-none-win32.whl", "unsupported-localpath"),
    (
        (
            "http://wxpython.org/Phoenix/snapshot-builds/wxPython_Phoenix-3.0.3."
            "dev1820+49a8884-cp34-none-win_amd64.whl"
        ),
        "unsupported-url"
    ),
    ("-z foobar", "unsupported-argument"),
])
def test_parser_invalid(source, parsed_name):
    """
    All expected invalid requirement line formats should return invalid package object.
    """
    pkg = PackageRequirement(source)
    assert pkg.status == parsed_name
    assert pkg.name is None
    assert pkg.is_valid is False
