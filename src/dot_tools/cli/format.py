from pathlib import Path
from typing import Annotated

import typer

from dot_tools.markdown_format import FormatResult, apply_format, check_format, find_markdown_files

cli = typer.Typer(no_args_is_help=True, help="Format supported file types.")


@cli.command("markdown")
def markdown(
    paths: Annotated[list[Path], typer.Argument(..., metavar="PATH")],
    check: Annotated[bool, typer.Option("--check", help="Check formatting without changing files")] = False,
) -> None:
    """Format Markdown files, or check them with --check."""
    file_collection = find_markdown_files(paths)
    result: FormatResult
    if check:
        result = check_format(file_collection.files)
    else:
        result = apply_format(file_collection.files)

    for message in result.messages:
        typer.echo(message, err=bool(result.exit_code))

    if file_collection.errors:
        typer.echo("\n".join(file_collection.errors), err=True)
        raise typer.Exit(result.exit_code or 1)
    if result.exit_code:
        raise typer.Exit(result.exit_code)
    if check:
        typer.echo(f"Markdown format check passed for {len(file_collection.files)} file(s).")
