from freezegun import freeze_time

from dependency_comb.formatting import CSVFormatter


@freeze_time("2024-07-25 10:00:00")
def test_csv_print(settings):
    """
    Without failures enabled the output should only contains the analyzed table.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.csv"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = CSVFormatter(printer=receiver)
    formatter.print(analyze, with_failures=False)

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_csv_print_with_failures(settings):
    """
    With failures enabled the output should contains the analyzed and failures tables.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.csv"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = CSVFormatter(printer=receiver)
    formatter.print(analyze, with_failures=True)
    # formatted.write_text("".join(output))

    assert "".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_csv_write_with_failures(settings, tmp_path):
    """
    CSV writer method should write output in given destination file.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.csv"
    destination = tmp_path / "output.csv"

    formatter = CSVFormatter()
    formatter.write(analyze, destination=destination, with_failures=True)

    assert destination.read_text() == formatted.read_text()
