import json

import pytest

from packaging.requirements import Requirement, SpecifierSet

from dependency_comb.exceptions import RequirementParserError
from dependency_comb.parser import RequirementParser
from dependency_comb.utils.jsons import ExtendedJsonEncoder


def test_parse_content(settings):
    """
    Parser should be able to parse requirements with valid Pip syntax from a string
    then return requirements objects.
    """
    sample_source = settings.fixtures_path / "pip_syntax/requirements.txt"
    sample_parsed = settings.fixtures_path / "pip_syntax/parsed.json"
    parser = RequirementParser()

    # As a string
    results = parser.parse_requirements(sample_source.read_text())

    # Turn data to JSON to stringify some objects and then load it as Python object to
    # make assert
    serialized = json.loads(
        json.dumps(results, indent=4, cls=ExtendedJsonEncoder)
    )
    assert serialized == json.loads(sample_parsed.read_text())

    # As a file with a Path object
    results = parser.parse_requirements(sample_source)
    # Turn data to JSON to stringify some objects and then load it as Python object to
    # make assert
    serialized = json.loads(
        json.dumps(results, indent=4, cls=ExtendedJsonEncoder)
    )
    assert serialized == json.loads(sample_parsed.read_text())


def test_parse_markers(settings):
    """
    When environment is given, it will be used to evaluate requirement markers against
    environment variables to eliminate requirement that does not match.
    """
    sample_source = (
        "django\n"
        "foo ; python_version < \"2.7\"\n"
        "bar ; os_name == \"linux\"\n"
        "nope ; platform_system == \"plop\"\n"
    )
    parser = RequirementParser()

    results = parser.parse_requirements(sample_source, environment={
        "python_version": "3.0",
        "os_name": "linux",
    })

    # Turn data to JSON to stringify some objects and then load it as Python object to
    # make assert
    serialized = json.loads(
        json.dumps(results, indent=4, cls=ExtendedJsonEncoder)
    )

    assert serialized == [
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": None,
            "name": "django",
            "parsed": "django",
            "pypi_url": None,
            "repository_url": None,
            "source": "django",
            "specifier": "",
            "status": "parsed",
            "url": None,
            "resolved_version": None,
            "resolved_published": None,
            "parsing_error": None
        },
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": "python_version < \"2.7\"",
            "name": "foo",
            "parsed": "foo; python_version < \"2.7\"",
            "pypi_url": None,
            "repository_url": None,
            "source": "foo ; python_version < \"2.7\"",
            "specifier": "",
            "status": "marker-reject",
            "url": None,
            "resolved_version": None,
            "resolved_published": None,
            "parsing_error": None
        },
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": "os_name == \"linux\"",
            "name": "bar",
            "parsed": "bar; os_name == \"linux\"",
            "pypi_url": None,
            "repository_url": None,
            "source": "bar ; os_name == \"linux\"",
            "specifier": "",
            "status": "parsed",
            "url": None,
            "resolved_version": None,
            "resolved_published": None,
            "parsing_error": None
        },
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": "platform_system == \"plop\"",
            "name": "nope",
            "parsed": "nope; platform_system == \"plop\"",
            "pypi_url": None,
            "repository_url": None,
            "source": "nope ; platform_system == \"plop\"",
            "specifier": "",
            "status": "marker-reject",
            "url": None,
            "resolved_version": None,
            "resolved_published": None,
            "parsing_error": None
        }
    ]


def test_parse_inclusion_directive(settings):
    """
    Parser should replace inclusion directive with their resolved requirement
    content if basepath is given.
    """
    sample_source = settings.fixtures_path / "nested_requirements/base.txt"
    parser = RequirementParser()

    results = parser.parse_requirements(
        sample_source.read_text(),
        basepath=settings.fixtures_path / "nested_requirements",
    )

    assert [pkg.data() for pkg in results] == [
        {
            "extras": set(),
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": None,
            "name": "django",
            "parsed": Requirement("django<1.12,>=1.11"),
            "pypi_url": None,
            "repository_url": None,
            "resolved_version": None,
            "resolved_published": None,
            "source": "django>=1.11,<1.12",
            "specifier": SpecifierSet("<1.12,>=1.11"),
            "status": "parsed",
            "url": None,
            "parsing_error": None,
        },
        {
            "extras": set(),
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": None,
            "name": "diskette",
            "parsed": Requirement("diskette"),
            "pypi_url": None,
            "repository_url": None,
            "resolved_version": None,
            "resolved_published": None,
            "source": "diskette",
            "specifier": SpecifierSet(""),
            "status": "parsed",
            "url": None,
            "parsing_error": None,
        },
        {
            "extras": set(),
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": None,
            "name": "boussole",
            "parsed": Requirement("boussole<=2.1.2"),
            "pypi_url": None,
            "repository_url": None,
            "resolved_version": None,
            "resolved_published": None,
            "source": "boussole<=2.1.2",
            "specifier": SpecifierSet("<=2.1.2"),
            "status": "parsed",
            "url": None,
            "parsing_error": None,
        },
        {
            "extras": set(),
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "marker": None,
            "name": "django-admin-shortcuts",
            "parsed": Requirement("django-admin-shortcuts==1.2.6"),
            "pypi_url": None,
            "repository_url": None,
            "resolved_version": None,
            "resolved_published": None,
            "source": "django-admin-shortcuts==1.2.6",
            "specifier": SpecifierSet("==1.2.6"),
            "status": "parsed",
            "url": None,
            "parsing_error": None,
        },
    ]


def test_parse_inclusion_directive_notfound(settings):
    """
    A RequirementParserError exception should be raised with a proper message when
    included source file is not found.
    """
    sample_source = settings.fixtures_path / "nested_requirements/base.txt"
    included_source = settings.fixtures_path / "dev.txt"
    parser = RequirementParser()

    with pytest.raises(RequirementParserError) as excinfo:
        parser.parse_requirements(
            sample_source.read_text(),
            basepath=settings.fixtures_path,
        )

    assert str(excinfo.value) == (
        "Unable to find included source: {}".format(included_source)
    )
