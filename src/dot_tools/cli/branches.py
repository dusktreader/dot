import json
from typing import Annotated

import typer
from typerdrive import attach_settings, handle_errors, attach_logging

from dot_tools.git_tools import GitManager
from dot_tools.jira_tools import JiraManager
from dot_tools.settings import Settings

cli = typer.Typer(help="Commands to interact with git")


@cli.command()
@handle_errors("Couldn't checkout branch by pattern")
@attach_logging()
def cojira(
    ctx: typer.Context,
    pattern: Annotated[str, typer.Argument(help="The branch pattern to search for")],
):
    """
    Checkout a git branch based on a pattern
    """
    git_man = GitManager()
    git_man.checkout_branch_by_pattern(pattern)


@cli.command()
@handle_errors("Couldn't get JIRA issue")
@attach_settings(Settings)
@attach_logging()
def issue(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(help="The JIRA key")],
    settings: Settings,
):
    """
    Checkout a git branch based on a pattern
    """
    jira_man = JiraManager(settings.jira_info)
    jira_man.get_issue(key)
