import logging
from pathlib import Path

import click

from ..utils.logger import NoOperationLogger
from ..formatting import DEFAULT_FORMAT, AVAILABLE_FORMATS, output_formatted_content
from .. import __pkgname__


@click.command()
@click.argument(
    "source",
    type=click.File(),
    default="requirements.txt",
    metavar="SOURCE",
)
@click.option(
    "--format",
    metavar="STRING",
    type=click.Choice(AVAILABLE_FORMATS.keys()),
    help="Format name.",
    default=DEFAULT_FORMAT,
    show_default=True,
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
@click.option(
    "--failures/--no-failures",
    is_flag=True,
    default=True,
    help=(
        "Include requirement analyze failures in a different table, also each table"
        "will have its own title."
    ),
)
@click.pass_context
def format_command(*args, **parameters):
    """
    Format an existing analyze.

    Analyze is expected to be a valid JSON as outputted from 'analyze' command.

    Arguments:

    \b
    SOURCE
        Computed analyze in a JSON file path. Instead of a file path you can also give
        a requirements file content from standard input using '-'. For example:

            dependency_comb analyze requirements.txt | dependency_comb report -
    """
    logger = logging.getLogger(__pkgname__)

    source = parameters["source"].read()
    destination = parameters["destination"]
    format_name = parameters["format"]
    with_failures = parameters["failures"]

    # Disable logger when writing results to standard output
    if not destination:
        logger = NoOperationLogger()

    # Output formatted content depending format and output method
    output_formatted_content(
        format_name,
        source,
        destination=destination,
        with_failures=with_failures
    )

    if destination:
        logger.info("Formatted analyze to: {}".format(destination))
