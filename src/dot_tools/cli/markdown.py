"""Typer commands for generic Markdown formatting."""

from pathlib import Path
from typing import Annotated

import typer

from dot_tools.markdown_formatter.operations import check_paths, format_paths

markdown_cli = typer.Typer(no_args_is_help=True, help="Format and check Markdown files.")
Paths = Annotated[list[Path], typer.Argument(..., metavar="PATH")]


def _run(result) -> None:
    """Print operation records and exit with the operation status."""
    for file in result.files:
        typer.echo(f"{file.status} {file.path}")
    typer.echo(f"summary {result.operation} {result.status} {len(result.files)}")
    if result.status.value != "SUCCESS":
        raise typer.Exit(1)


@markdown_cli.command("format")
def format_markdown(paths: Paths) -> None:
    """Format Markdown files in place."""
    _run(format_paths(paths, Path.cwd()))


@markdown_cli.command("check")
def check_markdown(paths: Paths) -> None:
    """Check Markdown files without writing them."""
    _run(check_paths(paths, Path.cwd()))
