import click

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    '-v/-q',
    '--verbose/--quiet',
    default=False,
    help="control verbosity of status messages",
)
def main(verbose):
    """
    Push a new branch up to the origin git repo
    """
    if verbose:
        setup_logging()

    git_man = GitManager()
    git_man.pushup()


if __name__ == '__main__':
    main()
