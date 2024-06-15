import click

from dependency_comb import __version__


@click.command()
@click.pass_context
def version_command(context):
    """
    Print out version information.
    """
    click.echo("dependency-comb {}".format(__version__))
