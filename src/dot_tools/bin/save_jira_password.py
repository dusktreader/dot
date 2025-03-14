import click

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
def main(verbose):
    password = click.prompt(
        "Please enter the JIRA password to save",
        hide_input=True,
        confirmation_prompt=True,
    )
    setup_logging(verbose=verbose)
    git_man = GitManager()
    git_man.save_jira_password(password)
