import datetime
from textwrap import TextWrapper

import humanize
from tabulate import tabulate

from ..package import PackageRequirement
from .base import BaseReport


class RestructuredTextReport(BaseReport):
    """
    Build a RestructuredText report for a requirements analyze.
    """
    def get_required_release(self, item):
        """
        Return a release labels for a requirement.

        Arguments:
            item (dict): The requirement dictionnary.

        Returns:
            tuple or string: Just string "Latest" if there is not resolved_version,
                else the version label and resolved age delta computed from release
                publish date against date now.
        """
        if not item["resolved_version"]:
            return "Latest"

        resolved_age = humanize.naturaldelta(
            self.now_date - datetime.datetime.fromisoformat(
                item["resolved_published"]
            )
        )
        return item["resolved_version"], resolved_age.capitalize()

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
        rows = []

        for i, item in enumerate(items, start=1):
            lateness = len(item["lateness"]) if item["lateness"] else "-"

            resolved_version = self.get_required_release(item)
            if isinstance(resolved_version, tuple):
                resolved_version = "{} - {} ago".format(*resolved_version)

            # Compute latest release label including humanized delta from current to
            # latest date
            latest_activity = humanize.naturaldelta(
                self.now_date - datetime.datetime.fromisoformat(
                    item["highest_published"]
                )
            )
            latest_release = "{} - {} ago".format(
                item["highest_version"],
                latest_activity.capitalize(),
            )

            # Append column data to the requirement row
            rows.append([
                i,
                item["name"],
                lateness,
                resolved_version,
                latest_release,
            ])

        return str(tabulate(
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
        rows = []
        wrapper = TextWrapper(width=40, max_lines=2, placeholder="")
        default_label = PackageRequirement.STATUS_LABELS["unknown"]

        for i, item in enumerate(items, start=1):
            status = item["status"]

            resume = PackageRequirement.STATUS_LABELS.get(status, default_label)
            if status == "invalid":
                resume += ": {}".format(item["parsing_error"])

            rows.append([
                i,
                wrapper.fill(item["source"]),
                status,
                wrapper.fill(resume),
            ])

        return str(tabulate(
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

    def output(self, content, with_failures=True):
        output = []
        data = super().output(content)

        analyzed_items = [v for v in data if v["status"] == "analyzed"]
        ignored_items = [v for v in data if v["status"] != "analyzed"]

        if with_failures:
            output.append("Analyzed")
            output.append("*" * len("Analyzed"))

        output.append(self.build_analyzed_table(analyzed_items))

        if with_failures:
            output.append("\nFailures")
            output.append("*" * len("Failures"))
            output.append(self.build_errors_table(ignored_items))

        return "\n".join(output)
