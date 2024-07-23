import json

from pathlib import Path


class BaseReport:
    def __init__(self):
        pass

    def output(self, content):
        if isinstance(content, Path):
            content = content.read_text()

        data = json.loads(content)

        return data
