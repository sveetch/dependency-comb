import json

import pytest
from freezegun import freeze_time

from dependency_comb.exceptions import FormatterEmptyContentError
from dependency_comb.formatting import BaseFormatter


@freeze_time("2024-07-25 10:00:00")
def test_build_analyzed_table(settings):
    """
    Method should build a list of dictionnaries for all items with status 'analyzed'.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    analyze_content = json.loads(analyze.read_text())
    formatter = BaseFormatter()

    output = formatter.build_analyzed_table(analyze_content)
    assert output == [
        {
            "key": 1,
            "name": "django",
            "lateness": 187,
            "resolved_version": "1.11.9 - 6 years ago",
            "latest_release": "5.1.2 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "1.11.9",
            "release_age": "6 years"
        },
        {
            "key": 2,
            "name": "Pillow",
            "lateness": 6,
            "resolved_version": "9.5.0 - 1 year, 4 months ago",
            "latest_release": "10.4.0 - A month ago",
            "latest_activity": "a month",
            "release_label": "9.5.0",
            "release_age": "1 year, 4 months"
        },
        {
            "key": 3,
            "name": "djangorestframework",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "3.15.2 - A month ago",
            "latest_activity": "a month",
            "release_label": "Latest",
            "release_age": None
        },
        {
            "key": 4,
            "name": "django-admin-shortcuts",
            "lateness": 6,
            "resolved_version": "1.2.6 - 9 years ago",
            "latest_release": "3.0.1 - 4 days ago",
            "latest_activity": "4 days",
            "release_label": "1.2.6",
            "release_age": "9 years"
        },
        {
            "key": 5,
            "name": "requests",
            "lateness": 55,
            "resolved_version": "2.8.1 - 8 years ago",
            "latest_release": "2.32.3 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "2.8.1",
            "release_age": "8 years"
        },
        {
            "key": 6,
            "name": "urllib3",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "2.2.3 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "Latest",
            "release_age": None
        }
    ]


@freeze_time("2024-07-25 10:00:00")
def test_build_errors_table(settings):
    """
    Method should build a list of dictionnaries for all items except the ones with
    status 'analyzed'.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    analyze_content = json.loads(analyze.read_text())
    formatter = BaseFormatter()

    output = formatter.build_errors_table(analyze_content)
    assert output == [
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported"
        },
        {
            "key": 2,
            "source": "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-",
            "status": "unsupported-url",
            "resume": "Direct package URL is not supported"
        }
    ]


def test_open_content_from_filepath(settings):
    """
    Base formatter is able to open analyze from a file path but just returns
    deserialized JSON to Python data.
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


def test_open_content_from_string(settings):
    """
    Base formatter is able to open analyze from a string but just returns deserialized
    JSON to Python data.
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


@pytest.mark.parametrize("source, success, failed, with_failures", [
    (
        "minimal_success_and_failure.json",
        ["django"],
        ["./downloads/numpy-1.9.2-cp34-none-\nwin32.whl"],
        True,
    ),
    (
        "minimal_success_and_failure.json",
        ["django"],
        [],
        False,
    ),
    (
        "failure_only.json",
        [],
        ["./downloads/numpy-1.9.2-cp34-none-\nwin32.whl"],
        True,
    ),
    (
        "success_only.json",
        ["django"],
        [],
        True,
    ),
    (
        "success_only.json",
        ["django"],
        [],
        False,
    ),
])
def test_build(settings, source, success, failed, with_failures):
    """
    Build method should return found success and possibly failures (according to
    option).
    """
    analyzes = settings.fixtures_path / "analyzes"

    formatter = BaseFormatter()

    succeeds, failures = formatter.build(analyzes / source, with_failures=with_failures)
    assert [v["name"] for v in succeeds] == success
    assert [v["source"] for v in failures] == failed


def test_build_empty(settings):
    """
    Build method should raise an error if there is no success and failures.
    """
    formatter = BaseFormatter()

    # If content is empty
    with pytest.raises(FormatterEmptyContentError):
        formatter.build([])

    # If there is only failures but they are disabled from option, this lead to empty
    # result
    with pytest.raises(FormatterEmptyContentError):
        formatter.build(
            settings.fixtures_path / "analyzes/failure_only.json",
            with_failures=False
        )


