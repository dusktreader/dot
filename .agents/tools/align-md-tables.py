#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["typer"]
# ///

import re
from pathlib import Path

import typer

app = typer.Typer()


def align_table(lines: list[str]) -> list[str]:
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)

    sep_idx = next(
        (i for i, r in enumerate(rows) if all(re.fullmatch(r"-+", c) for c in r)),
        None,
    )

    num_cols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < num_cols:
            r.append("")

    widths = [max(len(r[c]) for r in rows) for c in range(num_cols)]

    result = []
    for i, row in enumerate(rows):
        if i == sep_idx:
            result.append("| " + " | ".join("-" * widths[c] for c in range(num_cols)) + " |")
        else:
            result.append("| " + " | ".join(row[c].ljust(widths[c]) for c in range(num_cols)) + " |")
    return result


def process_file(path: Path) -> None:
    lines = path.read_text().split("\n")
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.extend(align_table(table_lines))
        else:
            out.append(lines[i])
            i += 1
    path.write_text("\n".join(out))


@app.command()
def main(files: list[Path] = typer.Argument(..., help="Markdown files to align in place")) -> None:
    """Align markdown tables in one or more files.

    Each file is rewritten in place. Tables are detected as contiguous blocks of
    lines beginning with '|'. Column widths are computed from the widest cell in
    each column across all rows, including the header. The separator row is
    regenerated to match.

    Non-table content is left untouched.
    """
    for path in files:
        if not path.is_file():
            typer.echo(f"Not a file: {path}", err=True)
            raise typer.Exit(1)
        process_file(path)
        typer.echo(f"aligned: {path}")


if __name__ == "__main__":
    app()
