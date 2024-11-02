from .base import BaseFormatter
from .csv import CSVFormatter
from .json_format import JSONFormatter
from .rich import RichFormatter
from .rst import RestructuredTextFormatter


__all__ = [
    "BaseFormatter",
    "CSVFormatter",
    "JSONFormatter",
    "RichFormatter",
    "RestructuredTextFormatter",
]


DEFAULT_FORMAT = "rst"


AVAILABLE_FORMATS = {
    "csv": CSVFormatter,
    "json": JSONFormatter,
    "rst": RestructuredTextFormatter,
    "rich": RichFormatter,
}


def output_formatted_content(name, content, printer=None, printer_kwargs=None,
                             destination=None, with_failures=True):
    """
    Helper to output formatted content either with a printer or written to a file.
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
