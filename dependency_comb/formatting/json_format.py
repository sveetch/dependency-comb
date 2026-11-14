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

    def build(self, content, with_failures=True, with_duplicates=True):
        """
        Build dictionnary of analyzed and possibles failures

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.

        """
        results = super().build(content, with_failures=with_failures, with_duplicates=with_duplicates)

        return {
            "analyzed": results.analyzed,
            #TODO
            #"duplicated": results.duplicated,
            "failures": results.failed,
        }

    def print(self, content, with_failures=True, with_duplicates=True):
        """
        Print out the analyzed and possibly failures

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.
        """
        self.printer_call(
            json.dumps(self.build(content, with_failures=with_failures, with_duplicates=with_duplicates), indent=4)
        )

    def write(self, content, destination, with_failures=True, with_duplicates=True):
        """
        Write the analyzed and possibly failures into destination file.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.

        Return:
            Path: Path of created file.
        """
        destination.write_text(
            json.dumps(self.build(content, with_failures=with_failures, with_duplicates=with_duplicates))
        )

        return destination
