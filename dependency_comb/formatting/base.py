import datetime
import json

from pathlib import Path
from textwrap import TextWrapper

import humanize

from ..package import PackageRequirement
from ..utils.dates import safe_isoformat_parse


class BaseFormatter:
    """
    Base formatter just defines some internal attributes and return Python object from
    given JSON.

    Arguments:
        now_date (datetime): A datetime to set instead of default ``datetime.now()``.
            This datetime is used to compute the delta time between release and current
            date.
    """
    def __init__(self, now_date=None):
        self.now_date = now_date or datetime.datetime.now()

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
            self.now_date - safe_isoformat_parse(item["resolved_published"])
        )
        return item["resolved_version"], resolved_age.capitalize()

    def build_analyzed_table(self, items):
        """
        Build the information table for properly analyzed requirements.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. Only
                items with status ``analyzed`` are processed here and all other status
                items are ignored.

        Returns:
            list: A list of dictionnaries for each processed items.
        """
        analyzed_items = [v for v in items if v["status"] == "analyzed"]

        rows = []

        for i, item in enumerate(analyzed_items, start=1):
            lateness = len(item["lateness"]) if item["lateness"] else "-"

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
            rows.append({
                "key": i,
                "name": item["name"],
                "lateness": lateness,
                "resolved_version": resolved_version,
                "latest_release": latest_release,
            })

        return rows

    def build_errors_table(self, items):
        """
        Build the information table for failed requirements analyze.

        Arguments:
            items (list): List of requirement dict as returned from Analyzer. All items
                are processed except the ones with status ``analyzed``.

        Returns:
            list: A list of dictionnaries for each processed items.
        """
        ignored_items = [v for v in items if v["status"] != "analyzed"]

        rows = []
        wrapper = TextWrapper(width=40, max_lines=2, placeholder="")
        default_label = PackageRequirement.STATUS_LABELS["unknown"]

        for i, item in enumerate(ignored_items, start=1):
            status = item["status"]

            resume = PackageRequirement.STATUS_LABELS.get(status, default_label)
            if status == "invalid":
                resume += ": {}".format(item["parsing_error"])

            rows.append({
                "key": i,
                "source": wrapper.fill(item["source"]),
                "status": status,
                "resume": wrapper.fill(resume),
            })

        return rows

    def output(self, content):
        """
        Parse given content and returns it as a Python list.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. It
                can be either:

                * A string assumed as JSON to be parsed;
                * A file Path that will be readed and parsed as JSON;
                * A list that is expected to be directly the list of (dict) analyzed
                  requirements, no parsing will be involved.

        Returns:
            list: The list of all (dict) requirements from given content.
        """
        if isinstance(content, list):
            return content

        if isinstance(content, Path):
            content = content.read_text()

        data = json.loads(content)

        return data

    def print(self, content, with_failures=True, printer=print):
        """
        TODO: Print out the analyzed and possibly failures
        """
        data = self.output(content)

        success_output = self.build_analyzed_table(data)
        printer(success_output)

        if with_failures:
            failures_output = self.build_errors_table(data)
            printer(failures_output)

    def write(self, content, destination, with_failures=True):
        """
        TODO: Write the analyzed and possibly failures into destination file.
        """
        data = self.output(content)

        success_output = self.build_analyzed_table(data)
        output = success_output

        if with_failures:
            failures_output = self.build_errors_table(data)
            output += failures_output

        # Write merged built lists as JSON
        destination.write_text(json.dumps(output))

        return destination
