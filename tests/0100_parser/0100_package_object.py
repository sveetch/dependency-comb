from packaging.requirements import Requirement, SpecifierSet

from dependency_comb.package import PackageRequirement


def test_package_without_analyze():
    """
    Without post process from analyzer, the package object only has basic informations
    from packaging parsing.
    """
    pkg = PackageRequirement("diskette>=0.1.0,<0.3.4")

    assert pkg.data() == {
        "extras": set(),
        "highest_published": None,
        "highest_version": None,
        "lateness": None,
        "marker": None,
        "name": "diskette",
        "parsed": Requirement("diskette<0.3.4,>=0.1.0"),
        "pypi_url": None,
        "repository_url": None,
        "source": "diskette>=0.1.0,<0.3.4",
        "specifier": SpecifierSet("<0.3.4,>=0.1.0"),
        "status": "parsed",
        "url": None,
        "resolved_version": None,
        "resolved_published": None
    }
