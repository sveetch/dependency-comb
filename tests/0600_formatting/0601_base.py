import json
from pathlib import Path

import pytest
from freezegun import freeze_time
from packaging.requirements import SpecifierSet
from packaging.version import Version

from tests.utils import complete_analyze, minimal_analyze  # noqa: F401

from dependency_comb.exceptions import FormatterEmptyContentError
from dependency_comb.formatting import BaseFormatter


@pytest.mark.skip("Loading content from a file is deprecated")
def test_open_content_from_filepath(settings):
    """
    Base formatter is able to open analyze from a file path and returns deserialized
    JSON to Python data.

    DEPRECATED: We still have to remove its usage from code and tests
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    formatter = BaseFormatter()

    content = formatter.open_content(analyze)
    assert len(content) == 8
    assert [v["source"] for v in content] == [
        "django>=1.11,<1.12",
        "Pillow>=3.1.1 # With useless comment",
        "djangorestframework",
        "django-admin-shortcuts==1.2.6",
        "requests [security] >= 2.8.1, == 2.8.* ; python_version < \"2.7\"",
        "urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip",
        "./downloads/numpy-1.9.2-cp34-none-win32.whl",
        (
            "http://wxpython.org/Phoenix/snapshot-builds/wxPython_Phoenix-3.0.3."
            "dev1820+49a8884-cp34-none-win_amd64.whl"
        ),
    ]


@pytest.mark.skip("Loading content from a string is deprecated")
def test_open_content_from_string(settings):
    """
    Base formatter is able to open analyze from a string and returns deserialized JSON
    to Python data.

    DEPRECATED: We still have to remove its usage from code and tests
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"

    formatter = BaseFormatter()
    content = formatter.open_content(analyze.read_text())

    assert len(content) == 8
    assert [v["source"] for v in content] == [
        "django>=1.11,<1.12",
        "Pillow>=3.1.1 # With useless comment",
        "djangorestframework",
        "django-admin-shortcuts==1.2.6",
        "requests [security] >= 2.8.1, == 2.8.* ; python_version < \"2.7\"",
        "urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip",
        "./downloads/numpy-1.9.2-cp34-none-win32.whl",
        (
            "http://wxpython.org/Phoenix/snapshot-builds/wxPython_Phoenix-3.0.3."
            "dev1820+49a8884-cp34-none-win_amd64.whl"
        ),
    ]


