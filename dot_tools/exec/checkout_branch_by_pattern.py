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
@click.argument('pattern')
def main(pattern, verbose):
    """
    Checkout a branch based on a PATTERN
    """
    if verbose:
        setup_logging()

    git_man = GitManager()

    git_man.checkout_branch_by_pattern(pattern)


if __name__ == '__main__':
    main()
