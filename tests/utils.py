from os import getenv
from pathlib import Path

import dependency_comb


# API key filename
API_FILEKEY_FILENAME = "librariesio-key.txt"
API_ENABLED_ENVVAR = "COMB_TEST_API_ENABLED"


def get_api_key():
    """
    Get Libraries.io API key from expected file ``librariesio-key.txt`` at project root.

    Returns:
        string: Either the API key found from file if it exists else return
        None.
    """
    package_path = Path(
        dependency_comb.__file__
    ).parents[0].resolve().parent

    filekey = package_path / API_FILEKEY_FILENAME
    if filekey.exists():
        key = filekey.read_text().strip()
        if key:
            return key

    return None


# Condition to enable API request depends from existing API key file and environment
# variable
skip_api_condition = (
    get_api_key() is None or
    getenv(API_ENABLED_ENVVAR, default="").strip().lower() != "true"
)
