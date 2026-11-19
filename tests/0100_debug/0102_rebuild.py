"""
All functions here are fake tests just to be runned in test suite to rebuild some
data fixtures.

Once runned, this is likely to make some test to fail because assertions may have
changed. It is recommended to run this module directly instead of inside the full test
suite.

Each function have to be enabled (comment the skip line) manually. They all fail so we
can see when they are yet enabled.
"""
import pytest

from freezegun import freeze_time

from dependency_comb.analyzer import DependenciesAnalyzer
from dependency_comb.formatting import AVAILABLE_FORMATS


@pytest.mark.skip("Only to rebuild analyzer inspect")
@freeze_time("2024-07-25 10:00:00.000000")
@pytest.mark.parametrize("source, analyze", [
    ("requirements/basic.txt", "analyzes/basic.json"),
    ("requirements/basic_with_duplicates.txt", "analyzes/basic_with_duplicates.json"),
    ("requirements/failure_only.txt", "analyzes/failure_only.json"),
    (
        "requirements/minimal_success_and_failure.txt",
        "analyzes/minimal_success_and_failure.json"
    ),
    ("requirements/success_only.txt", "analyzes/success_only.json"),
])
def test_analyzer_build_inspection(settings, source, analyze):
    """
    A non test routine to rebuild JSON analyzes fixture files.
    """
    import json
    from dependency_comb.utils.jsons import ExtendedJsonEncoder

    cachedir = settings.fixtures_path / "api_cache"
    sample_source = settings.fixtures_path / source
    sample_analyzed = settings.fixtures_path / analyze

    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    packages = analyzer.inspect(sample_source, basepath=settings.fixtures_path)
    dump = json.dumps(
        [item.serialize() for item in packages],
        indent=4,
        cls=ExtendedJsonEncoder
    )

    #print(dump)

    sample_analyzed.write_text(dump)
    print("Fixture wrote to:", sample_analyzed)

    assert 1 == 42


@pytest.mark.skip("Only to rebuild formatted analyzes")
@freeze_time("2024-07-25 10:00:00.000000")
@pytest.mark.parametrize("output_format", ["json", "rst"])  #, "rich"])
def test_formatted_full(settings, output_format):
    """
    A non test routine to rebuild formatted fixture files for a format.

    TODO: Use analyzer to build payload to pass to formatter instead of deprecated
    JSON analyze dump.
    TODO: A output of table kind for duplicated will be needed
    """
    import json
    from dependency_comb.utils.jsons import ExtendedJsonEncoder

    cachedir = settings.fixtures_path / "api_cache"
    analyze = settings.fixtures_path / "analyzes/basic.json"
    # Complete formatted output
    formatted_full = (
        settings.fixtures_path / "formatted/with_failures.{}".format(output_format)
    )
    # Output of failed table only
    formatted_no_failures = (
        settings.fixtures_path / "formatted/no_failures.{}".format(output_format)
    )

    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    # Get formatter class related to format
    formatter_class = AVAILABLE_FORMATS[output_format]
    formatter = formatter_class(printer=print)

    # Write all kind of output
    formatter.write(analyze, destination=formatted_full, with_failures=True, indent=4)
    formatter.write(
        analyze, destination=formatted_no_failures, with_failures=False, indent=4
    )

    print("Fixture 'with_failures' wrote to:", formatted_full)
    print("Fixture 'no_failures' wrote to:", formatted_no_failures)

    #formatter.print(analyze, with_failures=True)

    assert 1 == 42
