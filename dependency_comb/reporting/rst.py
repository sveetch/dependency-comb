import datetime

import humanize
from tabulate import tabulate

from .base import BaseReport


class RestructuredTextReport(BaseReport):
    def get_required_release(self, item):
        if not item["resolved_version"]:
            return "Latest"

        resolved_age = humanize.naturaldelta(
            self.now_date - datetime.datetime.fromisoformat(
                item["resolved_published"]
            )
        )
        return item["resolved_version"], resolved_age.capitalize()

    def build_analyzed_table(self, items):
        rows = []

        for item in items:
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
                item["name"],
                lateness,
                resolved_version,
                latest_release,
            ])

        return str(tabulate(
            rows,
            tablefmt="grid",
            headers=[
                "Name",
                "Lateness",
                "Required",
                "Latest release",
            ],
            showindex="always",
            colalign=("center", "left", "center", "right", "right"),
        ))

    def output(self, content):
        data = super().output(content)

        analyzed_items = [v for v in data if v["status"] == "analyzed"]
        ignored_items = [v for v in data if v["status"] != "analyzed"]

        print("analyzed_items", len(analyzed_items))
        print("ignored_items", len(ignored_items))

        analyzed_output = self.build_analyzed_table(analyzed_items)
        #print()
        #print(analyzed_output)
        #print()

        # TODO: Make the ignored report that should be a different table structure
        # with different informations

        return data
