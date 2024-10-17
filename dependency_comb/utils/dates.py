import datetime


def safe_isoformat_parse(content):
    """
    Parse a string that is expected to be a datetime in ISO format.

    There is currently known two format from Pypi for dates:

    * 2022-10-29T14:15:57.755859Z
    * 2022-10-29T14:15:57Z

    Any other format would probably raise an error from datetime parsing.

    Arguments:
        content (string): Expected datetime in ISO format.

    Returns:
        datetime: Parsed datetime
    """
    # Remove microsecond with timezone Z
    if "." in content:
        content = content.split(".")[0]

    # Remove remaining timezone Z
    if content.endswith("Z"):
        content = content[:-1]

    return datetime.datetime.fromisoformat(content)
