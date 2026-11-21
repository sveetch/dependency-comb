from io import StringIO

import pytest
from freezegun import freeze_time

from tests.utils import complete_analyze  # noqa: F401

from dependency_comb.formatting import RichFormatter


# Skip marker decorator for tests depending on a Rich installation
rich_available = pytest.mark.skipif(
    RichFormatter is None,
    reason="Rich is not installed"
)


@rich_available
@freeze_time("2024-07-25 10:00:00")
def test_print_all(settings, complete_analyze):  # noqa: F811
    """
    With all features enabled, the output should contains all tables.
    """
    expected = settings.fixtures_path / "formatted/complete_all.rich"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RichFormatter()

    console = formatter.print(
        [v.serialize() for v in complete_analyze.packages],
        destination=StringIO(),
        with_failures=True,
        with_duplicates=True,
    )
    assert console.file.getvalue() == expected.read_text()


@rich_available
@freeze_time("2024-07-25 10:00:00")
def test_print_without_failures(settings, complete_analyze):  # noqa: F811
    """
    Without failures enabled the output should only contains the analyzed table.

    Rich formatter does not use the given printer.
    """
    expected = settings.fixtures_path / "formatted/complete_without_failures.rich"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RichFormatter()

    console = formatter.print(
        [v.serialize() for v in complete_analyze.packages],
        destination=StringIO(),
        with_failures=False,
        with_duplicates=True,
    )
    assert console.file.getvalue() == expected.read_text()


@rich_available
@freeze_time("2024-07-25 10:00:00")
def test_print_without_duplicates(settings, complete_analyze):  # noqa: F811
    """
    With failures enabled the output should contains the analyzed and failures tables.

    Rich formatter does not use the given printer.
    """
    expected = settings.fixtures_path / "formatted/complete_without_duplicates.rich"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RichFormatter()

    console = formatter.print(
        [v.serialize() for v in complete_analyze.packages],
        destination=StringIO(),
        with_failures=True,
        with_duplicates=False
    )
    assert console.file.getvalue() == expected.read_text()


@rich_available
@freeze_time("2024-07-25 10:00:00")
def test_write_all(settings, complete_analyze, tmp_path):  # noqa: F811
    """
    Rich writer method should write the console output in given destination file.
    """
    expected = settings.fixtures_path / "formatted/complete_all.rich"
    destination = tmp_path / "output.rich"

    formatter = RichFormatter()
    formatter.write(
        [v.serialize() for v in complete_analyze.packages],
        destination=destination,
        with_failures=True,
        with_duplicates=True,
    )

    assert destination.read_text() == expected.read_text()
