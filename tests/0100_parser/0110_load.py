import json

import pytest

from packaging.requirements import Requirement

from dependency_comb.parser import RequirementParser
from dependency_comb.utils.jsons import ExtendedJsonEncoder


def test_parse_content(settings):
    """
    Parser should be able to parse requirements from a string then return requirements
    objects.
    """
    sample_source = settings.fixtures_path / "pip_requirements.txt"
    sample_parsed = settings.fixtures_path / "parsed_pip_requirements.json"
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
    sample_parsed = settings.fixtures_path / "parsed_pip_requirements.json"
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
            "latest_activity": None,
            "marker": None,
            "name": "django",
            "parsed": "django",
            "pypi_url": None,
            "repository_url": None,
            "source": "django",
            "specifier": "",
            "status": "parsed",
            "url": None,
            "resolved_version": None
        },
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "latest_activity": None,
            "marker": "python_version < \"2.7\"",
            "name": "foo",
            "parsed": "foo; python_version < \"2.7\"",
            "pypi_url": None,
            "repository_url": None,
            "source": "foo ; python_version < \"2.7\"",
            "specifier": "",
            "status": "marker-reject",
            "url": None,
            "resolved_version": None
        },
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "latest_activity": None,
            "marker": "os_name == \"linux\"",
            "name": "bar",
            "parsed": "bar; os_name == \"linux\"",
            "pypi_url": None,
            "repository_url": None,
            "source": "bar ; os_name == \"linux\"",
            "specifier": "",
            "status": "parsed",
            "url": None,
            "resolved_version": None
        },
        {
            "extras": [],
            "highest_published": None,
            "highest_version": None,
            "lateness": None,
            "latest_activity": None,
            "marker": "platform_system == \"plop\"",
            "name": "nope",
            "parsed": "nope; platform_system == \"plop\"",
            "pypi_url": None,
            "repository_url": None,
            "source": "nope ; platform_system == \"plop\"",
            "specifier": "",
            "status": "marker-reject",
            "url": None,
            "resolved_version": None
        }
    ]