@freeze_time("2024-07-25 10:00:00")
def test_print(settings):
    """
    Printer method should write its result outputs into given printer function.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    analyze_content = json.loads(analyze.read_text())

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.append(content)

    formatter = BaseFormatter(printer=receiver)
    formatter.print(analyze_content, with_failures=True)

    assert output == [
        [
            {
                "key": 1,
                "name": "django",
                "lateness": 187,
                "resolved_version": "1.11.9 - 6 years ago",
                "latest_release": "5.1.2 - 2 months ago",
                "latest_activity": "2 months",
                "release_label": "1.11.9",
                "release_age": "6 years"
            },
            {
                "key": 2,
                "name": "Pillow",
                "lateness": 6,
                "resolved_version": "9.5.0 - 1 year, 4 months ago",
                "latest_release": "10.4.0 - A month ago",
                "latest_activity": "a month",
                "release_label": "9.5.0",
                "release_age": "1 year, 4 months"
            },
            {
                "key": 3,
                "name": "djangorestframework",
                "lateness": "-",
                "resolved_version": "Latest",
                "latest_release": "3.15.2 - A month ago",
                "latest_activity": "a month",
                "release_label": "Latest",
                "release_age": None
            },
            {
                "key": 4,
                "name": "django-admin-shortcuts",
                "lateness": 6,
                "resolved_version": "1.2.6 - 9 years ago",
                "latest_release": "3.0.1 - 4 days ago",
                "latest_activity": "4 days",
                "release_label": "1.2.6",
                "release_age": "9 years"
            },
            {
                "key": 5,
                "name": "requests",
                "lateness": 55,
                "resolved_version": "2.8.1 - 8 years ago",
                "latest_release": "2.32.3 - 2 months ago",
                "latest_activity": "2 months",
                "release_label": "2.8.1",
                "release_age": "8 years"
            },
            {
                "key": 6,
                "name": "urllib3",
                "lateness": "-",
                "resolved_version": "Latest",
                "latest_release": "2.2.3 - 2 months ago",
                "latest_activity": "2 months",
                "release_label": "Latest",
                "release_age": None
            }
        ],
        [
            {
                "key": 1,
                "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
                "status": "unsupported-localpath",
                "resume": "Local package is not supported"
            },
            {
                "key": 2,
                "source": (
                    "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-"
                ),
                "status": "unsupported-url",
                "resume": "Direct package URL is not supported"
            }
        ]
    ]


@freeze_time("2024-07-25 10:00:00")
def test_write(settings, tmp_path):
    """
    Base writer method should write its result outputs as JSON into given file
    destination.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    analyze_content = json.loads(analyze.read_text())
    destination = tmp_path / "output.json"

    formatter = BaseFormatter()
    formatter.write(analyze_content, destination, with_failures=True)

    assert json.loads(destination.read_text()) == [
        {
            "key": 1,
            "name": "django",
            "lateness": 187,
            "resolved_version": "1.11.9 - 6 years ago",
            "latest_release": "5.1.2 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "1.11.9",
            "release_age": "6 years"
        },
        {
            "key": 2,
            "name": "Pillow",
            "lateness": 6,
            "resolved_version": "9.5.0 - 1 year, 4 months ago",
            "latest_release": "10.4.0 - A month ago",
            "latest_activity": "a month",
            "release_label": "9.5.0",
            "release_age": "1 year, 4 months"
        },
        {
            "key": 3,
            "name": "djangorestframework",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "3.15.2 - A month ago",
            "latest_activity": "a month",
            "release_label": "Latest",
            "release_age": None
        },
        {
            "key": 4,
            "name": "django-admin-shortcuts",
            "lateness": 6,
            "resolved_version": "1.2.6 - 9 years ago",
            "latest_release": "3.0.1 - 4 days ago",
            "latest_activity": "4 days",
            "release_label": "1.2.6",
            "release_age": "9 years"
        },
        {
            "key": 5,
            "name": "requests",
            "lateness": 55,
            "resolved_version": "2.8.1 - 8 years ago",
            "latest_release": "2.32.3 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "2.8.1",
            "release_age": "8 years"
        },
        {
            "key": 6,
            "name": "urllib3",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "2.2.3 - 2 months ago",
            "latest_activity": "2 months",
            "release_label": "Latest",
            "release_age": None
        },
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported"
        },
        {
            "key": 2,
            "source": "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-",
            "status": "unsupported-url",
            "resume": "Direct package URL is not supported"
        }
    ]
