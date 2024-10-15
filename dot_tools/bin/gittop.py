import click

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    "-r/-a",
    "--relative/--absolute",
    default=False,
    help="How to represent the found path",
)
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
@click.argument("path", nargs=1, required=False)
def main(path, relative, verbose):
    """Find the top-level for a PATH in a git clone. PATH defaults to pwd"""
    setup_logging(verbose=verbose)

    git_man = GitManager(path=path)
    print(git_man.toplevel(start_path=path, relative=relative))
