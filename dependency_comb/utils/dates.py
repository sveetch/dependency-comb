import datetime


def parse_pypi_date(content):
    """
    Parse a string that is expected to be a datetime in ISO format.

    There is currently two known formats from Pypi for dates:

    * ``2022-10-29T14:15:57.755859Z``
    * ``2022-10-29T14:15:57Z``

    Any other format would probably raise an error from datetime parser.

    Arguments:
        content (string): Expected datetime in ISO format.

    Returns:
        datetime: Parsed datetime
    """
    # Remove microseconds with timezone marker 'Z'
    if "." in content:
        content = content.split(".")[0]

    # Remove simple timezone marker 'Z'
    if content.endswith("Z"):
        content = content[:-1]

    return datetime.datetime.fromisoformat(content)
