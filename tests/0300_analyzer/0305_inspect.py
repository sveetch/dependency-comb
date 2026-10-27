import pytest

from dependency_comb.analyzer import DependenciesAnalyzer


@pytest.mark.parametrize("source, strict, environment, expected", [
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
        {},
        [
            ("diskette", "diskette", "analyzed"),
            ("-r dev.txt", None, "unsupported-argument"),
            ("project-composer==0.7.0", "project-composer", "analyzed"),
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
    Analyzer should return an iterator of PackageRequirement object with proper status
    from given requirements and possible strict option and possible environment.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)
    # analyzer = DependenciesAnalyzer(
    #     cachedir=cachedir,
    #     api_pause=None
    # )

    packages = analyzer.inspect(source, environment=environment, strict=strict)

    assert [(item.source, item.name, item.status) for item in packages] == expected


@pytest.mark.skip("Just for test development")
def test_build_inspection(settings):
    """
    A non test routine to rebuild 'pip_syntax/analyzed.json' fixture file content.
    """
    import json
    from dependency_comb.utils.jsons import ExtendedJsonEncoder

    cachedir = settings.fixtures_path / "api_cache"
    sample_source = settings.fixtures_path / "pip_syntax/requirements.txt"
    sample_analyzed = settings.fixtures_path / "pip_syntax/analyzed.json"

    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    packages = analyzer.inspect(sample_source)
    sample_analyzed.write_text(json.dumps(
        [item.data() for item in packages],
        indent=4,
        cls=ExtendedJsonEncoder),
    )

    print("Fixture wrote to:", sample_analyzed)

    assert 1 == 42
