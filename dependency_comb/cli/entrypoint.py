"""
Main entrance to commandline actions
"""
import click

from ..utils.logger import init_logger

from .version import version_command
from .analyze import analyze_command
from .formatter import format_command
from .report import report_command


# Help alias on "-h" argument
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


# Default logger conf
APP_LOGGER_CONF = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", None)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-v", "--verbose",
    type=click.IntRange(min=0, max=5),
    default=4,
    metavar="INTEGER",
    help=(
        "An integer between 0 and 5, where '0' make a totaly "
        "silent output and '5' set level to DEBUG (the most verbose "
        "level). Default to '4' (Info level)."
    )
)
@click.pass_context
def cli_frontend(ctx, verbose):
    """
    dependency-comb commandline entrypoint.
    """
    printout = True
    if verbose == 0:
        verbose = 1
        printout = False

    # Verbosity is the inverse of logging levels
    levels = [item for item in APP_LOGGER_CONF]
    levels.reverse()
    # Init the logger config
    root_logger = init_logger(
        "dependency-comb",
        levels[verbose],
        printout=printout
    )

    # Init the default context that will be passed to commands
    ctx.obj = {
        "verbosity": verbose,
        "logger": root_logger,
    }


# Attach commands methods to the main grouper
cli_frontend.add_command(version_command, name="version")
cli_frontend.add_command(analyze_command, name="analyze")
cli_frontend.add_command(format_command, name="format")
cli_frontend.add_command(report_command, name="report")
