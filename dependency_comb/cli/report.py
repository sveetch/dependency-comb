import logging
from pathlib import Path

import click

from .. import __pkgname__


@click.command()
@click.argument(
    "source",
    type=click.File(),
    default="requirements.txt",
    metavar="SOURCE",
)
@click.option(
    "--destination",
    type=click.Path(
        file_okay=True, dir_okay=False, resolve_path=False, path_type=Path,
    ),
    help=(
        "File path destination where to write serialized JSON manifest. If not given "
        "the JSON will be sent to standard output."
    ),
)
@click.pass_context
def report_command(*args, **parameters):
    """
    Build a report from requirements analyze.

    Arguments:

    \b
    source
        Computed analyze in a JSON file path. Instead of a file path you can also give
        a requirements file content from standard input using '-'. For example:

            dependency_comb analyze requirements.txt | dependency_comb report -
    """
    logger = logging.getLogger(__pkgname__)

    source = parameters["source"].read()  # noqa: F841
    destination = parameters["destination"]  # noqa: F841

    logger.info("TODO")
