from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Find the top-level for a git clone",
    )
    parser.add_argument(
        '-r',
        '--relative',
        action='store_true',
        help="Find the path as relative to the path",
    )
    parser.add_argument(
        'path',
        nargs='?',
        help="The path for which to find the git toplevel (defaults to pwd)",
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="print extra status messages",
    )
    args = parser.parse_args()
    if args.verbose:
        setup_logging()

    git_man = GitManager(path=args.path)
    print(git_man.toplevel(start_path=args.path, relative=args.relative))
