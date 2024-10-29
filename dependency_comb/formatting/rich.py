import json

from pathlib import Path
from textwrap import TextWrapper

import humanize

from rich import box
from rich.panel import Panel
from rich.table import Table

from ..package import PackageRequirement
from ..utils.dates import safe_isoformat_parse
from .base import BaseFormatter


class RichFormatter(BaseFormatter):
    """
    Base formatter just defines some internal attributes and return Python object from
    given JSON.

    Arguments:
        now_date (datetime): A datetime to set instead of default ``datetime.now()``.
            This datetime is used to compute the delta time between release and current
            date.
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
        main_table = Table(
            "#",
            "Name",
            "Lateness",
            "Required",
            "Latest release",
            box=box.MINIMAL_HEAVY_HEAD,
            #leading=True
        )

        for i, item in enumerate(items, start=1):
            lateness = str(len(item["lateness"])) if item["lateness"] else "-"

            label, age = self.get_required_release(item)
            if age:
                resolved_version = "{} - {} ago".format(label, age)
            else:
                resolved_version = label

            # Compute latest release label including humanized delta from current to
            # latest date
            latest_activity = humanize.naturaldelta(
                self.now_date - safe_isoformat_parse(item["highest_published"])
            )
            latest_release = "{} - {} ago".format(
                item["highest_version"],
                latest_activity.capitalize(),
            )

            # Append column data to the requirement row
            main_table.add_row(
                str(i),
                item["name"],
                lateness,
                resolved_version,
                latest_release,
            )

        return Panel.fit(main_table, title="Analyzed")

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
        main_table = Table(
            "#",
            "Source",
            "Status",
            "Resume",
            box=box.MINIMAL_HEAVY_HEAD,
            leading=True
        )

        rows = []
        wrapper = TextWrapper(width=40, max_lines=2, placeholder="")
        default_label = PackageRequirement.STATUS_LABELS["unknown"]

        for i, item in enumerate(items, start=1):
            status = item["status"]

            resume = PackageRequirement.STATUS_LABELS.get(status, default_label)
            if status == "invalid":
                resume += ": {}".format(item["parsing_error"])

            main_table.add_row(
                str(i),
                wrapper.fill(item["source"]),
                status,
                wrapper.fill(resume),
            )

        return Panel.fit(main_table, title="Failures")

    def output(self, content, with_failures=True):
        """
        Output formatted analyze.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. It
                can be either:

                * A JSON as a string that will be parsed;
                * A file Path that will be readed and parsed as JSON;
                * A list that is expected to be directly the list of analyzed
                  requirements, no parsing will be involved.
            with_failures (boolean): If True, the report include both analyzed and
                failures in different tables, both tables will have a title. If False,
                only the table of analyzed items without a title.

        Returns:
            string: Built report.
        """
        data = super().output(content)
        output = []

        analyzed_items = [v for v in data if v["status"] == "analyzed"]
        ignored_items = [v for v in data if v["status"] != "analyzed"]

        from rich import print
        success_output = self.build_analyzed_table(analyzed_items)
        print(success_output)

        if with_failures:
            failures_output = self.build_errors_table(ignored_items)
            print(failures_output)

        return None
