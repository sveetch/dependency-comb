import json

from click.testing import CliRunner

from dependency_comb.cli.entrypoint import cli_frontend


def test_analyze_default(caplog):
    """
    Command should fail without requirement arguments/options.
    """
    runner = CliRunner()
    result = runner.invoke(cli_frontend, ["analyze"])

    msg = (
        "Error: Invalid value for 'SOURCE': 'requirements.txt': No such file or "
        "directory"
    )

    assert result.exit_code == 2
    assert msg in result.output
    assert caplog.record_tuples == []


def test_analyze_basic(caplog, settings):
    """
    Command should succeed to compute informations for requirement packages given
    from standard input. We use cache to speed up tests.
    """
    cachedir = settings.fixtures_path / "api_cache"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "analyze",
            "-",
            "--cachedir", str(cachedir),
        ],
        input="django==3.2.1\ndiskette",
    )
    print(result.output)

    assert result.exit_code == 0
    assert caplog.record_tuples == []

    results = json.loads(result.output)
    assert len(results) == 2
    assert results[0]["name"] == "django"
    assert results[1]["name"] == "diskette"
