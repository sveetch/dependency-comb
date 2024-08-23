import datetime
import json

from pathlib import Path


class BaseReport:
    def __init__(self):
        self.now_date = datetime.datetime.now()

    def output(self, content):
        if isinstance(content, Path):
            content = content.read_text()

        data = json.loads(content)

        return data
