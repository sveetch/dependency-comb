from pathlib import Path

import dependency_comb


API_FILEKEY_FILENAME = "librariesio-key.txt"


def get_api_key():
    """
    Get Libraries.io API key retrieved from file ``librariesio-key.txt`` at this
    project root.

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
