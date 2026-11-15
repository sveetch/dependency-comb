from freezegun import freeze_time

from dependency_comb.formatting import RestructuredTextFormatter


def format_to_multline_str(content):
    """
    Shortand to format table output to a multiline string suitable for expected
    assertions.

    Each line will contain a Flake8 bypass code for "line too long".

    This is mostly an helper to rewrite test data fixtures during development.

    Arguments:
        content (string): The content to format.

    Returns:
        string: Formatted content.
    """
    total = len(content.splitlines())
    return "\n".join(
        [
            '"""{source}{newline}"""  # noqa: E501'.format(
                source=l.replace('"', '\\"'),
                newline="\\n" if i < total else "",
            )
            for i, l in enumerate(content.splitlines(), start=1)
        ]
    )


def test_rst_build_errors_table():
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
            "lineno": 1,
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
            "lineno": 2,
            "origin": None,
        },
        {
            "marker": None,
            "source": "nope",
            "specifier": None,
            "status": "unknown",
            "parsing_error": None,
            "lineno": 3,
            "origin": None,
        },
    ])

    # Used to rebuild table when code or formatting have changed
    # print("👷")
    # print(format_to_multline_str(output))
    # print("👷")

    assert output == (
        """\n"""  # noqa: E501
        """Failures\n"""  # noqa: E501
        """********\n"""  # noqa: E501
        """+-----+------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| #   | Source                             |        Status         | Resume                                 |\n"""  # noqa: E501
        """+=====+====================================+=======================+========================================+\n"""  # noqa: E501
        """| 1   | ./downloads/numpy-1.9.2-cp34-none- | unsupported-localpath | Local package is not supported         |\n"""  # noqa: E501
        """|     | win32.whl                          |                       |                                        |\n"""  # noqa: E501
        """+-----+------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 2   | -~@àlà                             |        invalid        | Invalid syntax: This could be an       |\n"""  # noqa: E501
        """|     |                                    |                       | exception error title without the long |\n"""  # noqa: E501
        """+-----+------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 3   | nope                               |        unknown        | Unexpected failure                     |\n"""  # noqa: E501
        """+-----+------------------------------------+-----------------------+----------------------------------------+"""  # noqa: E501
    )


@freeze_time("2024-07-25 10:00:00")
def test_rst_print(settings):
    """
    Without failures enabled the output should only contains the analyzed table.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    expected = settings.fixtures_path / "formatted/no_failures.rst"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)

    formatter.print(analyze, with_failures=False)
    assert "\n".join(output) == expected.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_rst_print_with_failures(settings):
    """
    With failures enabled the output should contains both analyzed and failed tables
    each with a title.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    expected = settings.fixtures_path / "formatted/with_failures.rst"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)
    formatter.print(analyze, with_failures=True)
    # print("👷")
    # print("\n".join(output))
    # print("👷")

    assert "\n".join(output) == expected.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_rst_write_without_failures(settings, tmp_path):
    """
    RST writer method should write the output formatted as RST in given destination
    file.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    expected = settings.fixtures_path / "formatted/no_failures.rst"
    destination = tmp_path / "output.rst"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RestructuredTextFormatter()
    formatter.write(analyze, destination=destination, with_failures=False)
    # print("👷")
    # print(destination.read_text())
    # print("👷")
    assert destination.read_text() == expected.read_text()
