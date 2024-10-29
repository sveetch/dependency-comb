from .base import BaseFormatter
from .rich import RichFormatter
from .rst import RestructuredTextFormatter


__all__ = [
    "BaseFormatter",
    "RichFormatter",
    "RestructuredTextFormatter",
]


def output_formatted_content(name, content, printer=print, printer_kwargs=None,
                             destination=None, with_failures=True):
    """
    Helper to output formatted content either with a printer or written to a file.
    """
    printer_kwargs = printer_kwargs or {}

    if name == "rich":
        formatter = RichFormatter()
    else:
        formatter = RestructuredTextFormatter()

    if not destination:
        formatter.print(
            content,
            printer=printer,
            printer_kwargs=printer_kwargs,
            with_failures=with_failures
        )
    else:
        formatter.write(content, destination, with_failures=with_failures)
