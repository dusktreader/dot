import click

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    "-b",
    "--base",
    help="the base for the new branch. Defaults to current branch",
)
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
@click.argument("issue")
def main(base, verbose, issue):
    """
    Create a new git branch based on a github or JIRA issue named ISSUE
    """
    setup_logging(verbose=verbose)
    git_man = GitManager()
    git_man.make_branch(issue, base=base)
