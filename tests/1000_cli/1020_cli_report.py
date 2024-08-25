import json

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


def test_report_with_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a full
    RST report with failures included.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    report = settings.fixtures_path / "pip_syntax/report_with_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["report", "-", "--failures"],
        input=analyze.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == report.read_text()


def test_report_without_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a
    RST report without failures included and titles.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    report = settings.fixtures_path / "pip_syntax/report_without_failures.rst"

    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["report", "-"], input=analyze.read_text())

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == report.read_text()


def test_report_with_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a full
    RST report with failures included.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    report = settings.fixtures_path / "pip_syntax/report_with_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["report", "-", "--failures"],
        input=analyze.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    assert result.output == report.read_text()


def test_report_to_file(caplog, tmp_path, settings):
    """
    Command should should write JSON to a file instead of standard output and logging
    some messages.
    """
    cachedir = settings.fixtures_path / "api_cache"
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    destination = tmp_path / "report.rst"
    expected = settings.fixtures_path / "pip_syntax/report_without_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["report", "-", "--destination", str(destination)],
        input=analyze.read_text()
    )
    assert result.exit_code == 0

    # Written report contains an additional newline character
    assert expected.read_text() == destination.read_text() + "\n"
    assert caplog.record_tuples == [
        ("dependency-comb", 20, "Written report to: {}".format(destination)),
    ]
