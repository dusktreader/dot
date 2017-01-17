import os
import click
import logbook

from dot_tools.configure import DotInstaller
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    '-H', '--home',
    default=os.path.expanduser('~'), type=click.Path(exists=True),
    help='The home directory where dotfiles are typically found',
)
@click.option(
    '-r', '--root',
    default=os.path.expanduser('~/dot'), type=click.Path(exists=True),
    help='The directory where dot is currently found',
)
@click.option(
    '-v/-q',
    '--verbose/--quiet',
    default=False,
    help="control verbosity of status messages",
)
def main(home, root, verbose):
    """
    Configure dot for the current user
    """
    if verbose:
        setup_logging(level=logbook.DEBUG)
    else:
        setup_logging(level=logbook.INFO)
    installer = DotInstaller(home=home, root=root, name='dot-tools')
    installer.install_dot()


if __name__ == '__main__':
    main()