@freeze_time("2024-07-25 10:00:00")
def test_build_analyzed_table(minimal_analyze):  # noqa: F811
    """
    Method should build a list of dictionnaries for all items with status 'analyzed'.
    """
    formatter = BaseFormatter()

    output = formatter.build_analyzed_table([
        v.serialize()
        for v in minimal_analyze.packages
        if v.status == "analyzed"
    ])
    assert output == [
        {
            "key": 1,
            "name": "django",
            "lateness": 187,
            "resolved_version": "1.11.9 - 6 years ago",
            "latest_release": "5.1.2 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": Version("1.11.9"),
            "release_age": "6 years",
            "lineno": 2,
            "origin": Path("minimal.txt")
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_build_duplicates_table(complete_analyze):  # noqa: F811
    """
    Method should build a list of dictionnaries for given items.
    """
    formatter = BaseFormatter()

    output = formatter.build_duplicates_table([
        v.serialize()
        for v in complete_analyze.packages
        if v.status == "duplicated"
    ])
    assert output == [
        {
            "key": 1,
            "name": "django",
            "source": "django<1.12",
            "specifier": SpecifierSet("<1.12"),
            "lineno": 17,
            "origin": Path("complete.txt"),
        },
        {
            "key": 2,
            "name": "django-admin-shortcuts",
            "source": "django-admin-shortcuts",
            "specifier": SpecifierSet(""),
            "lineno": 18,
            "origin": Path("complete.txt"),
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_build_errors_table(complete_analyze):  # noqa: F811
    """
    Method should build a list of dictionnaries for given items.
    """
    formatter = BaseFormatter()

    output = formatter.build_errors_table([
        v.serialize()
        for v in complete_analyze.packages
        if v.status not in ("analyzed", "duplicated")
    ])
    assert output == [
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported",
            "lineno": 12,
            "origin": Path("complete.txt")
        },
        {
            "key": 2,
            "source": "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-",
            "status": "unsupported-url",
            "resume": "Direct package URL is not supported",
            "lineno": 15,
            "origin": Path("complete.txt")
        }
    ]


@pytest.mark.parametrize(
    "analyzed, duplicated, failed, with_failures, with_duplicates",
    [
        (
            [
                "django",
                "Pillow",
                "djangorestframework",
                "django-admin-shortcuts",
                "requests",
                "urllib3",
            ],
            ["django", "django-admin-shortcuts"],
            [
                "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
                "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-",
            ],
            True,
            True,
        ),
        (
            [
                "django",
                "Pillow",
                "djangorestframework",
                "django-admin-shortcuts",
                "requests",
                "urllib3",
            ],
            ["django", "django-admin-shortcuts"],
            [],
            False,
            True,
        ),
        (
            [
                "django",
                "Pillow",
                "djangorestframework",
                "django-admin-shortcuts",
                "requests",
                "urllib3",
            ],
            [],
            [
                "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
                "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-",
            ],
            True,
            False,
        ),
        (
            [
                "django",
                "Pillow",
                "djangorestframework",
                "django-admin-shortcuts",
                "requests",
                "urllib3",
            ],
            [],
            [],
            False,
            False,
        ),
    ]
)
def test_build(complete_analyze, analyzed, duplicated, failed,  # noqa: F811
               with_failures, with_duplicates):
    """
    The build method should return found analyzed and possible failured and duplicated
    (according to options).
    """
    formatter = BaseFormatter()

    results = formatter.build(
        [pkg.serialize() for pkg in complete_analyze.packages],
        with_failures=with_failures,
        with_duplicates=with_duplicates
    )
    assert [v["name"] for v in results.analyzed] == analyzed
    assert [v["name"] for v in results.duplicated] == duplicated
    assert [v["source"] for v in results.failed] == failed


def test_build_empty():
    """
    Build method should raise an error if there is no success and failures.
    """
    formatter = BaseFormatter()

    # If content is empty
    with pytest.raises(FormatterEmptyContentError):
        formatter.build([])


@freeze_time("2024-07-25 10:00:00")
def test_print_all(minimal_analyze):  # noqa: F811
    """
    Printer method should write its result outputs into given printer function.
    """
    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.extend(content)

    formatter = BaseFormatter(printer=receiver)
    formatter.print(
        [v.serialize() for v in minimal_analyze.packages],
        with_failures=True,
        with_duplicates=True,
    )

    assert output == [
        {
            "key": 1,
            "name": "django",
            "lateness": 187,
            "resolved_version": "1.11.9 - 6 years ago",
            "latest_release": "5.1.2 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": Version("1.11.9"),
            "release_age": "6 years",
            "lineno": 2,
            "origin": Path("minimal.txt")
        },
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported",
            "lineno": 5,
            "origin": Path("minimal.txt")
        },
        {
            "key": 1,
            "name": "django",
            "source": "django>=1.11",
            "specifier": SpecifierSet(">=1.11"),
            "lineno": 7,
            "origin": Path("minimal.txt"),
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_write_all(minimal_analyze, tmp_path):  # noqa: F811
    """
    Base writer method should write its result outputs as JSON into given file
    destination.
    """
    destination = tmp_path / "output.json"

    formatter = BaseFormatter()
    formatter.write(
        [v.serialize() for v in minimal_analyze.packages],
        destination,
        with_failures=True,
        with_duplicates=True,
    )

    assert json.loads(destination.read_text()) == [
        {
            "key": 1,
            "name": "django",
            "lateness": 187,
            "resolved_version": "1.11.9 - 6 years ago",
            "latest_release": "5.1.2 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "1.11.9",
            "release_age": "6 years",
            "lineno": 2,
            "origin": "minimal.txt"
        },
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported",
            "lineno": 5,
            "origin": "minimal.txt"
        },
        {
            "key": 1,
            "name": "django",
            "source": "django>=1.11",
            "specifier": ">=1.11",
            "lineno": 7,
            "origin": "minimal.txt",
        },
    ]
