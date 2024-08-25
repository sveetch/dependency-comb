import datetime
import json

from pathlib import Path


class BaseFormatter:
    """
    Base formatter just defines some internal attributes and return Python object from
    given JSON.

    Arguments:
        now_date (datetime): A datetime to set instead of default ``datetime.now()``.
            This datetime is used to compute the delta time between release and current
            date.
    """
    def __init__(self, now_date=None):
        self.now_date = now_date or datetime.datetime.now()

    def output(self, content):
        """
        Returns formatted output.

        This base method only parse given content and returns it as a Python list.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. It
                can be either:

                * A JSON as a string that will be parsed;
                * A file Path that will be readed and parsed as JSON;
                * A list that is expected to be directly the list of analyzed
                  requirements, no parsing will be involved.

        Returns:
            list: The list of analyzed requirements.
        """
        if isinstance(content, list):
            return content

        if isinstance(content, Path):
            content = content.read_text()

        data = json.loads(content)

        return data
