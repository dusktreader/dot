import click

from dot_tools.file_tools import find_test_file
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
@click.argument("source_file_path", type=click.Path(exists=True))
def main(source_file_path, verbose):
    """
    Find a test file for a source file at SOURCE_FILE_PATH
    """
    setup_logging(verbose=verbose)
    print(find_test_file(source_file_path))
