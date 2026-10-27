import json

from freezegun import freeze_time

from dependency_comb.formatting import JSONFormatter


@freeze_time("2024-07-25 10:00:00")
def test_json_print(settings):
    """
    Without failures enabled the output should only contains the analyzed table.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.json"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = JSONFormatter(printer=receiver)
    formatter.print(analyze, with_failures=False)

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_json_print_with_failures(settings):
    """
    With failures enabled the output should contains the analyzed and failures tables.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.json"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = JSONFormatter(printer=receiver)
    formatter.print(analyze, with_failures=False)

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_json_write_with_failures(settings, tmp_path):
    """
    JSON writer method should write JSON data into given destination file.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.json"
    destination = tmp_path / "output.json"

    formatter = JSONFormatter()
    formatter.write(analyze, destination=destination, with_failures=True)

    assert json.loads(destination.read_text()) == json.loads(formatted.read_text())
