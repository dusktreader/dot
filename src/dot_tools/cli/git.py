from typing import Annotated

import typer
from typerdrive import handle_errors, attach_logging

from dot_tools.git_tools import GitManager

cli = typer.Typer()

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
