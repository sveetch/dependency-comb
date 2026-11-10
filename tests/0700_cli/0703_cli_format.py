from freezegun import freeze_time

import pytest

from click.testing import CliRunner

from dependency_comb.cli.entrypoint import cli_frontend
from dependency_comb.formatting import AVAILABLE_FORMATS
from dependency_comb.compat.click_support import ABORT_ENDING


def test_default(caplog):
    """
    Command should fail without requirement arguments/options.
    """
    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["format"])

    msg = (
        "Invalid value for 'SOURCE': 'requirements.txt': No such file or directory"
    )

    assert result.exit_code == 2
    assert msg in result.output
    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_with_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a
    RST format without failures included and titles.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    expected = settings.fixtures_path / "formatted/with_failures.rst"

    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["format", "-"], input=analyze.read_text())

    # if result.exit_code > 0:
    #     import traceback
    #     klass, error, error_tb = result.exc_info
    #     print(error)
    #     traceback.print_tb(error_tb, limit=None)
    #     raise error

    assert result.exit_code == 0
    assert caplog.record_tuples == []
    assert result.output == expected.read_text() + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_without_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a full
    RST format with failures included.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    expected = settings.fixtures_path / "formatted/no_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["format", "-", "--no-failures"],
        input=analyze.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []
    assert result.output == expected.read_text() + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_without_failures_to_file(caplog, tmp_path, settings):
    """
    Command should should write JSON to a file instead of standard output and logging
    some messages.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    destination = tmp_path / "format.rst"
    expected = settings.fixtures_path / "formatted/no_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["format", "-", "--no-failures", "--destination", str(destination)],
        input=analyze.read_text()
    )

    assert result.exit_code == 0

    # Written format contains have an additional newline character
    assert destination.read_text() == expected.read_text()

    assert caplog.record_tuples == [
        ("dependency-comb", 20, "Formatted analyze to: {}".format(destination)),
    ]


@pytest.mark.parametrize("format_name", AVAILABLE_FORMATS)
def test_empty(caplog, settings, format_name):
    """
    Ensure empty analyze is properly managed.
    """
    analyze = settings.fixtures_path / "analyzes/failure_only.json"

    runner = CliRunner()

    result = runner.invoke(
        cli_frontend,
        [
            "format",
            "-",
            "--no-failures",
            "--format", format_name,
        ],
        input=analyze.read_text()
    )
    # print(result.output)
    assert result.exit_code == 1
    assert result.output == (
        "There was no data to format.\nAborted{}\n".format(ABORT_ENDING)
    )
    assert caplog.record_tuples == []
