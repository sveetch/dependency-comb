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

from tests.utils import complete_analyze, minimal_analyze  # noqa: F401

from dependency_comb.formatting import AVAILABLE_FORMATS


@pytest.mark.skip("Only to rebuild formatted analyzes")
@freeze_time("2024-07-25 10:00:00.000000")
@pytest.mark.parametrize("output_format", ["json", "rst", "rich"])
def test_formatted_complete(settings, complete_analyze, output_format):  # noqa: F811
    """
    A non test routine to rebuild formatted fixture files for a format with 'complete'
    requirements.

    This routine is dependent from formatters so they are required to be working well,
    broken formatter would fail or build broken dump.
    """
    formatted_full = (
        "formatted/complete_all.{}".format(output_format)
    )
    formatted_without_failures = (
        "formatted/complete_without_failures.{}".format(output_format)
    )
    formatted_without_duplicates = (
        "formatted/complete_without_duplicates.{}".format(output_format)
    )

    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    # Get formatter class related to format
    formatter_class = AVAILABLE_FORMATS[output_format]
    formatter = formatter_class(printer=print)

    packages = [
        v.serialize()
        for v in complete_analyze.packages
    ]

    # Write all kind of output
    formatter.write(
        packages,
        destination=settings.fixtures_path / formatted_full,
        with_failures=True,
        with_duplicates=True,
        indent=4,
    )
    print(
        "Fixture 'complete_all' wrote to:",
        settings.fixtures_path / formatted_full
    )

    formatter.write(
        packages,
        destination=settings.fixtures_path / formatted_without_failures,
        with_failures=False,
        with_duplicates=True,
        indent=4,
    )
    print(
        "Fixture 'complete_without_failures' wrote to:",
        settings.fixtures_path / formatted_without_failures
    )

    formatter.write(
        packages,
        destination=settings.fixtures_path / formatted_without_duplicates,
        with_failures=True,
        with_duplicates=False,
        indent=4,
    )
    print(
        "Fixture 'complete_without_duplicates' wrote to:",
        settings.fixtures_path / formatted_without_duplicates
    )

    """
    print()
    formatter.print(
        packages,
        with_failures=True,
        with_duplicates=False,
    )
    print()
    formatter.print(
        packages,
        with_failures=False,
        with_duplicates=True,
    )
    print()
    formatter.print(
        packages,
        with_failures=True,
        with_duplicates=False,
    )
    print()
    """

    assert 1 == 42
