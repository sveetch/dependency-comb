import csv
from io import StringIO


from .base import BaseStringFormatter


class CSVFormatter(BaseStringFormatter):
    """
    Format a requirements analyze to a report made with Rich library.
    """
    def build_analyzed_table(self, items):
        """
        Build the information table for properly analyzed requirements.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. All
                given items should have a status "analyzed" else it would lead to
                unexpected results or even errors.

        Returns:
            string:
        """
        payload = StringIO()

        data = super().build_analyzed_table(items)

        if not data:
            return

        table = csv.DictWriter(
            payload,
            fieldnames=data[0].keys(),
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            dialect=csv.unix_dialect,
        )

        table.writeheader()
        for item in data:
            table.writerow(item)

        return payload.getvalue()

    def build_errors_table(self, items):
        """
        Build the information table for failed requirements analyze.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. Given
                items could have any status despite not very useful for properly
                analyzed items.

        Returns:
            string:
        """
        payload = StringIO()

        data = super().build_errors_table(items)

        if not data:
            return

        table = csv.DictWriter(
            payload,
            fieldnames=data[0].keys(),
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            dialect=csv.unix_dialect,
        )

        table.writeheader()
        for item in data:
            table.writerow(item)

        return payload.getvalue()
