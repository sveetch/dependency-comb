from freezegun import freeze_time

from click.testing import CliRunner

from dependency_comb.cli.entrypoint import cli_frontend


def test_format_default(caplog):
    """
    Command should fail without requirement arguments/options.
    """
    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["format"])

    msg = (
        "Error: Invalid value for 'SOURCE': 'requirements.txt': No such file or "
        "directory"
    )

    assert result.exit_code == 2
    assert msg in result.output
    assert caplog.record_tuples == []


@freeze_time("2024-07-25 10:00:00")
def test_format_with_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a
    RST format without failures included and titles.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.rst"

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
    assert result.output == formatted.read_text() + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_format_without_failures_from_stdin(caplog, settings):
    """
    Command should succeed to get JSON analyze from standard input and return a full
    RST format with failures included.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["format", "-", "--no-failures"],
        input=analyze.read_text()
    )

    assert result.exit_code == 0
    assert caplog.record_tuples == []
    assert result.output == formatted.read_text() + "\n"


@freeze_time("2024-07-25 10:00:00")
def test_format_without_failures_to_file(caplog, tmp_path, settings):
    """
    Command should should write JSON to a file instead of standard output and logging
    some messages.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    destination = tmp_path / "format.rst"
    expected = settings.fixtures_path / "pip_syntax/formatted_without_failures.rst"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        ["format", "-", "--no-failures", "--destination", str(destination)],
        input=analyze.read_text()
    )

    assert result.exit_code == 0

    # Written format contains have an additional newline character
    assert expected.read_text() == destination.read_text()

    assert caplog.record_tuples == [
        ("dependency-comb", 20, "Formatted analyze to: {}".format(destination)),
    ]
