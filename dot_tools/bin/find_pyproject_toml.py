import click

from dot_tools.misc_tools import DotException, setup_logging, find_pyproject_toml


@click.command()
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
def main(verbose):
    setup_logging(verbose=verbose)
    pyproject_toml = find_pyproject_toml()
    DotException.require_condition(
        pyproject_toml, "Couldn't find a pyproject.toml from pwd"
    )
    print(pyproject_toml)
