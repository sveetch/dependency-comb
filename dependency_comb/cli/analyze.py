import json
import logging
from pathlib import Path

import click

from ..analyzer import DependenciesAnalyzer
from ..exceptions import DependencyCombError
from ..utils.jsons import ExtendedJsonEncoder
from ..utils.logger import NoOperationLogger
from .. import __pkgname__


@click.command()
@click.argument(
    "source",
    type=click.File(),
    default="requirements.txt",
    metavar="SOURCE",
)
@click.option(
    "--filekey",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
        resolve_path=True,
    ),
    default="librariesio-key.txt",
    metavar="FILEPATH",
    help=(
        "A simple text file which only contains the Libraries.io API key to use "
        "to request the API. It is required since API is restricted. Default to "
        "'librariesio-key.txt'."
    ),
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
    "--indent",
    type=click.INT,
    default=4,
    help=(
        "Indentation level for JSON output. Default to 4 spaces."
    ),
)
@click.option(
    "--pause",
    type=click.INT,
    default=1,
    help=(
        "The time in second to pause before an API requests. Default to 1 second "
        "that should be enough to follow the Libraries.io rate limit for a free "
        "account. *DO NOT* set it to zero if you don't own an API key suitable to "
        "override the API rate limit or you may be blocked."
    ),
)
@click.option(
    "--timeout",
    type=click.INT,
    default=15,
    help=(
        "Timeout in seconds for API requests. Sometime Libraries.io is unresponsive "
        "and the request may hang almost infinitely so this option may avoid this."
        "The default timeout is set to 15 seconds, set it to 0 to disable timeout."
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
@click.pass_context
def analyze_command(*args, **parameters):
    """
    Analyze package releases from a requirements file and output computed statistics
    as JSON.

    Arguments:

    \b
    source
        Pip requirements file to parse and analyze.
        Instead of a file path you can also give a requirements file content from
        standard input using '-'. For example using the Pip freeze output:

            pip freeze | dependency_comb analyze -

        Or to analyze an unique package:

            echo "django==3.2.1" | dependency_comb analyze -

    """
    logger = logging.getLogger(__pkgname__)

    source = parameters["source"].read()
    filekey = parameters["filekey"]
    cachedir = parameters["cachedir"]
    destination = parameters["destination"]
    environment = json.loads(parameters["env"].read_text()) if parameters["env"] else {}
    indent = parameters["indent"] or None
    api_pause = parameters["pause"] or None
    api_timeout = parameters["timeout"] or None

    # Disable logger when writing results to standard output
    if not destination:
        logger = NoOperationLogger()

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

    logger.debug("API file key: {}".format(filekey))
    logger.debug("Cache directory: {}".format(cachedir))

    # Read API key
    api_key = filekey.read_text()

    # Create cache directory if needed
    if cachedir and not cachedir.exists():
        cachedir.mkdir()

    # Analyze requirements
    try:
        analyzer = DependenciesAnalyzer(
            api_key,
            cachedir=cachedir,
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

    # Build output
    output = json.dumps(payload, indent=indent, cls=ExtendedJsonEncoder)

    if not destination:
        click.echo(output)
    else:
        destination.write_text(output)
