from textwrap import TextWrapper

import humanize
from tabulate import tabulate

from ..package import PackageRequirement
from ..utils.dates import safe_isoformat_parse
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
                given items should have a status "analyzed" else it would lead to
                unexpected results or even errors.

        Returns:
            string: An ASCII table built from given items.
        """
        rows = [
            [
                item["key"],
                item["name"],
                item["lateness"],
                item["resolved_version"],
                item["latest_release"],
            ]
            for item in super().build_analyzed_table(items)
        ]

        head = "Analyzed" + "\n" + ("*" * len("Analyzed")) + "\n"
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

    def build_errors_table(self, items):
        """
        Build the information table for failed requirements analyze.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. Given
                items could have any status despite not very useful for properly
                analyzed items.

        Returns:
            string: An ASCII table built from given items.
        """
        rows = [
            [
                item["key"],
                item["source"],
                item["status"],
                item["resume"],
            ]
            for item in super().build_errors_table(items)
        ]

        if not rows:
            return ""

        head = "\nFailures" + "\n" + ("*" * len("Failures")) + "\n"
        return head + str(tabulate(
            rows,
            tablefmt="grid",
            headers=[
                "#",
                "Source",
                "Status",
                "Resume",
            ],
            colalign=("left", "left", "center", "left"),
        ))
