import json

import pytest

from packaging.requirements import Marker, Requirement, SpecifierSet

from dependency_comb.exceptions import RequirementParserError
from dependency_comb.parser import RequirementParser
from dependency_comb.utils.jsons import ExtendedJsonEncoder


def test_basic(settings):
    """
    Parser should be able to parse requirements with valid Pip syntax from a string
    then return requirements objects.
    """
    sample_source = settings.fixtures_path / "requirements_basic.txt"
    sample_parsed = settings.fixtures_path / "parsed_requirements_basic.json"
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


def test_markers(settings):
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

    data = {
        pkg.data()["name"]: pkg.data()
        for pkg in results
    }

    assert data["django"]["name"] == "django"
    assert data["django"]["status"] == "parsed"
    assert data["django"]["marker"] is None
    assert data["django"]["parsed"] == Requirement("django")

    assert data["foo"]["name"] == "foo"
    assert data["foo"]["status"] == "marker-reject"
    assert data["foo"]["marker"] == Marker("python_version < \"2.7\"")
    assert data["foo"]["parsed"] == Requirement("foo; python_version < \"2.7\"")

    assert data["bar"]["name"] == "bar"
    assert data["bar"]["status"] == "parsed"
    assert data["bar"]["marker"] == Marker("os_name == \"linux\"")
    assert data["bar"]["parsed"] == Requirement("bar; os_name == \"linux\"")

    assert data["nope"]["name"] == "nope"
    assert data["nope"]["status"] == "marker-reject"
    assert data["nope"]["marker"] == Marker("platform_system == \"plop\"")
    assert data["nope"]["parsed"] == Requirement("nope; platform_system == \"plop\"")


def test_includes(settings):
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

    data = {
        pkg.data()["name"]: pkg.data()
        for pkg in results
    }

    assert data["django"]["name"] == "django"
    assert data["django"]["status"] == "parsed"
    assert data["django"]["parsed"] == Requirement("django<1.12,>=1.11")
    assert data["django"]["source"] == "django>=1.11,<1.12"
    assert data["django"]["specifier"] == SpecifierSet("<1.12,>=1.11")

    assert data["diskette"]["name"] == "diskette"
    assert data["diskette"]["status"] == "parsed"
    assert data["diskette"]["parsed"] == Requirement("diskette")
    assert data["diskette"]["source"] == "diskette"
    assert data["diskette"]["specifier"] == SpecifierSet("")

    assert data["boussole"]["name"] == "boussole"
    assert data["boussole"]["status"] == "parsed"
    assert data["boussole"]["parsed"] == Requirement("boussole<=2.1.2")
    assert data["boussole"]["source"] == "boussole<=2.1.2"
    assert data["boussole"]["specifier"] == SpecifierSet("<=2.1.2")

    assert data["django-admin-shortcuts"]["name"] == "django-admin-shortcuts"
    assert data["django-admin-shortcuts"]["status"] == "parsed"
    assert data["django-admin-shortcuts"]["parsed"] == Requirement(
        "django-admin-shortcuts==1.2.6"
    )
    assert data["django-admin-shortcuts"]["source"] == "django-admin-shortcuts==1.2.6"
    assert data["django-admin-shortcuts"]["specifier"] == SpecifierSet("==1.2.6")


def test_include_notfound(settings):
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


def test_circular(settings):
    """
    Parser should detect a circular reference in included requirement files and raise
    an error.
    """
    sample_source = settings.fixtures_path / "nested_requirements/circular_parent.txt"
    parser = RequirementParser()

    with pytest.raises(RequirementParserError) as excinfo:
        parser.parse_requirements(
            sample_source,
            basepath=settings.fixtures_path / "nested_requirements",
        )

    assert str(excinfo.value) == (
        "File 'circular_leaf.txt' try to include the parent file 'circular_parent.txt' "
        "that would lead to a circular reference."
    )
