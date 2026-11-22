from .base import BaseFormatter
from .json_format import JSONFormatter
from .rst import RestructuredTextFormatter


# Manage optional Rich formatter
from ..compat.rich_support import RICH_ENABLED

if RICH_ENABLED is True:
    from .rich import RichFormatter
else:
    RichFormatter = None


__all__ = [
    "BaseFormatter",
    "JSONFormatter",
    "RestructuredTextFormatter",
    "RichFormatter",
]


# Build default and available formatters
DEFAULT_FORMAT = "rst"

AVAILABLE_FORMATS = {
    "json": JSONFormatter,
    "rst": RestructuredTextFormatter,
}

# If Rich is enabled, formatter is available and become the default one
if RICH_ENABLED is True:
    AVAILABLE_FORMATS["rich"] = RichFormatter


def output_formatted_content(format_name, content, printer=None, printer_kwargs=None,
                             destination=None, statistics=None, **kwargs):
    """
    Helper function to output formatted content either with a printer or written to a
    file.

    Arguments:
        format_name (string): Keyword name of formatter, it must be an existing entry
            from ``AVAILABLE_FORMATS``.
            content (list): List of PackageRequirement objects as built from Analyzer.

    Keyword Arguments:
        printer (function): Custom function to print out formatted content. It will use
            the default printer if not given.
        printer_kwargs (dict): Dict of keyword arguments to pass to printer function.
        destination (Path): Path object to a file where to write formatted content. If
            given, content won't be print out.
        statistics (dict): A dictionnary of computed analyzer inspection statistics.
    """
    if format_name not in AVAILABLE_FORMATS:
        raise ValueError("Given formatter name is unknown: {}".format(format_name))

    # Init the right formatter
    formatter = AVAILABLE_FORMATS[format_name](
        printer=printer,
        printer_kwargs=printer_kwargs,
    )

    # Use print if no destination was given, else write formatter output to the given
    # destination
    if not destination:
        formatter.print(content, **kwargs)
    else:
        formatter.write(content, destination, **kwargs)
