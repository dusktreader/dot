#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["dot-tools"]
#
# [tool.uv.sources]
# dot-tools = { path = "../..", editable = true }
# ///

from __future__ import annotations

from typing import Annotated

import git
import typer
from dot_tools.exceptions import DotError
from dot_tools.worktree_tools import (
    BranchRef,
    BranchType,
    Worktree,
    build_branch_name,
    checkout_worktree,
    create_worktree,
    list_worktrees,
    matching_branches,
    navigate_to,
    project_root,
)


def pull_worktree(worktree: Worktree) -> None:
    repository = git.Repo(worktree.path)
    tracking_branch = repository.head.reference.tracking_branch()
    if tracking_branch is None:
        return
    repository.git.pull(tracking_branch.remote_name, tracking_branch.remote_head)


def search_candidates(ticket: str | None, summary: str) -> list[tuple[str, Worktree | None, str | None]]:
    root = project_root()
    repository = git.Repo(root)
    worktrees = {worktree.branch: worktree for worktree in list_worktrees(root)}
    branches = {head.name: BranchRef(head.name) for head in repository.heads}
    for remote in repository.remotes:
        for ref in remote.refs:
            if ref.remote_head != "HEAD":
                branches.setdefault(ref.remote_head, BranchRef(ref.remote_head, remote.name))

    matches: dict[str, BranchRef] = {}
    for query in (ticket, summary):
        if not query:
            continue
        try:
            query_matches = matching_branches(query, list(branches.values()), similarity=0.2)
        except DotError:
            continue
        matches.update((branch.name, branch) for branch in query_matches)

    return [(branch.name, worktrees.get(branch.name), branch.remote) for branch in matches.values()]


def search_command(
    summary: Annotated[list[str], typer.Argument(help="Text summary to compare")],
    ticket: Annotated[str | None, typer.Option("--ticket", help="Ticket identifier to compare")] = None,
) -> None:
    matches = search_candidates(ticket, " ".join(summary))
    if not matches:
        typer.echo("No similar branches or worktrees found.")
        return

    for branch, worktree, remote in matches:
        location = (
            str(worktree.path) if worktree else (f"remote branch: {remote}/{branch}" if remote else "local branch")
        )
        typer.echo(f"{branch} ({location})")


def switch_command(
    summary: Annotated[list[str], typer.Argument(help="Text summary for the task")],
    branch_type: Annotated[BranchType, typer.Option("--type", help="Conventional commit type")] = BranchType.feat,
    ticket: Annotated[str | None, typer.Option("--ticket", help="Ticket identifier")] = None,
) -> None:
    branch = build_branch_name(branch_type, " ".join(summary), ticket)
    root = project_root()
    worktree = next((item for item in list_worktrees(root) if item.branch == branch), None)

    if worktree is not None:
        pull_worktree(worktree)
        typer.echo(f"Using existing worktree for {worktree.branch} at {worktree.path}")
    else:
        try:
            worktree = checkout_worktree(branch)
        except DotError as error:
            if not str(error).startswith("No local or origin branch matches"):
                raise
            worktree = create_worktree(branch)
            typer.echo(f"Created worktree for {worktree.branch} at {worktree.path}")
        else:
            pull_worktree(worktree)
            typer.echo(f"Checked out existing branch {worktree.branch} at {worktree.path}")

    navigate_to(worktree.path)


app = typer.Typer(help="Find or switch to a task worktree", no_args_is_help=True)
app.command("search")(search_command)
app.command("switch")(switch_command)


if __name__ == "__main__":
    app()
