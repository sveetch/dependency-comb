from freezegun import freeze_time

from dependency_comb.formatting import BaseFormatter, RestructuredTextFormatter


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


@freeze_time("2024-07-25 10:00:00")
def test_rst_build_analyzed_table(settings):
    """
    Method should build a table for succeeded analyzed items with proper informations.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    base_formatter = BaseFormatter()
    formatter = RestructuredTextFormatter()

    output = formatter.build_analyzed_table([
        v
        for v in base_formatter.output(analyze)
        if v["status"] == "analyzed"
    ])

    # Used to rebuild table when code or formatting have changed
    # print()
    # print(format_to_multline_str(output))
    # print()

    assert output == (
        """Analyzed\n"""  # noqa: E501
        """********\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+\n"""  # noqa: E501
        """| #   | Name                   |  Lateness  |                     Required |       Latest release |\n"""  # noqa: E501
        """+=====+========================+============+==============================+======================+\n"""  # noqa: E501
        """| 1   | django                 |    187     |         1.11.9 - 6 years ago | 5.1.2 - 2 months ago |\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+\n"""  # noqa: E501
        """| 2   | Pillow                 |     6      | 9.5.0 - 1 year, 3 months ago | 10.4.0 - 24 days ago |\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+\n"""  # noqa: E501
        """| 3   | djangorestframework    |     -      |                       Latest | 3.15.2 - A month ago |\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+\n"""  # noqa: E501
        """| 4   | django-admin-shortcuts |     6      |          1.2.6 - 9 years ago |   3.0.1 - 4 days ago |\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+\n"""  # noqa: E501
        """| 5   | requests               |     55     |          2.8.1 - 8 years ago | 2.32.3 - A month ago |\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+\n"""  # noqa: E501
        """| 6   | urllib3                |     -      |                       Latest |  2.2.3 - A month ago |\n"""  # noqa: E501
        """+-----+------------------------+------------+------------------------------+----------------------+"""  # noqa: E501
    )


def test_rst_build_errors_table():
    """
    Method should build a table for failures from items.
    """
    formatter = RestructuredTextFormatter()
    output = formatter.build_errors_table([
        {
            "marker": None,
            "source": "./downloads/numpy-1.9.2-cp34-none-win32.whl",
            "specifier": None,
            "status": "unsupported-localpath",
            "parsing_error": None
        },
        {
            "marker": None,
            "source": "http://wxpython.org/Phoenix/wxPython.whl",
            "specifier": None,
            "status": "unsupported-url",
            "parsing_error": None
        },
        {
            "marker": None,
            "source": "requests[security]>=2.8.1; python_version < \"2.7\"",
            "specifier": None,
            "status": "marker-reject",
            "parsing_error": None
        },
        {
            "marker": None,
            "source": "-c constraints.txt",
            "specifier": None,
            "status": "unsupported-argument",
            "parsing_error": None
        },
        {
            "marker": None,
            "source": "-~@élé",
            "specifier": None,
            "status": "invalid",
            "parsing_error": None
        },
        {
            "marker": None,
            "source": "-~@àlà",
            "specifier": None,
            "status": "invalid",
            "parsing_error": (
                "This could be an exception error title without the long traceback"
            ),
        },
        {
            "marker": None,
            "source": "nope",
            "specifier": None,
            "status": "unknown",
            "parsing_error": None
        },
        {
            "marker": None,
            "source": "nope",
            "specifier": None,
            "status": "niet",
            "parsing_error": None
        },
    ])

    # Used to rebuild table when code or formatting have changed
    # print()
    # print(format_to_multline_str(output))
    # print()

    assert output == (
        """\nFailures\n"""
        """********\n"""
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| #   | Source                                   |        Status         | Resume                                 |\n"""  # noqa: E501
        """+=====+==========================================+=======================+========================================+\n"""  # noqa: E501
        """| 1   | ./downloads/numpy-1.9.2-cp34-none-       | unsupported-localpath | Local package is not supported         |\n"""  # noqa: E501
        """|     | win32.whl                                |                       |                                        |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 2   | http://wxpython.org/Phoenix/wxPython.whl |    unsupported-url    | Direct package URL is not supported    |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 3   | requests[security]>=2.8.1;               |     marker-reject     | Rejected by marker evaluation against  |\n"""  # noqa: E501
        """|     | python_version < \"2.7\"                   |                       | given environment                      |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 4   | -c constraints.txt                       | unsupported-argument  | Unsupported Pip argument               |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 5   | -~@élé                                   |        invalid        | Invalid syntax: None                   |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 6   | -~@àlà                                   |        invalid        | Invalid syntax: This could be an       |\n"""  # noqa: E501
        """|     |                                          |                       | exception error title without the long |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 7   | nope                                     |        unknown        | Unexpected failure                     |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+\n"""  # noqa: E501
        """| 8   | nope                                     |         niet          | Unexpected failure                     |\n"""  # noqa: E501
        """+-----+------------------------------------------+-----------------------+----------------------------------------+"""  # noqa: E501
    )


@freeze_time("2024-07-25 10:00:00")
def test_rst_print(settings):
    """
    Without failures enabled the output should only contains the analyzed table.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.rst"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)

    formatter.print(analyze, with_failures=False)
    assert "\n".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_rst_output_with_failures(settings):
    """
    With failures enabled the output should contains both analyzed and failed tables
    each with a title.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_with_failures.rst"

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = RestructuredTextFormatter(printer=receiver)
    formatter.print(analyze, with_failures=True)

    assert "\n".join(output) == formatted.read_text()


@freeze_time("2024-07-25 10:00:00")
def test_rst_write_without_failures(settings, tmp_path):
    """
    RST writer method should write the output formatted as RST in given destination
    file.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatted = settings.fixtures_path / "pip_syntax/formatted_without_failures.rst"
    destination = tmp_path / "output.rst"

    # Dummy printer function to receive output into 'output' to assert on it
    formatter = RestructuredTextFormatter()
    formatter.write(analyze, destination=destination, with_failures=False)
    assert destination.read_text() == formatted.read_text()
