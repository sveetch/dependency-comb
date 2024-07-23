from freezegun import freeze_time

from dependency_comb.reporting import BaseReport, RestructuredTextReport


def format_to_multline_str(content):
    """
    Shortand to format table output to a multiline string suitable for expected
    assertions.

    Each line will contain a Flake8 bypass code for "line too long".
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


@freeze_time("2024-01-15 10:00:00")
def test_rst_build_analyzed_table(settings):
    """
    Method should build a table for succeeded analyzed items with proper informations.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    base_reporter = BaseReport()
    reporter = RestructuredTextReport()

    items = [
        v
        for v in base_reporter.output(analyze)
        if v["status"] == "analyzed"
    ]
    output = reporter.build_analyzed_table(items)

    # print()
    # print(format_to_multline_str(output))
    # print()

    assert output == (
        """+----+------------------------+------------+------------+-----------------------+\n"""  # noqa: E501
        """|    | Name                   |  Lateness  |  Required  |        Latest release |\n"""  # noqa: E501
        """+====+========================+============+============+=======================+\n"""  # noqa: E501
        """| 0  | django                 |    178     |   1.11.9   |   5.1a1 - A month ago |\n"""  # noqa: E501
        """+----+------------------------+------------+------------+-----------------------+\n"""  # noqa: E501
        """| 1  | Pillow                 |     6      |   9.5.0    |  10.4.0 - 15 days ago |\n"""  # noqa: E501
        """+----+------------------------+------------+------------+-----------------------+\n"""  # noqa: E501
        """| 2  | djangorestframework    |     -      |   Latest   |  3.15.2 - 27 days ago |\n"""  # noqa: E501
        """+----+------------------------+------------+------------+-----------------------+\n"""  # noqa: E501
        """| 3  | django-admin-shortcuts |     4      |   1.2.6    | 2.1.1 - 10 months ago |\n"""  # noqa: E501
        """+----+------------------------+------------+------------+-----------------------+\n"""  # noqa: E501
        """| 4  | requests               |     56     |   2.8.1    |  2.32.3 - A month ago |\n"""  # noqa: E501
        """+----+------------------------+------------+------------+-----------------------+\n"""  # noqa: E501
        """| 5  | urllib3                |     -      |   Latest   | 1.26.19 - 29 days ago |\n"""  # noqa: E501
        """+----+------------------------+------------+------------+-----------------------+"""  # noqa: E501
    )
