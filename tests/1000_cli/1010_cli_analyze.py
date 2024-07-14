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


def test_analyze_from_stdin(caplog, settings):
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
    assert result.exit_code == 0

    results = json.loads(result.output)
    assert len(results) == 2
    assert [v["name"] for v in results] == [
        "django",
        "diskette",
    ]
    assert caplog.record_tuples == []


def test_analyze_from_file(caplog, settings):
    """
    Command should succeed to compute informations for requirement packages given
    from file path. We use cache to speed up tests.
    """
    cachedir = settings.fixtures_path / "api_cache"
    requirements_file = settings.fixtures_path / "pip_requirements.txt"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "analyze",
            str(requirements_file),
            "--cachedir", str(cachedir),
        ],
    )
    assert result.exit_code == 0

    results = json.loads(result.output)
    assert len(results) == 9
    assert [v["name"] for v in results] == [
        "django",
        "Pillow",
        "djangorestframework",
        "django-admin-shortcuts",
        None,
        "requests",
        "urllib3",
        None,
        None,
    ]
    assert caplog.record_tuples == []


def test_analyze_to_file(caplog, tmp_path, settings):
    """
    Command should should write JSON to a file instead of standard output and log out
    some messages.
    """
    cachedir = settings.fixtures_path / "api_cache"
    destination = tmp_path / "analyze.json"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "analyze",
            "-",
            "--cachedir", str(cachedir),
            "--destination", str(destination),
        ],
        input="django==3.2.1\ndiskette",
    )
    assert result.exit_code == 0

    results = json.loads(destination.read_text())
    assert len(results) == 2
    assert [v["name"] for v in results] == [
        "django",
        "diskette",
    ]
    assert caplog.record_tuples == [
        ("dependency-comb", 20, "Processing package: django"),
        ("dependency-comb", 20, "Processing package: diskette"),
    ]


def test_analyze_with_env(caplog, settings):
    """
    Command should succeed to compute informations for requirement packages given
    from file path. We use cache to speed up tests.
    """
    cachedir = settings.fixtures_path / "api_cache"
    requirements_file = settings.fixtures_path / "pip_requirements.txt"
    environment_file = settings.fixtures_path / "env_requirements.json"

    runner = CliRunner()
    result = runner.invoke(
        cli_frontend,
        [
            "analyze",
            str(requirements_file),
            "--cachedir", str(cachedir),
            "--env", str(environment_file),
        ],
    )
    assert result.exit_code == 0

    results = json.loads(result.output)
    names = [
        v["name"]
        for v in results
        if v["status"] != "marker-reject"
    ]
    assert len(results) == 9
    assert names == [
        "django",
        "Pillow",
        "djangorestframework",
        "django-admin-shortcuts",
        None,
        "urllib3",
        None,
        None,
    ]
    assert caplog.record_tuples == []