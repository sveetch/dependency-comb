from dependency_comb.formatting import BaseFormatter


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
