import click

from dot_tools.misc_tools import setup_logging, get_config_line_length


@click.command()
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
def main(verbose):
    setup_logging(verbose=verbose)
    print(get_config_line_length())
