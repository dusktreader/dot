import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from dot_tools.configure import DotInstaller


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Configure dot for current user',
        )
    parser.add_argument(
        '-H',
        '--home',
        default=os.path.expanduser('~'),
        help='The home directory where dotfiles are typically found',
        )
    parser.add_argument(
        '-r',
        '--root',
        default=os.path.expanduser('~/dot'),
        help='The directory where dot is currently found',
        )
    args = parser.parse_args()

    installer = DotInstaller(home=args.home, root=args.root, name='dot-tools')
    installer.install_dot()