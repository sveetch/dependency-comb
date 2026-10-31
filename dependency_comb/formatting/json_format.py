import json

from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """
    Format a requirements analyze to a JSON report.

    .. Note::
        Opposed to other formatters, this one won't raise error if there was not any
        data from analyze or failure. 'analyzed' and 'failures' are always in returned
        JSON object even if they are empty.
    """

    def build(self, content, with_failures=True):
        """
        Build dictionnary of analyzed and possibles failures
        """
        succeeds, failures = super().build(content, with_failures=with_failures)

        return {
            "analyzed": succeeds,
            "failures": failures,
        }

    def print(self, content, with_failures=True):
        """
        Print out the analyzed and possibly failures
        """
        self.printer_call(
            json.dumps(self.build(content, with_failures=with_failures), indent=4)
        )

    def write(self, content, destination, with_failures=True):
        """
        Write the analyzed and possibly failures into destination file.
        """
        destination.write_text(
            json.dumps(self.build(content, with_failures=with_failures))
        )

        return destination
