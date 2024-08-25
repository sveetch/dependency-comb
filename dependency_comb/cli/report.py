import logging
from pathlib import Path

import click

from ..utils.logger import NoOperationLogger
from ..reporting import RestructuredTextReport
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
@click.option(
    "--failures",
    is_flag=True,
    help=(
        "Commit the purge."
    ),
)
@click.pass_context
def report_command(*args, **parameters):
    """
    Build a report from a requirement analyze.

    Analyze is expected to be a valid JSON as outputted from 'analyze' command.

    Arguments:

    \b
    source
        Computed analyze in a JSON file path. Instead of a file path you can also give
        a requirements file content from standard input using '-'. For example:

            dependency_comb analyze requirements.txt | dependency_comb report -
    """
    logger = logging.getLogger(__pkgname__)

    source = parameters["source"].read()
    destination = parameters["destination"]
    with_failures = parameters["failures"]

    reporter = RestructuredTextReport()
    output = reporter.output(source, with_failures=with_failures)

    if not destination:
        click.echo(output)
    else:
        destination.write_text(output)
        logger.info("Written report to: {}".format(destination))
