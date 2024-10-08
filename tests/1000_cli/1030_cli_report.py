from freezegun import freeze_time

from click.testing import CliRunner

from dependency_comb.cli.entrypoint import cli_frontend


def test_report_default(caplog):
    """
    Command should fail without requirement arguments/options.
    """
    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["report"])

    msg = (
        "Error: Invalid value for 'SOURCE': 'requirements.txt': No such file or "
        "directory"
    )

    assert result.exit_code == 2
    assert msg in result.output
    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_report_with_failures_from_stdin(caplog, settings):
    """
    Command should succeed to analyze from standard input and return a full
    RST format with failures included.
    """
    cachedir = settings.fixtures_path / "api_cache"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.rst"
    requirements_file = settings.fixtures_path / "pip_syntax/requirements.txt"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["-v", "0", "report", "-", "--cachedir", str(cachedir), "--failures"],
        input=requirements_file.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_report_without_failures_from_stdin(caplog, settings):
    """
    Command should succeed to analyze from standard input and return a
    RST format without failures included and titles. Logs are muted.
    """
    cachedir = settings.fixtures_path / "api_cache"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.rst"
    requirements_file = settings.fixtures_path / "pip_syntax/requirements.txt"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["-v", "0", "report", "-", "--cachedir", str(cachedir)],
        input=requirements_file.read_text()
    )

    assert result.exit_code == 0

    assert result.output == formatted.read_text()

    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_report_without_failures_to_file(caplog, tmp_path, settings):
    """
    Command should should write JSON to a file instead of standard output and logging
    some messages.
    """
    cachedir = settings.fixtures_path / "api_cache"
    destination = tmp_path / "format.rst"
    expected = settings.fixtures_path / "pip_syntax/formatted_without_failures.rst"
    requirements_file = settings.fixtures_path / "pip_syntax/requirements.txt"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["report", "-", "--cachedir", str(cachedir), "--destination", str(destination)],
        input=requirements_file.read_text()
    )
    assert result.exit_code == 0

    # Written format contains have an additional newline character
    assert expected.read_text() == destination.read_text() + "\n"

    assert caplog.record_tuples == [
        ("dependency-comb", 20, "Processing package: django"),
        ("dependency-comb", 20, "Processing package: Pillow"),
        ("dependency-comb", 20, "Processing package: djangorestframework"),
        ("dependency-comb", 20, "Processing package: django-admin-shortcuts"),
        ("dependency-comb", 20, "Processing package: requests"),
        ("dependency-comb", 20, "Processing package: urllib3"),
    ]
