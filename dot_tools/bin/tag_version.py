import click

from dot_tools.misc_tools import setup_logging
from dot_tools.version_tools import (
    VersionType,
    VersionManager,
)


@click.command()
@click.option(
    "-c",
    "--comment",
    default="{name} version {release}",
    help="""
        A TEXT comment describing the version.
        May include format_arguments for settings in the metadata file
    """,
)
@click.option(
    # TODO: could be eager...maybe
    "-C",
    "--current-version",
    "print_current",
    is_flag=True,
    help="Print the current version and immediately exit",
)
@click.option(
    "-b",
    "--bump-version",
    "bump_type",
    type=click.Choice(VersionType.all_keys()),
    default=None,
    help="Bump the version",
)
@click.option(
    "-f",
    "--metadata-file",
    "path",
    default=".project_metadata.json",
    help="The path to the METADATA_FILE to parse/update",
)
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
def main(comment, print_current, path, verbose, bump_type):
    """
    Create a new tag based on the project's version
    """
    setup_logging(verbose=verbose)
    version_man = VersionManager(path=path)

    if print_current:
        print(version_man.version)
    else:
        version_man.tag_version(comment=comment, bump_type=bump_type)
