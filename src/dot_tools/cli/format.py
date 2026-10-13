from pathlib import Path
from typing import Annotated

import typer

from dot_tools.markdown_format import format_contents, markdown_files, read_file, validate_file


cli = typer.Typer(no_args_is_help=True, help="Format supported file types.")


@cli.command("markdown")
def markdown(
    paths: Annotated[list[Path], typer.Argument(..., metavar="PATH")],
    check: Annotated[bool, typer.Option("--check", help="Check formatting without changing files")] = False,
) -> None:
    """Format Markdown files, or check them with --check."""
    files, input_errors = markdown_files(paths)
    errors = list(input_errors)

    if check:
        for path in files:
            errors.extend(validate_file(path, read_file(path)))
        if errors:
            typer.echo("\n".join(errors), err=True)
            raise typer.Exit(1)
        typer.echo(f"Markdown format check passed for {len(files)} file(s).")
        return

    for path in files:
        contents = read_file(path)
        formatted = format_contents(contents)
        if formatted != contents:
            path.write_text(formatted, encoding="utf-8")
            typer.echo(f"formatted: {path}")
        else:
            typer.echo(f"unchanged: {path}")
        errors.extend(validate_file(path, formatted))

    if errors:
        typer.echo("\n".join(errors), err=True)
        raise typer.Exit(1)
