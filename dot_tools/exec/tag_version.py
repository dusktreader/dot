from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from dot_tools.git_tools import tag_version, get_current_version, VersionType

if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Create a new tag based on the project's version",
    )
    parser.add_argument(
        '-c',
        '--comment',
        default='{name} version {release}',
        help="""
            A TEXT comment describing the version.
            May include format_arguments for settings in the metadata file
        """,
    )
    parser.add_argument(
        '-C',
        '--current-version',
        action='store_true',
        help="Print the current version and immediately exit",
    )
    parser.add_argument(
        '-b',
        '--bump-version',
        nargs='?',
        const=VersionType.patch.name,
        choices=VersionType.all_keys(),
        help="""
            Bump the version.
            If specified without argument, will be {}.
            If an argument is supplied, it must be one of: {}.
        """.format(
            repr(VersionType.patch.name),
            VersionType.all_keys(),
        ),
    )
    parser.add_argument(
        '-f',
        '--metadata-file',
        default='.project_metadata.json',
        help="The PATH to the metadata file to parse/update",
        metavar='PATH',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="print extra status messages",
    )
    args = parser.parse_args()

    if args.current_version:
        version = get_current_version(path=args.metadata_file)
        print(version)
    else:
        tag_version(
            comment=args.comment,
            bump_type=args.bump_version,
            path=args.metadata_file,
            verbose=args.verbose,
        )