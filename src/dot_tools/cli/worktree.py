from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from typerdrive import attach_logging, handle_errors

from dot_tools.worktree_tools import (
    BranchType,
    build_branch_name,
    checkout_worktree,
    create_worktree,
    find_worktree,
    list_worktrees,
    navigate_to,
    project_root,
    remove_worktree,
)


cli = typer.Typer(help="Create and manage repository worktrees", no_args_is_help=True)


def make_worktree(summary: list[str], branch_type: BranchType, ticket: str | None) -> None:
    branch = build_branch_name(branch_type, " ".join(summary), ticket)
    worktree = create_worktree(branch)
    typer.echo(f"Created worktree for {worktree.branch} at {worktree.path}")
    navigate_to(worktree.path)


def grab_branch(query: list[str]) -> None:
    worktree = checkout_worktree(" ".join(query))
    typer.echo(f"Checked out {worktree.branch} at {worktree.path}")
    navigate_to(worktree.path)


def jump_to_worktree(query: str) -> None:
    worktree = find_worktree(query)
    navigate_to(worktree.path)


def drop_worktree(query: str, delete_branch: bool) -> None:
    root = project_root()
    worktree = find_worktree(query, root=root)
    branch_detail = f" and branch {worktree.branch}" if delete_branch else ""
    typer.confirm(f"Remove worktree {worktree.path}{branch_detail}?", abort=True)
    remove_worktree(worktree, delete_branch=delete_branch)
    navigate_to(root)


def jump_to_root() -> None:
    navigate_to(project_root())


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't build branch name")
@attach_logging()
def name(
    ctx: typer.Context,
    summary: Annotated[list[str], typer.Argument(help="Text summary for the branch name")],
    branch_type: Annotated[BranchType, typer.Option("--type", help="Conventional commit type")] = BranchType.feat,
    ticket: Annotated[str | None, typer.Option("--ticket", help="Ticket identifier")]=None,
):
    """Create a branch and worktree from a summary."""
    branch_name = build_branch_name(branch_type, " ".join(summary), ticket)
    typer.echo(branch_name)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't create worktree")
@attach_logging()
def make(
    ctx: typer.Context,
    summary: Annotated[list[str], typer.Argument(help="Text summary for the branch name")],
    branch_type: Annotated[BranchType, typer.Option("--type", help="Conventional commit type")] = BranchType.feat,
    ticket: Annotated[str | None, typer.Option("--ticket", help="Ticket identifier")]=None,
):
    """Create a branch and worktree from a summary."""
    make_worktree(summary, branch_type, ticket)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't grab branch")
@attach_logging()
def grab(
    ctx: typer.Context,
    query: Annotated[list[str], typer.Argument(help="Text to match against local and origin branches")],
):
    """Grab a matching local or origin branch into a worktree."""
    grab_branch(query)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't find worktree")
@attach_logging()
def jump(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Text to match against worktree branches")],
):
    """Navigate to a matching worktree."""
    jump_to_worktree(query)


@cli.command("list")
@handle_errors("Couldn't list worktrees")
@attach_logging()
def list_(ctx: typer.Context):
    """Show repository worktrees and their branches."""
    root = project_root()
    worktrees = list_worktrees(root)
    if not worktrees:
        typer.echo("No worktrees found.")
        return

    table = Table(
        title="Worktrees",
        title_style="bold cyan",
        header_style="bold white",
        border_style="blue",
        box=box.ROUNDED,
    )
    table.add_column("Branch", style="green", no_wrap=True)
    table.add_column("Path", style="dim")
    for worktree in worktrees:
        table.add_row(worktree.branch, str(worktree.path.relative_to(root)))
    Console().print(table)


@cli.command(no_args_is_help=True)
@handle_errors("Couldn't remove worktree")
@attach_logging()
def drop(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Text to match against worktree branches")],
    delete_branch: Annotated[bool, typer.Option("--branch", help="Delete the branch after removing the worktree")] = False,
):
    """Remove a matching worktree."""
    drop_worktree(query, delete_branch)


@cli.command()
@handle_errors("Couldn't find project root")
@attach_logging()
def root(ctx: typer.Context):
    """Navigate to the project root."""
    jump_to_root()
