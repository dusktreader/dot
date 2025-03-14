import click

from dot_tools.file_tools import find_source_file
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
@click.argument("test_file_path", type=click.Path(exists=True))
def main(test_file_path, verbose):
    """
    Find a source file for a test file at TEST_FILE_PATH
    """
    setup_logging(verbose=verbose)
    print(find_source_file(test_file_path))
