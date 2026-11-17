import pytest
from freezegun import freeze_time

from click.testing import CliRunner

from dependency_comb import __pkgname__
from dependency_comb.cli.entrypoint import cli_frontend
from dependency_comb.formatting import AVAILABLE_FORMATS
from dependency_comb.compat.click_support import ABORT_ENDING


def test_report_default(caplog):
    """
    Command should fail without requirement arguments/options.
    """
    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["report"])

    msg = (
        "Invalid value for 'SOURCE': 'requirements.txt': No such file or "
        "directory"
    )

    assert result.exit_code == 2
    assert msg in result.output
    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_report_with_failures_from_stdin(caplog, settings):
    """
    Command should succeed to analyze from standard input and return a full
    JSON format with failures included.

    NOTE: We use JSON format because it is easier to patch origin with stdin (no
    origin) and expected dump (include an origin).
    """
    cachedir = settings.fixtures_path / "api_cache"
    requirements_file = settings.fixtures_path / "requirements/basic.txt"
    formatted = settings.fixtures_path / "formatted/with_failures.json"
    # Patch dump to nullify origin
    expected = formatted.read_text().replace(
        "\"origin\": \"requirements/basic.txt\"",
        "\"origin\": null"
    )

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report", "-",
            "--format", "json",
            "--cachedir", str(cachedir)
        ],
        input=requirements_file.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == expected + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_report_no_failures_from_stdin(caplog, settings):
    """
    Command should succeed to analyze from standard input and return a
    RST format without failures included and titles. Logs are muted.

    NOTE: We use JSON format because it is easier to patch origin with stdin (no
    origin) and expected dump (include an origin).
    """
    cachedir = settings.fixtures_path / "api_cache"
    requirements_file = settings.fixtures_path / "requirements/basic.txt"
    formatted = settings.fixtures_path / "formatted/no_failures.json"
    # Patch dump to nullify origin
    expected = formatted.read_text().replace(
        "\"origin\": \"requirements/basic.txt\"",
        "\"origin\": null"
    )

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report", "-",
            "--no-failures",
            "--format", "json",
            "--cachedir", str(cachedir)
        ],
        input=requirements_file.read_text()
    )

    assert result.exit_code == 0

    assert result.output == expected + "\n"

    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_report_to_file(caplog, tmp_path, settings):
    """
    Command should write RST to a file instead of standard output and logging
    some messages.
    """
    cachedir = settings.fixtures_path / "api_cache"
    destination = tmp_path / "format.rst"
    expected = settings.fixtures_path / "formatted/no_failures.rst"
    requirements_file = settings.fixtures_path / "requirements/basic.txt"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "report",
            "-",
            "--no-failures",
            "--cachedir",
            str(cachedir),
            "--destination",
            str(destination)
        ],
        input=requirements_file.read_text()
    )

    # if result.exit_code > 0:
    #     import traceback
    #     klass, error, error_tb = result.exc_info
    #     print(error)
    #     traceback.print_tb(error_tb, limit=None)
    #     raise error

    assert result.exit_code == 0

    # Written format contains have an additional newline character
    assert expected.read_text() == destination.read_text()

    assert caplog.record_tuples == [
        (__pkgname__, 20, "Processing package: django"),
        (__pkgname__, 20, "Processing package: Pillow"),
        (__pkgname__, 20, "Processing package: djangorestframework"),
        (__pkgname__, 20, "Processing package: django-admin-shortcuts"),
        (__pkgname__, 20, "Processing package: requests"),
        (__pkgname__, 20, "Processing package: urllib3"),
        (__pkgname__, 20, "Report written to: {}".format(destination)),
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
            "report",
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
