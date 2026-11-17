from tabulate import tabulate

from .base import BaseStringFormatter


class RestructuredTextFormatter(BaseStringFormatter):
    """
    Format a requirements analyze to a RestructuredText report.
    """
    def build_analyzed_table(self, items):
        """
        Build the information table for properly analyzed requirements.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. All
                given items should have a status "analyzed".

        Returns:
            string: An ASCII table built from given items.
        """
        results = super().build_analyzed_table(items)

        if not results:
            return

        rows = [
            [
                item["key"],
                item["name"],
                item["lateness"],
                item["resolved_version"],
                item["latest_release"],
            ]
            for item in results
        ]

        head = "Analyzed" + "\n" + ("*" * len("Analyzed")) + "\n\n"

        return head + str(tabulate(
            rows,
            tablefmt="grid",
            headers=[
                "#",
                "Name",
                "Lateness",
                "Required",
                "Latest release",
            ],
            colalign=("left", "left", "center", "right", "right"),
        ))

    def build_duplicates_table(self, items):
        """
        Build the information table for duplicated requirements.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. All
                given items should have a status "duplicated".

        Returns:
            string: An ASCII table built from given items.
        """
        results = super().build_duplicates_table(items)

        if not results:
            return ""

        rows = [
            [
                item["key"],
                (
                    "<string>:{}".format(item["lineno"])
                    if not item["origin"]
                    else "{}:{}".format(item["origin"], item["lineno"])
                ),
                item["name"],
                item["specifier"] or "-",
                item["source"],
            ]
            for item in results
        ]

        head = "\nDuplicated" + "\n" + ("*" * len("Duplicated")) + "\n\n"

        return head + str(tabulate(
            rows,
            tablefmt="grid",
            headers=[
                "#",
                "Origin",
                "Name",
                "Version",
                "Source",
            ],
            colalign=("left", "left", "center", "left"),
        ))

    def build_errors_table(self, items):
        """
        Build the information table for failed requirements analyze.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. Given
                items could have various status except 'analyzed' and 'duplicated'.

        Returns:
            string: An ASCII table built from given items.
        """
        results = super().build_errors_table(items)

        if not results:
            return ""

        rows = [
            [
                item["key"],
                (
                    "<string>:{}".format(item["lineno"])
                    if not item["origin"]
                    else "{}:{}".format(item["origin"], item["lineno"])
                ),
                item["source"],
                item["status"],
                item["resume"],
            ]
            for item in results
        ]

        head = "\nFailures" + "\n" + ("*" * len("Failures")) + "\n\n"

        return head + str(tabulate(
            rows,
            tablefmt="grid",
            headers=[
                "#",
                "Origin",
                "Source",
                "Status",
                "Resume",
            ],
            colalign=("left", "left", "left", "left", "left"),
        ))
