import json

import pytest
from freezegun import freeze_time
from click.testing import CliRunner

from dependency_comb import __pkgname__
from dependency_comb.cli.entrypoint import cli_frontend
from dependency_comb.formatting import AVAILABLE_FORMATS
from dependency_comb.compat.click_support import ABORT_ENDING


def test_default(caplog):
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
def test_all(caplog, settings):
    """
    Command should succeed to analyze from file and return a full RST report.
    """
    requirements_file = settings.fixtures_path / "requirements/complete.txt"
    formatted = settings.fixtures_path / "formatted/complete_all.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report",
            str(requirements_file),
            "--format", "rst",
            "--cachedir", str(settings.apicache_path),
        ],
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == formatted.read_text() + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_all_env(caplog, settings):
    """
    When environment dict is given to command, markers are evaluated again environment
    and can lead to some requirement to be rejected.
    """
    requirements_file = settings.fixtures_path / "requirements/complete.txt"
    environment_file = settings.fixtures_path / "env_requirements.json"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report",
            str(requirements_file),
            "--format", "json",
            "--cachedir", str(settings.apicache_path),
            "--env", str(environment_file),
        ],
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    # 'requests' is not in analyzed since it has been rejected by marker
    loaded = json.loads(result.output)
    assert "requests" not in [v["name"] for v in loaded["analyzed"]]

    # 'requests' is in failures as a 'marker-reject'
    rejected = [v for v in loaded["failures"] if v["status"] == "marker-reject"]
    assert rejected == [
        {
            "key": 1,
            "source": "requests [security] >= 2.8.1, == 2.8.* ;\n"
            "python_version < \"2.7\"",
            "status": "marker-reject",
            "resume": "Rejected by marker evaluation against\ngiven environment",
            "lineno": 8,
            "origin": "complete.txt",
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_without_duplicates(caplog, settings):
    """
    Command should succeed to analyze from file and return a RST report without
    duplicates.
    """
    requirements_file = settings.fixtures_path / "requirements/complete.txt"
    formatted = settings.fixtures_path / "formatted/complete_without_duplicates.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report",
            str(requirements_file),
            "--no-duplicates",
            "--format", "rst",
            "--cachedir", str(settings.apicache_path),
        ],
    )

    assert result.exit_code == 0

    assert result.output == formatted.read_text() + "\n"

    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_without_failures(caplog, settings):
    """
    Command should succeed to analyze from file and return a RST report without
    failures.
    """
    requirements_file = settings.fixtures_path / "requirements/complete.txt"
    formatted = settings.fixtures_path / "formatted/complete_without_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report",
            str(requirements_file),
            "--no-failures",
            "--format", "rst",
            "--cachedir", str(settings.apicache_path),
        ],
    )

    assert result.exit_code == 0

    assert result.output == formatted.read_text() + "\n"

    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_all_from_stdin(caplog, settings):
    """
    Command should succeed to analyze from standard input and return a full
    JSON format with failures included.

    NOTE: We use JSON format because it is easier to patch origin with stdin (no
    origin) and expected dump (include an origin).
    """
    requirements_file = settings.fixtures_path / "requirements/complete.txt"
    formatted = settings.fixtures_path / "formatted/complete_all.json"
    # Patch dump to nullify origin
    expected = formatted.read_text().replace(
        "\"origin\": \"complete.txt\"",
        "\"origin\": null"
    )

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "-v", "0",
            "report", "-",
            "--format", "json",
            "--cachedir", str(settings.apicache_path),
        ],
        input=requirements_file.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == expected + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_all_to_rst_file(caplog, tmp_path, settings):
    """
    Command should write RST to a file instead of standard output and logging
    some messages.
    """
    destination = tmp_path / "format.rst"
    requirements_file = settings.fixtures_path / "requirements/complete.txt"
    expected = settings.fixtures_path / "formatted/complete_all.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "report",
            str(requirements_file),
            "--cachedir",
            str(settings.apicache_path),
            "--destination",
            str(destination),
        ],
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
def test_empty_input(caplog, settings, format_name):
    """
    Ensure empty input is properly managed.

    TODO: In fact it should raise another kind of error for an empty input.
    """
    runner = CliRunner()

    result = runner.invoke(
        cli_frontend,
        [
            "report",
            "-",
            "--no-failures",
            "--format", format_name,
        ],
        input=""
    )

    assert result.exit_code == 1
    assert result.output == (
        "There was no data to format.\nAborted{}\n".format(ABORT_ENDING)
    )
    assert caplog.record_tuples == []


@pytest.mark.parametrize("format_name", AVAILABLE_FORMATS)
def test_empty_analyze(caplog, settings, format_name):
    """
    Ensure empty analyze is properly managed.
    """
    runner = CliRunner()

    result = runner.invoke(
        cli_frontend,
        [
            "report",
            "-",
            "--no-failures",
            "--format", format_name,
        ],
        input="./downloads/numpy-1.9.2-cp34-none-win32.whl"
    )

    assert result.exit_code == 1
    assert result.output == (
        "There was no data to format.\nAborted{}\n".format(ABORT_ENDING)
    )
    assert caplog.record_tuples == []
