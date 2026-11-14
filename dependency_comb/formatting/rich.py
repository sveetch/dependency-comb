from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.console import Group

from .base import BaseStringFormatter


class RichFormatter(BaseStringFormatter):
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
            rich.table.Table: A Rich table object with successful requirement analyzes.
        """
        results = super().build_analyzed_table(items)

        if not results:
            return None

        table = Table(
            "#",
            "Name",
            "Lateness",
            "Required",
            "Latest release",
            box=box.MINIMAL_HEAVY_HEAD,
        )

        for item in results:
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
            rich.table.Table: A Rich table object with failed requirement analyzes.
        """
        results = super().build_errors_table(items)

        if not results:
            return None

        table = Table(
            "#",
            "Source",
            "Status",
            "Resume",
            box=box.MINIMAL_HEAVY_HEAD,
        )

        for item in results:
            table.add_row(
                str(item["key"]),
                item["source"],
                item["status"],
                item["resume"],
            )

        return table

    def print(self, content, destination=None, with_failures=True,
              with_duplicates=True):
        """
        Print out the analyzed and possible failures

        TODO: Console width should not be hardcoded

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.
        """
        results = self.build(content, with_failures=with_failures, with_duplicates=with_duplicates)

        console = Console(width=300, file=destination)
        group_items = []

        if results.analyzed:
            group_items.append(Padding("", (1, 2), expand=False))
            group_items.append(
                Panel(results.analyzed, title="[green]Analyzed[/green]", expand=False)
            )

        if results.failed:
            group_items.append(Padding("", (1, 2), expand=False))
            group_items.append(
                Panel(results.failed, title="[red]Failures[/red]", expand=False)
            )

        #if results.duplicated:
            #group_items.append(Padding("", (1, 2), expand=False))
            #group_items.append(
                #Panel(results.duplicated, title="[orange]Failures[/orange]", expand=False)
            #)

        panel_group = Group(*group_items)
        console.print(panel_group)

        return console

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
        self.print(
            content,
            destination=destination.open("w"),
            with_failures=with_failures,
            with_duplicates=with_duplicates
        )

        return destination
