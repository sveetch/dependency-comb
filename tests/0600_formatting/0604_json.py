import json

from freezegun import freeze_time

from tests.utils import complete_analyze  # noqa: F401

from dependency_comb.formatting import JSONFormatter


@freeze_time("2024-07-25 10:00:00")
def test_print_all(settings, complete_analyze):  # noqa: F811
    """
    With all features enabled the output should contains all tables.
    """
    formatted = settings.fixtures_path / "formatted/complete_all.json"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = JSONFormatter(printer=receiver)
    formatter.print(
        [pkg.serialize() for pkg in complete_analyze.packages],
        with_failures=True,
        with_duplicates=True,
    )

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_print_without_failures(settings, complete_analyze):  # noqa: F811
    """
    With failures disabled the output should contains the analyzed and duplicates
    tables.
    """
    formatted = settings.fixtures_path / "formatted/complete_without_failures.json"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = JSONFormatter(printer=receiver)
    formatter.print(
        [pkg.serialize() for pkg in complete_analyze.packages],
        with_failures=False,
        with_duplicates=True,
    )

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_print_without_duplicates(settings, complete_analyze):  # noqa: F811
    """
    With duplicates disabled the output should contains the analyzed and failures
    tables.
    """
    formatted = settings.fixtures_path / "formatted/complete_without_duplicates.json"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = JSONFormatter(printer=receiver)
    formatter.print(
        [pkg.serialize() for pkg in complete_analyze.packages],
        with_failures=True,
        with_duplicates=False,
    )

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_write_all(settings, complete_analyze, tmp_path):  # noqa: F811
    """
    JSON writer method should write JSON data into given destination file.
    """
    formatted = settings.fixtures_path / "formatted/complete_all.json"
    destination = tmp_path / "output.json"

    formatter = JSONFormatter()
    formatter.write(
        [pkg.serialize() for pkg in complete_analyze.packages],
        destination=destination,
        with_failures=True,
        with_duplicates=True,
    )

    assert json.loads(destination.read_text()) == json.loads(formatted.read_text())
