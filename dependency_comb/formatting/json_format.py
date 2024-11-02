import json

from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """
    Format a requirements analyze to a JSON report.
    """

    def build(self, content, with_failures=True):
        """
        Build dictionnary of analyzed and possibles failures
        """
        data = self.output(content)

        payload = {}

        payload["analyzed"] = self.build_analyzed_table(data)

        if with_failures:
            payload["failures"] = self.build_errors_table(data)

        return payload

    def print(self, content, with_failures=True):
        """
        Print out the analyzed and possibly failures
        """
        self.printer_call(json.dumps(self.build(content), indent=4))

    def write(self, content, destination, with_failures=True):
        """
        Write the analyzed and possibly failures into destination file.
        """
        destination.write_text(json.dumps(self.build(content)))

        return destination
