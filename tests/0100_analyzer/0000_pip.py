import pytest

from packaging.requirements import Requirement


@pytest.mark.skip("Just R&D demonstration")
def test_packaging_splitter():
    """
    Packaging specifier is more robust but don't support NPM style (like used in
    Poetry).

    We will need to check for SpecifierSet capacity to find the right elligible
    version(s) against a specifier and a list of released versions.

    This so, the Analyzer will need to include usage of SpecifierSet.contains() to
    find the highest released versions we got from the API.
    """
    reqs = [
        "django",
        "django>=1.11",
        "django<1.12",
        "django>=1.11,<1.12",
        "django==3.2.9",
        "django~=5.0.3",
        "django==0.32 ; python_version < \"2.7\"",
    ]

    for item in reqs:
        print()
        requirement = Requirement(item)
        print(item)
        print("├── name:", requirement.name)
        print("└── specifiers:", requirement.specifier)

    assert 1 == 42


@pytest.mark.skip("Just R&D demonstration")
def test_packaging_match():
    """
    Check SpecifierSet.contains() rightness with matching versions.
    """
    releases = [
        "1.11.2", "0.1", "2.0", "1.11", "1.11-pre.1", "5.1.1", "5.0.12", "5.2.0", "1", "2.0.1"
    ]

    print()
    print("Releases:", ", ".join(releases))

    reqs = [
        "django",
        "django>=1.11",
        "django<1.12",
        "django>=1.11,<1.12",
        "django==3.2.9",
        "django~=5.0.3",
        "django==0.32 ; python_version < \"2.7\"",
    ]

    for item in reqs:
        print()
        requirement = Requirement(item)
        print(item)
        print("├── name:", requirement.name)
        print("├── specifiers:", requirement.specifier)
        print("└── matching:", list(requirement.specifier.filter(releases, prereleases=False)))

    assert 1 == 42
