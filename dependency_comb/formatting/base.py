import json
from collections import namedtuple

from pathlib import Path
from textwrap import TextWrapper

import click
import humanize

from ..exceptions import FormatterEmptyContentError
from ..models.package import STATUS_LABELS
from ..utils.jsons import ExtendedJsonEncoder


BuiltResults = namedtuple(
    "BuiltResults",
    ["analyzed", "duplicated", "failed"],
    defaults=[[], [], []]
)


class BaseFormatter:
    """
    Base formatter abstract.

    This formatter output Python objects and write them to JSON.

    Formatters intended to output string would rather prefer to inherit from
    ``BaseStringFormatter``.

    Arguments:
        printer (callable): Function to use to print content. The function accept a
            an argument for the content and commonly return a string just like
            ``print()``. On default this will use ``click.echo()``.
        printer_kwargs (dict): Possible kwargs to pass to the printer function.
    """
    def __init__(self, printer=None, printer_kwargs=None):
        self.printer = printer
        self.printer_kwargs = printer_kwargs

    def get_printer_function(self):
        return self.printer or click.echo

    def get_printer_kwargs(self):
        return self.printer_kwargs or None

    def printer_call(self, content):
        """
        Print method wrapper.

        A concrete class may override ``get_printer_function``, ``get_printer_kwargs``,
        ``BaseFormatter.printer`` or ``BaseFormatter.printer`` to set another printer
        function. Default behavior is to use ``Click.echo()``.

        Arguments:
            content (string): Content to print out.
        """
        klass = self.get_printer_function()
        opts = self.get_printer_kwargs()
        if opts:
            klass(content, **opts)
        else:
            klass(content)

    def open_content(self, content):
        """
        Open content, parse it and returns it as a list of requirement dict.

        It is helpful since formatter can receive content to parse from different
        tools.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. It
                can be either:

                * A list that is expected to be directly the list of (dict) analyzed
                  requirements, no JSON parsing is involved. Commonly for some internals
                  like tests that don't work with intermediary JSON content;
                * A file Path that will be readed and parsed as JSON when dump path has
                  to be readen an parsed. Commonly when a processor does not need to
                  open it before;
                * Else it is assumed to be a JSON string to be parsed. Commonly when an
                  analyze dump is already in memory.

        Returns:
            list: The list of all (dict) requirements from given content.
        """
        if isinstance(content, list):
            return content

        if isinstance(content, Path):
            content = content.read_text()

        data = json.loads(content)

        return data

    def get_required_release(self, item):
        """
        Return the release label for a requirement.

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

        # NOTE: Temporary prints until 'delta date' #12 issue is resolved
        # print("💚 get_required_release for:", item["name"])
        # print("  🥚 resolved_version:", item["resolved_version"])
        # print("  🥚 resolved_published:", item["resolved_published"])

        resolved_age = humanize.naturaldelta(item["resolved_delta"])
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
            latest_activity = humanize.naturaldelta(item["highest_delta"])
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
                "latest_activity": latest_activity,
                "release_label": label,
                "release_age": age,
                "lineno": item["lineno"],
                "origin": item["origin"],
            })

        return rows

    def build_duplicates_table(self, items):
        """
        Build a table of duplicated items

        TODO: Item should be ordered. Ever on name then version, or origin then name.
        """
        rows = []

        for i, item in enumerate(items, start=1):
            rows.append({
                "key": i,
                "name": item["name"],
                "source": item["source"],
                "specifier": item["specifier"],
                "lineno": item["lineno"],
                "origin": item["origin"],
            })

        return rows

    def build_errors_table(self, items):
        """
        Build the information table for failed requirements analyze.

        Because failures can have some long string (url, error reason, etc..), source
        and resume are wrapped on two lines if they are over 40 characters, it means
        a string of +80 characters will be cut to 80.

        Arguments:
            items (list): List of requirement (dict) as returned from Analyzer and
            already filtered to only include failures.

        Returns:
            list: A list of dictionnaries for each processed items. Dict items
            ``source`` and ``resume`` will be wrapped to fit on line of 40 characters
            max and only for two lines (all other lines are replaced with an elipsis).
        """
        rows = []
        wrapper = TextWrapper(width=40, max_lines=2, placeholder="")
        default_label = STATUS_LABELS["unknown"]

        for i, item in enumerate(items, start=1):
            status = item["status"]

            resume = STATUS_LABELS.get(status, default_label)
            if status == "invalid":
                resume += ": {}".format(item["parsing_error"])

            rows.append({
                "key": i,
                "source": wrapper.fill(item["source"]),
                "status": status,
                "resume": wrapper.fill(resume),
                "lineno": item["lineno"],
                "origin": item["origin"],
            })

        return rows

    def build(self, content, with_failures=True, with_duplicates=True):
        """
        Build 'succeeds' and 'failures' payloads of analyze for concrete formatter
        method.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To enable display of failures.
            with_duplicates (boolean): To enable display of duplicates.

        Return:
            namedtuple: With items analyzed, duplicated and failed. Alls are lists.
        """
        data = self.open_content(content)

        # NOTE: This is not efficient as it could be since we iterate again the same
        # list for each kind of table
        results = BuiltResults(
            analyzed=self.build_analyzed_table(
                [v for v in data if v["status"] == "analyzed"]
            ),
            duplicated=(
                []
                if with_duplicates is False
                else self.build_duplicates_table(
                    [v for v in data if v["status"] == "duplicated"]
                )
            ),
            failed=(
                []
                if with_failures is False
                else self.build_errors_table(
                    [v for v in data if v["status"] not in ("analyzed", "duplicated")]
                )
            )
        )

        if not results.analyzed and not results.failed:
            raise FormatterEmptyContentError("There was no data to format.")

        return results

    def print(self, content, with_failures=True, with_duplicates=True,
              **kwargs):
        """
        Print out the analyzed and possibly failures.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.
            with_duplicates (boolean): To enable display of duplicates.
        """
        results = self.build(
            content,
            with_failures=with_failures,
            with_duplicates=with_duplicates
        )

        if results.analyzed:
            self.printer_call(results.analyzed)

        if results.failed:
            self.printer_call(results.failed)

        if results.duplicated:
            self.printer_call(results.duplicated)

    def write(self, content, destination, with_failures=True, with_duplicates=True,
              **kwargs):
        """
        Write the analyzed and possibly failures into destination file.

        Written content will be a list of lists, where each list is a part of
        analyze (analyzed, duplicated, failed). Part list will contain their serialized
        items.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.
            with_duplicates (boolean): To enable display of duplicates.

        Return:
            Path: Path of created file.
        """
        results = self.build(
            content,
            with_failures=with_failures,
            with_duplicates=with_duplicates
        )

        # Base output type adjust to 'content' type to fit different formatter
        output = []

        if results.analyzed:
            output.extend(results.analyzed)

        if results.failed:
            output.extend(results.failed)

        if results.duplicated:
            output.extend(results.duplicated)

        # Write merged contents
        destination.write_text(json.dumps(output, cls=ExtendedJsonEncoder))

        return destination


class BaseStringFormatter(BaseFormatter):
    """
    Alternative base formatter where content is assumed to be written as a string.

    This is commonly the one to inherit because BaseFormatter is intended for
    formatters that need to conserve Python objects.
    """
    def write(self, content, destination, with_failures=True, with_duplicates=True,
              **kwargs):
        """
        Write the analyzed and possibly failures into destination file.

        Arguments:
            content (Path or string or list): JSON content as built from Analyzer. See
                ``BaseFormatter.open_content()`` doc for more details.

        Keyword Arguments:
            with_failures (boolean): To disable display of failures.
            with_duplicates (boolean): To enable display of duplicates.

        Return:
            Path: Path of created file.
        """
        results = self.build(
            content,
            with_failures=with_failures,
            with_duplicates=with_duplicates
        )

        # Base output type adjust to 'content' type to fit different formatter
        output = []

        if results.analyzed:
            output.append(results.analyzed)

        if results.failed:
            output.append(results.failed)

        if results.duplicated:
            output.append(results.duplicated)

        # Write merged contents
        destination.write_text("\n".join(output))

        return destination
