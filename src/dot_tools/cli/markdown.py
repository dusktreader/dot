"""Typer commands for generic Markdown formatting."""

from pathlib import Path
from typing import Annotated

import typer

from dot_tools.markdown_formatter.models import OperationResult, OperationStatus
from dot_tools.markdown_formatter.operations import check_paths, format_paths

markdown_cli = typer.Typer(no_args_is_help=True, help="Format and check Markdown files.")
Paths = Annotated[list[Path], typer.Argument(..., metavar="PATH")]


def _run(result: OperationResult) -> None:
    """Print operation records and map operation status to the CLI contract."""
    for file in result.files:
        typer.echo(f"{file.status.value} {file.path}")
    for diagnostic in result.diagnostics:
        typer.echo(diagnostic, err=True)
    typer.echo(f"summary {result.operation} {result.status} {len(result.files)}")
    exit_code = {OperationStatus.SUCCESS: 0, OperationStatus.MISMATCH: 1, OperationStatus.READ_ERROR: 3, OperationStatus.PARTIAL_WRITE: 3, OperationStatus.WRITE_ERROR: 3}.get(result.status, 2)
    if exit_code:
        raise typer.Exit(exit_code)


@markdown_cli.command("format")
def format_markdown(paths: Paths) -> None:
    """Format Markdown files in place."""
    _run(format_paths(paths, Path.cwd()))


@markdown_cli.command("check")
def check_markdown(paths: Paths) -> None:
    """Check Markdown files without writing them."""
    _run(check_paths(paths, Path.cwd()))
