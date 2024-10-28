import json

from dependency_comb.formatting import BaseFormatter


def test_base_build_analyzed_table(settings):
    """
    Method should build a list of dictionnaries for all items with status 'analyzed'.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    analyze_content = json.loads(analyze.read_text())
    formatter = BaseFormatter()

    output = formatter.build_analyzed_table(analyze_content)

    assert output == [
        {
            "key": 1,
            "name": "django",
            "lateness": 187,
            "resolved_version": "1.11.9 - 6 years ago",
            "latest_release": "5.1.2 - 19 days ago"
        },
        {
            "key": 2,
            "name": "Pillow",
            "lateness": 6,
            "resolved_version": "9.5.0 - 1 year, 6 months ago",
            "latest_release": "10.4.0 - 3 months ago"
        },
        {
            "key": 3,
            "name": "djangorestframework",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "3.15.2 - 4 months ago"
        },
        {
            "key": 4,
            "name": "django-admin-shortcuts",
            "lateness": 6,
            "resolved_version": "1.2.6 - 9 years ago",
            "latest_release": "3.0.1 - 2 months ago"
        },
        {
            "key": 5,
            "name": "requests",
            "lateness": 55,
            "resolved_version": "2.8.1 - 9 years ago",
            "latest_release": "2.32.3 - 4 months ago"
        },
        {
            "key": 6,
            "name": "urllib3",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "2.2.3 - A month ago"
        }
    ]


def test_base_build_errors_table(settings):
    """
    Method should build a list of dictionnaries for all items except the ones with
    status 'analyzed'.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
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


def test_base_format_from_filepath(settings):
    """
    Base formatter is able to open analyze from a file path but just returns
    deserialized JSON to Python data.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatter = BaseFormatter()

    output = formatter.output(analyze)

    assert len(output) == 8
    assert [v["source"] for v in output] == [
        "django>=1.11,<1.12",
        "Pillow>=3.1.1",
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


def test_base_format_from_string(settings):
    """
    Base formatter is able to open analyze from a string but just returns deserialized
    JSON to Python data.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    formatter = BaseFormatter()

    output = formatter.output(analyze.read_text())

    assert len(output) == 8
    assert [v["source"] for v in output] == [
        "django>=1.11,<1.12",
        "Pillow>=3.1.1",
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


def test_base_print(settings):
    """
    Printer method should write its result outputs into given printer function.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
    analyze_content = json.loads(analyze.read_text())
    formatter = BaseFormatter()

    printted_out = []

    # Dummy printer function to receive output into 'printted_out' to assert on it
    def receiver(content):
        printted_out.append(content)

    formatter.print(analyze_content, printer=receiver, with_failures=True)

    assert printted_out == [
        # The successfully analyzed output
        [
            {
                "key": 1,
                "name": "django",
                "lateness": 187,
                "resolved_version": "1.11.9 - 6 years ago",
                "latest_release": "5.1.2 - 19 days ago"
            },
            {
                "key": 2,
                "name": "Pillow",
                "lateness": 6,
                "resolved_version": "9.5.0 - 1 year, 6 months ago",
                "latest_release": "10.4.0 - 3 months ago"
            },
            {
                "key": 3,
                "name": "djangorestframework",
                "lateness": "-",
                "resolved_version": "Latest",
                "latest_release": "3.15.2 - 4 months ago"
            },
            {
                "key": 4,
                "name": "django-admin-shortcuts",
                "lateness": 6,
                "resolved_version": "1.2.6 - 9 years ago",
                "latest_release": "3.0.1 - 2 months ago"
            },
            {
                "key": 5,
                "name": "requests",
                "lateness": 55,
                "resolved_version": "2.8.1 - 9 years ago",
                "latest_release": "2.32.3 - 4 months ago"
            },
            {
                "key": 6,
                "name": "urllib3",
                "lateness": "-",
                "resolved_version": "Latest",
                "latest_release": "2.2.3 - A month ago"
            }
        ],
        # The failures output
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


def test_base_write(settings, tmp_path):
    """
    Base writer method should write its result outputs as JSON into given file
    destination.
    """
    analyze = settings.fixtures_path / "pip_syntax/analyzed.json"
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
            "latest_release": "5.1.2 - 19 days ago"
        },
        {
            "key": 2,
            "name": "Pillow",
            "lateness": 6,
            "resolved_version": "9.5.0 - 1 year, 6 months ago",
            "latest_release": "10.4.0 - 3 months ago"
        },
        {
            "key": 3,
            "name": "djangorestframework",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "3.15.2 - 4 months ago"
        },
        {
            "key": 4,
            "name": "django-admin-shortcuts",
            "lateness": 6,
            "resolved_version": "1.2.6 - 9 years ago",
            "latest_release": "3.0.1 - 2 months ago"
        },
        {
            "key": 5,
            "name": "requests",
            "lateness": 55,
            "resolved_version": "2.8.1 - 9 years ago",
            "latest_release": "2.32.3 - 4 months ago"
        },
        {
            "key": 6,
            "name": "urllib3",
            "lateness": "-",
            "resolved_version": "Latest",
            "latest_release": "2.2.3 - A month ago"
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
