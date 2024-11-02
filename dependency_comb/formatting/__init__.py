from .base import BaseFormatter
from .rich import RichFormatter
from .rst import RestructuredTextFormatter


__all__ = [
    "BaseFormatter",
    "RichFormatter",
    "RestructuredTextFormatter",
]


def output_formatted_content(name, content, printer=None, printer_kwargs=None,
                             destination=None, with_failures=True):
    """
    Helper to output formatted content either with a printer or written to a file.
    """
    if name == "rich":
        formatter = RichFormatter(
            printer=printer,
            printer_kwargs=printer_kwargs,
        )
    else:
        formatter = RestructuredTextFormatter(
            printer=printer,
            printer_kwargs=printer_kwargs,
        )

    if not destination:
        formatter.print(content, with_failures=with_failures)
    else:
        formatter.write(content, destination, with_failures=with_failures)
