import pytest

from freezegun import freeze_time

from dependency_comb.analyzer import DependenciesAnalyzer


@pytest.mark.skip("Only to rebuild analyzer inspect")
@freeze_time("2024-07-25 10:00:00.000000")
def test_build_inspection(settings):
    """
    A non test routine to rebuild 'analyzes/basic.json' fixture file content.

    .. Warning::
        Rebuilding this data will involve test failures.
    """
    import json
    from dependency_comb.utils.jsons import ExtendedJsonEncoder

    cachedir = settings.fixtures_path / "api_cache"
    sample_source = settings.fixtures_path / "requirements_basic.txt"
    sample_analyzed = settings.fixtures_path / "analyzes/basic.json"

    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    packages = analyzer.inspect(sample_source)
    sample_analyzed.write_text(json.dumps(
        [item.data() for item in packages],
        indent=4,
        cls=ExtendedJsonEncoder),
    )

    print("Fixture wrote to:", sample_analyzed)

    assert 1 == 42
