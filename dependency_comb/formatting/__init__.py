from .base import BaseFormatter
from .csv import CSVFormatter
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
    "CSVFormatter",
    "JSONFormatter",
    "RestructuredTextFormatter",
    "RichFormatter",
]


# Build default and available formatters
DEFAULT_FORMAT = "rst"

AVAILABLE_FORMATS = {
    "csv": CSVFormatter,
    "json": JSONFormatter,
    "rst": RestructuredTextFormatter,
}

# If Rich is enabled, formatter is available and become the default one
if RICH_ENABLED is True:
    AVAILABLE_FORMATS["rich"] = RichFormatter


def output_formatted_content(name, content, printer=None, printer_kwargs=None,
                             destination=None, with_failures=True):
    """
    Helper function to output formatted content either with a printer or written to a
    file.
    """
    if name not in AVAILABLE_FORMATS:
        raise ValueError("Given formatter name is unknowed: {}".format(name))

    formatter = AVAILABLE_FORMATS[name](
        printer=printer,
        printer_kwargs=printer_kwargs,
    )

    if not destination:
        formatter.print(content, with_failures=with_failures)
    else:
        formatter.write(content, destination, with_failures=with_failures)
