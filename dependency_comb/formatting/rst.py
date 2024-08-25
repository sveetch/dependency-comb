import datetime
from textwrap import TextWrapper

import humanize
from tabulate import tabulate

from ..package import PackageRequirement
from .base import BaseFormatter


class RestructuredTextFormatter(BaseFormatter):
    """
    Format a requirements analyze to a RestructuredText report.
    """
    def get_required_release(self, item):
        """
        Return a release labels for a requirement.

        Arguments:
            item (dict): The requirement dictionnary.

        Returns:
            tuple: Respectively the version label and resolved age delta
                computed from release publish date against date now. If
                ``resolved_version`` is empty, the version label will just be
                ``Latest`` and resolved delta will be null.
        """
        if not item["resolved_version"]:
            return "Latest", None

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

            label, age = self.get_required_release(item)
            if age:
                resolved_version = "{} - {} ago".format(label, age)
            else:
                resolved_version = label

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

        if with_failures:
            output.append("Analyzed")
            output.append("*" * len("Analyzed"))

        output.append(self.build_analyzed_table(analyzed_items))

        if with_failures:
            output.append("\nFailures")
            output.append("*" * len("Failures"))
            output.append(self.build_errors_table(ignored_items))

        return "\n".join(output)
