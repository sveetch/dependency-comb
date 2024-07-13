from click.testing import CliRunner

from dependency_comb.cli.entrypoint import cli_frontend


def test_analyze_default(caplog):
    """
    TODO
    """
    runner = CliRunner()

    result = runner.invoke(cli_frontend, ["analyze"])

    msg = "Error: Invalid value for 'SOURCE': 'requirements.txt': No such file or directory"

    assert result.exit_code == 2
    assert msg in result.output
    assert caplog.record_tuples == []
