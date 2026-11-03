#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["dot-tools"]
#
# [tool.uv.sources]
# dot-tools = { path = "../..", editable = true }
# ///

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Annotated

import git
import typer
from dot_tools.exceptions import DotError
from dot_tools.worktree_tools import BranchType, parameterize_summary, validate_ticket


class ArtifactDirectoryError(ValueError):
    pass


def artifact_directory_component(branch_type: BranchType, summary: str, ticket: str | None = None) -> str:
    summary_slug = parameterize_summary(summary)
    if not summary_slug:
        raise ArtifactDirectoryError("Summary must contain at least one letter or number")

    try:
        ticket = validate_ticket(ticket)
    except DotError as error:
        raise ArtifactDirectoryError(str(error)) from error

    if ticket:
        return f"{branch_type.value}--{ticket}--{summary_slug}"

    return f"{branch_type.value}--{summary_slug}"


def matching_artifact_dirs(artifact_root: Path, artifact_component: str) -> list[Path]:
    if not artifact_root.exists():
        return []
    if not artifact_root.is_dir():
        raise ArtifactDirectoryError(f"Artifact root is not a directory: {artifact_root}")

    return sorted(
        path
        for path in artifact_root.iterdir()
        if path.is_dir()
        and len(path.name) > 10
        and path.name[:8].isdigit()
        and path.name[8:10] == "--"
        and path.name[10:] == artifact_component
    )


def create_artifact_dir(
    summary: str,
    branch_type: BranchType = BranchType.feat,
    ticket: str | None = None,
    cwd: Path | None = None,
    created_on: date | None = None,
) -> Path:
    artifact_component = artifact_directory_component(branch_type, summary, ticket)

    try:
        repository = git.Repo(cwd or Path.cwd(), search_parent_directories=True)
    except (git.InvalidGitRepositoryError, git.NoSuchPathError) as error:
        raise ArtifactDirectoryError("Current directory is not inside a Git worktree") from error

    if repository.working_tree_dir is None:
        raise ArtifactDirectoryError("Current Git repository has no working directory")
    worktree_root = Path(repository.working_tree_dir)
    if not worktree_root.is_dir():
        raise ArtifactDirectoryError("Current Git worktree has no working directory")

    artifact_root = worktree_root / ".artifacts"
    matching_dirs = matching_artifact_dirs(artifact_root, artifact_component)
    if len(matching_dirs) > 1:
        paths = ", ".join(str(path) for path in matching_dirs)
        raise ArtifactDirectoryError(f"Multiple artifact directories match '{artifact_component}': {paths}")
    if matching_dirs:
        return matching_dirs[0]

    artifact_date = created_on or datetime.now().astimezone().date()
    artifact_dir = artifact_root / f"{artifact_date:%Y%m%d}--{artifact_component}"
    try:
        artifact_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        if artifact_dir.is_dir():
            return artifact_dir
        raise ArtifactDirectoryError(f"Artifact path already exists and is not a directory: {artifact_dir}")

    return artifact_dir


def main(
    summary: Annotated[list[str], typer.Argument(help="Text summary for the task")],
    branch_type: Annotated[BranchType, typer.Option("--type", help="Conventional branch type")] = BranchType.feat,
    ticket: Annotated[str | None, typer.Option("--ticket", help="Ticket identifier")] = None,
) -> None:
    try:
        artifact_dir = create_artifact_dir(" ".join(summary), branch_type, ticket)
    except ArtifactDirectoryError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error

    typer.echo(str(artifact_dir))


if __name__ == "__main__":
    typer.run(main)
