from io import StringIO

from freezegun import freeze_time

from dependency_comb.formatting import RichFormatter


@freeze_time("2024-07-25 10:00:00")
def test_rich_print(settings):
    """
    Without failures enabled the output should only contains the analyzed table.

    Rich formatter does not use the given printer.

    NOTE: Rich can make some empty line with some whitespace that can not be visible,
    be careful when editing the '*.rich' files.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.rich"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RichFormatter()

    console = formatter.print(analyze, destination=StringIO(), with_failures=False)
    assert console.file.getvalue() == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_rich_print_with_failures(settings):
    """
    With failures enabled the output should contains the analyzed and failures tables.

    Rich formatter does not use the given printer.

    NOTE: Rich can make some empty line with some whitespace that can not be visible,
    be careful when editing the '*.rich' files.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.rich"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RichFormatter()

    console = formatter.print(analyze, destination=StringIO(), with_failures=True)
    assert console.file.getvalue() == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_rich_write_with_failures(settings, tmp_path):
    """
    Rich writer method should write the console output in given destination file.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.rich"
    destination = tmp_path / "output.rich"

    formatter = RichFormatter()
    formatter.write(analyze, destination=destination, with_failures=True)

    assert destination.read_text() == formatted.read_text()
