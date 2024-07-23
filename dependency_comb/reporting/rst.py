from tabulate import tabulate

from .base import BaseReport


class RestructuredTextReport(BaseReport):
    def build_analyzed_table(self, items):
        rows = []

        for item in items:
            lateness = len(item["lateness"]) if item["lateness"] else "-"
            resolved_version = item["resolved_version"] or "Latest"
            latest_release = "{} - {} ago".format(
                item["highest_version"],
                item["latest_activity"].capitalize(),
            )
            rows.append([item["name"], lateness, resolved_version, latest_release])

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
            colalign=("center", "left", "center", "center", "right"),
        ))

    def output(self, content):
        data = super().output(content)

        analyzed_items = [v for v in data if v["status"] == "analyzed"]
        ignored_items = [v for v in data if v["status"] != "analyzed"]

        print("analyzed_items", len(analyzed_items))
        print("ignored_items", len(ignored_items))

        analyzed_output = self.build_analyzed_table(analyzed_items)
        print()
        print(analyzed_output)
        print()

        # TODO: Make the ignored report that should be a different table structure
        # with different informations

        return data
