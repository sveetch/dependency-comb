from freezegun import freeze_time

from tests.utils import complete_analyze  # noqa: F401

from dependency_comb.formatting import RestructuredTextFormatter


def test_build_errors_table():
    """
    Ensure all error cases are well formatted.

    NOTE: We use some custom samples to ensure long string are managed well.
    """
    formatter = RestructuredTextFormatter()
    output = formatter.build_errors_table([
        {
            "marker": None,
            "source": "./downloads/numpy-1.9.2-cp34-none-win32.whl",
            "specifier": None,
            "status": "unsupported-localpath",
            "parsing_error": None,
            "lineno": 4,
            "origin": None,
        },
        {
            "marker": None,
            "source": "-~@àlà",
            "specifier": None,
            "status": "invalid",
            "parsing_error": (
                "This could be an exception error title without the long traceback"
            ),
            "lineno": 5,
            "origin": None,
        },
        {
            "marker": None,
            "source": "nope",
            "specifier": None,
            "status": "unknown",
            "parsing_error": None,
            "lineno": 6,
            "origin": None,
        },
    ])

    # Used to rebuild table when payload or formatter have changed behaviors
    # from tests.utils import format_to_multline_str
    # print("👷")
    # print(format_to_multline_str(output))
    # print("👷")

    assert output == (
        """\n"""  # noqa: E501
        """Failures\n"""  # noqa: E501
        """********\n\n"""  # noqa: E501
        """+-----+------------+------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| #   | Origin     | Source                             | Status                | Resume                                 |\n"""  # noqa: E501
        """+=====+============+====================================+=======================+========================================+\n"""  # noqa: E501
        """| 1   | <string>:4 | ./downloads/numpy-1.9.2-cp34-none- | unsupported-localpath | Local package is not supported         |\n"""  # noqa: E501
        """|     |            | win32.whl                          |                       |                                        |\n"""  # noqa: E501
        """+-----+------------+------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 2   | <string>:5 | -~@àlà                             | invalid               | Invalid syntax: This could be an       |\n"""  # noqa: E501
        """|     |            |                                    |                       | exception error title without the long |\n"""  # noqa: E501
        """+-----+------------+------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 3   | <string>:6 | nope                               | unknown               | Unexpected failure                     |\n"""  # noqa: E501
        """+-----+------------+------------------------------------+-----------------------+----------------------------------------+"""  # noqa: E501
    )


@freeze_time("2024-07-25 10:00:00")
def test_print_all(settings, complete_analyze):  # noqa: F811
    """
    Without failures enabled the output should only contains the analyzed table.
    """
    expected = settings.fixtures_path / "formatted/complete_all.rst"

    # Dummy printer function to receive and store output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)

    formatter.print(
        [v.serialize() for v in complete_analyze.packages],
        with_failures=True,
        with_duplicates=True,
    )
    assert "\n".join(output) == expected.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_print_without_failures(settings, complete_analyze):  # noqa: F811
    """
    With failures enabled the output should contains both analyzed and failed tables
    each with a title.
    """
    expected = settings.fixtures_path / "formatted/complete_without_failures.rst"

    # Dummy printer function to receive and store output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)
    formatter.print(
        [v.serialize() for v in complete_analyze.packages],
        with_failures=False,
        with_duplicates=True,
    )

    assert "\n".join(output) == expected.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_print_without_duplicates(settings, complete_analyze):  # noqa: F811
    """
    With failures enabled the output should contains both analyzed and duplicates tables
    each with a title.
    """
    expected = settings.fixtures_path / "formatted/complete_without_duplicates.rst"

    # Dummy printer function to receive and store output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)
    formatter.print(
        [v.serialize() for v in complete_analyze.packages],
        with_failures=True,
        with_duplicates=False,
    )

    assert "\n".join(output) == expected.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_write_all(settings, complete_analyze, tmp_path):  # noqa: F811
    """
    RST writer method should write the output formatted as RST in given destination
    file.
    """
    expected = settings.fixtures_path / "formatted/complete_all.rst"
    destination = tmp_path / "output.rst"

    formatter = RestructuredTextFormatter()
    formatter.write(
        [v.serialize() for v in complete_analyze.packages],
        destination=destination,
        with_failures=True,
        with_duplicates=True,
    )

    assert destination.read_text() == expected.read_text()
