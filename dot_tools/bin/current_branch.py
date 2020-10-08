import click

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
def main(verbose):
    """
    Get the name of the current branch
    """
    setup_logging(verbose=verbose)
    git_man = GitManager()
    print(git_man.current_branch)
