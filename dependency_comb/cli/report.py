import json
import logging
from pathlib import Path

import click

from ..analyzer import DependenciesAnalyzer
from ..exceptions import DependencyCombError
from ..formatting import output_formatted_content
from ..utils.jsons import ExtendedJsonEncoder
from .. import __pkgname__


@click.command()
@click.argument(
    "source",
    type=click.File(),
    default="requirements.txt",
    metavar="SOURCE",
)
@click.option(
    "--cachedir",
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
        resolve_path=True,
    ),
    default=None,
    metavar="DIRPATH",
    help=(
        "A directory where to look for API request cache. It is looked for cache file "
        "per package and if any, avoid any request for a package details. There is not "
        "any mechanic to invalidate or update cache except than to remove cache files. "
        "The given directory path will be created automatically if it does not "
        "exists yet."
    ),
)
@click.option(
    "--format",
    metavar="STRING",
    type=click.Choice(["rst", "rich"]),
    help="Format name.",
    default="rst"
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
    "--chunk",
    type=click.INT,
    default=20,
    help=(
        "Amount of requirements to process in a chunk. Default to 20 requirements per "
        "chunk. If zero, it means every requirements are processed in a single "
        "job without no pause."
    ),
)
@click.option(
    "--pause",
    type=click.INT,
    default=1,
    help=(
        "The time in second to pause before each chunk. Default to 1 second. If zero "
        "it means no pause. Prefer to disable chunk if you don't want any pause."
    ),
)
@click.option(
    "--timeout",
    type=click.INT,
    default=15,
    help=(
        "Timeout in seconds for API requests. The default timeout is set to 15 "
        "seconds, set it to 0 to disable timeout."
    ),
)
@click.option(
    "--env",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
        resolve_path=True,
    ),
    default=None,
    required=False,
    metavar="FILEPATH",
    help=(
        "A JSON file for some environment variables to give to analyzer. This will be "
        "used to resolve specifier markers. If analyzer does not receive any "
        "environment variable all specifier markers are ignored (so its requirement "
        "is always considered valid)."
    ),
)
@click.option(
    "--failures",
    is_flag=True,
    help=(
        "Include requirement analyze failures in a different table, also each table"
        "will have its own title."
    ),
)
@click.pass_context
def report_command(*args, **parameters):
    """
    Analyze and report informations about requirements.

    Opposed to the 'analyze' command, the logs are not muted when there is no
    destination file.

    Arguments:

    \b
    source
        Pip requirements file to parse, analyze and report.
        Instead of a file path you can also give a requirements file content from
        standard input using '-'. For example using the Pip freeze output:

            pip freeze | dependency_comb report -

        Or to make a report for an unique package:

            echo "django==3.2.1" | dependency_comb report -

    """
    logger = logging.getLogger(__pkgname__)

    source = parameters["source"].read()
    # Analyzer opts
    cachedir = parameters["cachedir"]
    destination = parameters["destination"]
    environment = json.loads(parameters["env"].read_text()) if parameters["env"] else {}
    api_chunk = parameters["chunk"] or None
    api_pause = parameters["pause"] or None
    api_timeout = parameters["timeout"] or None
    # Formatter opts
    format_name = parameters["format"]
    with_failures = parameters["failures"]

    # Find the requirement basepath
    if parameters["source"].name == "<stdin>":
        # Since stdin cannot have a basepath like a file we assume the current working
        # directory
        requirement_basepath = Path.cwd()
    else:
        # Resolve basepath from file parent directory
        requirement_basepath = Path(
            parameters["source"].name
        ).parent.resolve()

    logger.debug("Cache directory: {}".format(cachedir))

    # Create cache directory if needed
    if cachedir and not cachedir.exists():
        cachedir.mkdir()

    # Analyze requirements
    try:
        analyzer = DependenciesAnalyzer(
            cachedir=cachedir,
            api_chunk=api_chunk,
            api_pause=api_pause,
            api_timeout=api_timeout,
            logger=logger,
        )
        packages = analyzer.inspect(
            source,
            environment=environment,
            strict=False,
            basepath=requirement_basepath,
        )
        payload = [pkg.data() for pkg in packages]
    except DependencyCombError as e:
        logger.critical(e)
        raise click.Abort()

    # Output formatted content depending format and output method
    output_formatted_content(
        format_name,
        json.dumps(payload, cls=ExtendedJsonEncoder),
        printer=click.echo,
        printer_kwargs={"nl": False},
        destination=destination,
        with_failures=with_failures
    )
    if destination:
        logger.info("Analyze report written to: {}".format(destination))
