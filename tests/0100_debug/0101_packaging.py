import pytest

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


@pytest.mark.skip("Just R&D demonstration")
def test_packaging_splitter():
    """
    How to parse a requirement to divide package name from package version
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
def test_packaging_specifier_match():
    """
    Check 'SpecifierSet.contains()' rightness with matching versions.
    """
    releases = [
        "1.11.2", "0.1", "2.0", "1.11", "1.11-pre.1", "5.1.1", "5.0.12", "5.2.0", "1",
        "2.0.1",
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
        print("└── matching:", list(requirement.specifier.filter(
            releases, prereleases=False
        )))

    assert 1 == 42


@pytest.mark.skip("Just R&D demonstration")
def test_packaging_specifier_comparaison():
    """
    SpecifierSet can be combined with another one and then be check if it can
    be satisfied, meaning there is no conflict.
    """
    empty = SpecifierSet("")

    """
    Django
    Django
    """
    sample_1 = empty & empty
    print()
    print("🍱 both no constraint:")
    print("   - combined:", sample_1)
    print("   - conflict:", sample_1.is_unsatisfiable())

    """
    Django
    Django==5.2
    """
    exact_52 = SpecifierSet("==5.2")
    sample_2 = empty & exact_52
    print()
    print("🍱 empty and exact constraint:")
    print("   - combined:", sample_2)
    print("   - conflict:", sample_2.is_unsatisfiable())

    """
    Django<5
    Django>5.2
    """
    less_5 = SpecifierSet("<5")
    more_52 = SpecifierSet(">5.2")
    sample_3 = less_5 & more_52
    print()
    print("🍱 contradictory less than and more than:")
    print("   - combined:", sample_3)
    print("   - conflict:", sample_3.is_unsatisfiable())

    """
    Django
    Django>=5.2
    Django==6.0
    """
    more_or_better_52 = SpecifierSet(">=5.2")
    exact_6 = SpecifierSet("==6.0")
    sample_6 = empty & more_or_better_52 & exact_6
    print()
    print("🍱 no constraint and 'more or better' and exact higher:")
    print("   - combined:", sample_6)
    print("   - conflict:", sample_6.is_unsatisfiable())

    assert 1 == 42
