import json

import pytest
from freezegun import freeze_time

from dependency_comb.analyzer import DependenciesAnalyzer
from dependency_comb.exceptions import FormatterEmptyContentError
from dependency_comb.formatting import BaseFormatter


def test_open_content_from_filepath(settings):
    """
    Base formatter is able to open analyze from a file path and returns deserialized
    JSON to Python data.

    NOTE: This is mostly to be deprecated in a further release.
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
    Base formatter is able to open analyze from a string and returns deserialized JSON
    to Python data.

    NOTE: This is mostly to be deprecated in a further release.
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
def test_build_analyzed_table(settings):
    """
    Method should build a list of dictionnaries for all items with status 'analyzed'.
    """
    analyze = settings.fixtures_path / "analyzes/success_only.json"
    analyze_content = [
        v
        for v in json.loads(analyze.read_text())
        if v["status"] == "analyzed"
    ]
    # Use formatted dump but only use the analyzed part
    formatted_analyzed = json.loads(
        (settings.fixtures_path / "formatted/with_failures.json").read_text()
    )["analyzed"]

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
            "release_age": "6 years",
            "lineno": 2,
            "origin": "requirements/success_only.txt"
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_build_duplicates_table(settings):
    """
    Method should build a list of dictionnaries for given items.
    """
    analyze = settings.fixtures_path / "analyzes/basic_with_duplicates.json"
    analyze_content = [
        v
        for v in json.loads(analyze.read_text())
        if v["status"] == "duplicated"
    ]
    formatter = BaseFormatter()

    output = formatter.build_duplicates_table(analyze_content)
    assert output == [
        {
            "key": 1,
            "name": "django",
            "source": "django<1.12",
            "specifier": "<1.12",
            "lineno": 17,
            "origin": "requirements/basic_with_duplicates.txt",
        },
        {
            "key": 2,
            "name": "django-admin-shortcuts",
            "source": "django-admin-shortcuts",
            "specifier": "",
            "lineno": 18,
            "origin": "requirements/basic_with_duplicates.txt",
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_build_errors_table(settings):
    """
    Method should build a list of dictionnaries for given items.
    """
    analyze = settings.fixtures_path / "analyzes/basic.json"
    analyze_content = [
        v
        for v in json.loads(analyze.read_text())
        if v["status"] not in ("analyzed", "duplicated")
    ]
    formatter = BaseFormatter()

    output = formatter.build_errors_table(analyze_content)
    assert output == [
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported",
            "lineno": 12,
            "origin": "requirements/basic.txt"
        },
        {
            "key": 2,
            "source": "http://wxpython.org/Phoenix/snapshot-bui\nlds/wxPython_Phoenix-",
            "status": "unsupported-url",
            "resume": "Direct package URL is not supported",
            "lineno": 15,
            "origin": "requirements/basic.txt"
        }
    ]


@pytest.mark.parametrize("source, success, duplicated, failed, with_failures", [
    (
        "minimal_complete.txt",
        ["django"],
        ["django"],
        ["./downloads/numpy-1.9.2-cp34-none-\nwin32.whl"],
        True,
    ),
    (
        "minimal_success_and_failure.txt",
        ["django"],
        [],
        ["./downloads/numpy-1.9.2-cp34-none-\nwin32.whl"],
        True,
    ),
    (
        "minimal_success_and_failure.txt",
        ["django"],
        [],
        [],
        False,
    ),
    (
        "failure_only.txt",
        [],
        [],
        ["./downloads/numpy-1.9.2-cp34-none-\nwin32.whl"],
        True,
    ),
    (
        "success_only.txt",
        ["django"],
        [],
        [],
        True,
    ),
    (
        "success_only.txt",
        ["django"],
        [],
        [],
        False,
    ),
])
def test_build(settings, source, success, duplicated, failed, with_failures):
    """
    The build method should return found success and possibly failures (according to
    option).
    """
    analyze = (settings.fixtures_path / "requirements" / source).read_text()

    analyzer = DependenciesAnalyzer(cachedir=(settings.fixtures_path / "api_cache"))
    packages = analyzer.inspect(analyze)

    formatter = BaseFormatter()

    results = formatter.build(
        [pkg.serialize() for pkg in packages],
        with_failures=with_failures
    )
    assert [v["name"] for v in results.analyzed] == success
    assert [v["name"] for v in results.duplicated] == duplicated
    assert [v["source"] for v in results.failed] == failed


def test_build_empty(settings):
    """
    Build method should raise an error if there is no success and failures.
    """
    formatter = BaseFormatter()

    # If content is empty
    with pytest.raises(FormatterEmptyContentError):
        formatter.build([])

    # If analyze only have failures but they are disabled from option, this lead to
    # empty result
    analyze = (settings.fixtures_path / "requirements" / "failure_only.txt").read_text()
    analyzer = DependenciesAnalyzer(cachedir=(settings.fixtures_path / "api_cache"))
    packages = analyzer.inspect(analyze)
    with pytest.raises(FormatterEmptyContentError):
        formatter.build(
            [pkg.serialize() for pkg in packages],
            with_failures=False
        )


@freeze_time("2024-07-25 10:00:00")
def test_print(settings):
    """
    Printer method should write its result outputs into given printer function.
    """
    analyze = settings.fixtures_path / "analyzes/minimal_success_and_failure.json"
    analyze_content = json.loads(analyze.read_text())

    # Dummy printer function to receive output into 'output' to assert on it
    output = []

    def receiver(content, *args, **kwargs):
        output.extend(content)

    formatter = BaseFormatter(printer=receiver)
    formatter.print(analyze_content, with_failures=True)

    assert output == [
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
            "origin": "requirements/minimal_success_and_failure.txt"
        },
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported",
            "lineno": 5,
            "origin": "requirements/minimal_success_and_failure.txt"
        },
    ]


@freeze_time("2024-07-25 10:00:00")
def test_write(settings, tmp_path):
    """
    Base writer method should write its result outputs as JSON into given file
    destination.
    """
    analyze = settings.fixtures_path / "analyzes/minimal_success_and_failure.json"
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
            "release_age": "6 years",
            "lineno": 2,
            "origin": "requirements/minimal_success_and_failure.txt"
        },
        {
            "key": 1,
            "source": "./downloads/numpy-1.9.2-cp34-none-\nwin32.whl",
            "status": "unsupported-localpath",
            "resume": "Local package is not supported",
            "lineno": 5,
            "origin": "requirements/minimal_success_and_failure.txt"
        },
    ]
