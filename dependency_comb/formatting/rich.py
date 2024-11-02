import json
from io import StringIO
from pathlib import Path
from textwrap import TextWrapper

import humanize

from rich import box, print as rich_print
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table, Column
from rich.console import Group

from ..package import PackageRequirement
from ..utils.dates import safe_isoformat_parse
from .base import BaseStringFormatter


class RichFormatter(BaseStringFormatter):
    """
    Format a requirements analyze to a report made with Rich library.
    """
    def get_printer_function(self):
        return self.printer or rich_print

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
        table = Table(
            "#",
            "Name",
            "Lateness",
            "Required",
            "Latest release",
            box=box.MINIMAL_HEAVY_HEAD,
        )


        for item in super().build_analyzed_table(items):
            table.add_row(
                str(item["key"]),
                item["name"],
                str(item["lateness"]),
                item["resolved_version"],
                item["latest_release"],
            )

        return table

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
        table = Table(
            "#",
            "Source",
            "Status",
            "Resume",
            box=box.MINIMAL_HEAVY_HEAD,
        )

        for item in super().build_errors_table(items):
            table.add_row(
                str(item["key"]),
                item["source"],
                item["status"],
                item["resume"],
            )

        return table

    def print(self, content, destination=None, with_failures=True):
        """
        Print out the analyzed and possible failures
        """
        data = self.output(content)
        console = Console(width=100, file=destination)
        group_items = []

        analyzed_table = self.build_analyzed_table(data)
        group_items.append(Padding("", (1, 2), expand=False))
        group_items.append(Panel(analyzed_table, title="[green]Analyzed[/green]"))


        if with_failures:
            failures = self.build_errors_table(data)
            group_items.append(Padding("", (1, 2), expand=False))
            group_items.append(Panel(failures, title="[dark_orange3]Failures[/dark_orange3]"))

        panel_group = Group(*group_items)
        console.print(panel_group)

        return console

    def write(self, content, destination, with_failures=True):
        """
        Write the analyzed and possibly failures into destination file.
        """
        console = self.print(
            content,
            destination=destination.open("w"),
            with_failures=with_failures
        )

        return destination
