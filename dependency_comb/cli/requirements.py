import logging
from pathlib import Path

import click

from .. import __pkgname__
from ..analyzer import DependenciesAnalyzer


@click.command()
@click.option(
    "--source",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
    ),
    default="requirements.txt",
    metavar="FILEPATH",
    help=(
        "Pip requirements file.."
    ),
)
@click.option(
    "--filekey",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
    ),
    default="api-key.txt",
    metavar="FILEPATH",
    help=(
        "A simple text file which only contains the Libraries.io API key to use "
        "to request the API. It is required since you can not request the API "
        "without an API key."
    ),
)
@click.option(
    "--cachedir",
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
    default=None,
    metavar="DIRPATH",
    help=(
        "A directory where to look for API request cache. It is looked for cache file "
        "per package and if any, avoid any request for a package details. There is not "
        "any mechanic to invalidate or update cache excepting to remove cache files. "
        "The given directory path will be created automatically if it does not "
        "exists yet."
    ),
)
@click.pass_context
def requirements_command(*args, **parameters):
    """
    Analyze package from a requirements file.

    TODO:
    * [x] Get back all arguments from alpha script;
    * [ ] start implementing requirements file parsing;
    * [ ] Test it !
    """
    logger = logging.getLogger(__pkgname__)

    source = parameters["source"].resolve()
    filekey = parameters["filekey"].resolve()
    cachedir = parameters["cachedir"].resolve() if parameters["cachedir"] else None
    api_key = filekey.read_text()

    logger.debug("Requirements file: {}".format(source))
    logger.debug("API file key: {}".format(filekey))
    logger.debug("Cache directory: {}".format(cachedir))

    if cachedir and not cachedir.exists():
        cachedir.mkdir()

    analyzer = DependenciesAnalyzer(api_key, cachedir=cachedir)

