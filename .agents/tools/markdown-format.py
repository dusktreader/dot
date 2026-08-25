#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["typer"]
# ///

import re
import textwrap
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

import typer


MAX_PROSE_LINE_LENGTH = 120
MARKDOWN_SUFFIX = ".md"
FENCE_PATTERN = re.compile(r"^(\s*)(`{3,})(.*)$")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+\S")
H1_PATTERN = re.compile(r"^#\s+\S")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-+:?$")
FRONTMATTER_DELIMITERS = {"---", "..."}

app = typer.Typer(no_args_is_help=True, help="Check and format Markdown files.")
Paths = Annotated[list[Path], typer.Argument(..., metavar="PATH")]


def fence_match(line: str) -> re.Match[str] | None:
    """Return a fenced-code match for a line, if present."""
    return FENCE_PATTERN.match(line)


def is_fence_close(match: re.Match[str], fence_length: int) -> bool:
    """Return whether a fence match closes the active fenced-code block."""
    return len(match[2]) >= fence_length and match[3].strip() == ""


def heading_match(line: str) -> re.Match[str] | None:
    """Return a heading match for a line, if present."""
    return HEADING_PATTERN.match(line)


def frontmatter_end(lines: list[str]) -> int | None:
    """Return the first line after YAML frontmatter, if present."""
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() in FRONTMATTER_DELIMITERS:
            return index + 1
    return None


def first_content_line(lines: list[str]) -> int:
    """Return the first non-blank Markdown line after optional frontmatter."""
    start = frontmatter_end(lines) or 0
    while start < len(lines) and lines[start].strip() == "":
        start += 1
    return start


def requires_h1(lines: list[str]) -> bool:
    """Return whether a Markdown file requires a prose H1 title."""
    content_start = first_content_line(lines)
    return not (
        frontmatter_end(lines) is not None
        and content_start < len(lines)
        and re.fullmatch(
            r"Read and follow the agent description in ~/.agents/agents/[a-z-]+\.md\.",
            lines[content_start],
        )
    )


def split_table_row(line: str) -> list[str]:
    """Split a pipe-table row without treating escaped or code-span pipes as delimiters."""
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]

    cells: list[str] = []
    cell: list[str] = []
    code_ticks = 0
    index = 0
    while index < len(row):
        character = row[index]
        if character == "\\" and index + 1 < len(row):
            cell.extend(row[index : index + 2])
            index += 2
            continue
        if character == "`":
            end = index
            while end < len(row) and row[end] == "`":
                end += 1
            ticks = end - index
            cell.extend(row[index:end])
            if code_ticks == 0:
                code_ticks = ticks
            elif code_ticks == ticks:
                code_ticks = 0
            index = end
            continue
        if character == "|" and code_ticks == 0:
            cells.append("".join(cell).strip())
            cell = []
        else:
            cell.append(character)
        index += 1

    cells.append("".join(cell).strip())
    return cells


def is_separator_row(cells: list[str]) -> bool:
    """Return whether cells describe a Markdown table separator row."""
    return bool(cells) and all(TABLE_SEPARATOR_PATTERN.fullmatch(cell) for cell in cells)


def separator_markers(cell: str) -> tuple[bool, bool]:
    """Return the left and right alignment markers from a separator cell."""
    return cell.startswith(":"), cell.endswith(":")


def align_table(lines: list[str]) -> list[str]:
    """Align a Markdown table and regenerate its separator row."""
    rows = [split_table_row(line) for line in lines]
    separator_index = next((index for index, row in enumerate(rows) if is_separator_row(row)), None)
    if separator_index is None:
        return lines

    column_count = max(len(row) for row in rows)
    for row in rows:
        row.extend("" for _ in range(column_count - len(row)))

    widths = []
    for column in range(column_count):
        content_width = max(
            (len(row[column]) for index, row in enumerate(rows) if index != separator_index),
            default=0,
        )
        left_marker, right_marker = separator_markers(rows[separator_index][column])
        marker_count = int(left_marker) + int(right_marker)
        widths.append(max(content_width, marker_count + 3))

    aligned = []
    for index, row in enumerate(rows):
        if index == separator_index:
            cells = []
            for column, cell in enumerate(row):
                left_marker, right_marker = separator_markers(cell)
                marker_count = int(left_marker) + int(right_marker)
                dashes = "-" * (widths[column] - marker_count)
                cells.append(f"{':' if left_marker else ''}{dashes}{':' if right_marker else ''}")
        else:
            cells = [cell.ljust(widths[column]) for column, cell in enumerate(row)]
        aligned.append("| " + " | ".join(cells) + " |")
    return aligned


def table_blocks(lines: list[str]) -> Iterator[tuple[int, list[str]]]:
    """Yield contiguous pipe-row blocks outside fenced code."""
    fence_length = None
    index = 0
    while index < len(lines):
        line = lines[index]
        match = fence_match(line)
        if fence_length is not None:
            if match and is_fence_close(match, fence_length):
                fence_length = None
            index += 1
            continue
        if match:
            fence_length = len(match[2])
            index += 1
            continue
        if not line.startswith("|"):
            index += 1
            continue

        start = index
        while index < len(lines) and lines[index].startswith("|"):
            index += 1
        yield start, lines[start:index]


def wrap_prose_line(line: str) -> list[str]:
    """Wrap one long prose line without changing its Markdown block marker."""
    if len(line) <= MAX_PROSE_LINE_LENGTH or not line.strip():
        return [line]
    if heading_match(line) or re.fullmatch(r"\s*-{3,}\s*", line):
        return [line]

    marker = re.match(r"^(\s*(?:[-+*]\s+|\d+\.\s+|>\s?))", line)
    if marker:
        initial_indent = marker[1]
        text = line[len(initial_indent) :]
        subsequent_indent = initial_indent if initial_indent.lstrip().startswith(">") else " " * len(initial_indent)
    else:
        initial_indent = line[: len(line) - len(line.lstrip())]
        text = line[len(initial_indent) :]
        subsequent_indent = initial_indent

    return textwrap.wrap(
        text,
        width=MAX_PROSE_LINE_LENGTH,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [line]


def format_heading_spacing(lines: list[str]) -> list[str]:
    """Normalize blank lines before headings outside fenced code."""
    prefix_end = frontmatter_end(lines)
    if prefix_end is None:
        result: list[str] = []
        content = lines
    else:
        content_start = first_content_line(lines)
        result = lines[:prefix_end]
        if content_start < len(lines) and requires_h1(lines):
            result.append("")
        content = lines[content_start:]

    fence_length = None
    first_content_heading = True
    for line in content:
        match = fence_match(line)
        if fence_length is not None:
            result.append(line)
            if match and is_fence_close(match, fence_length):
                fence_length = None
            continue
        if match:
            result.append(line)
            fence_length = len(match[2])
            continue

        heading = heading_match(line)
        if not heading:
            result.append(line)
            continue

        if first_content_heading:
            result.append(line)
            first_content_heading = False
            continue

        while result and result[-1].strip() == "":
            result.pop()
        if not result:
            result.append(line)
            continue

        prior_line = result[-1]
        prior_heading = heading_match(prior_line)
        expected_blank_lines = 1 if prior_line == "----" or (prior_heading and len(heading[1]) > len(prior_heading[1])) else 2
        result.extend([""] * expected_blank_lines)
        result.append(line)
    return result


def format_contents(contents: str) -> str:
    """Apply deterministic Markdown formatting to file contents."""
    lines = [line.rstrip() for line in contents.split("\n")]
    prefix_end = frontmatter_end(lines)
    content_start = first_content_line(lines)
    if prefix_end is not None:
        formatted = lines[:prefix_end]
        if content_start < len(lines) and requires_h1(lines):
            formatted.append("")
    else:
        formatted = []
        content_start = 0

    fence_length = None
    index = content_start
    while index < len(lines):
        line = lines[index]
        match = fence_match(line)
        if fence_length is not None:
            formatted.append(line)
            if match and is_fence_close(match, fence_length):
                fence_length = None
            index += 1
            continue
        if match:
            info = match[3].strip()
            if not info:
                info = "text"
            elif info in {"bash", "sh"}:
                info = "shell"
            formatted.append(f"{match[1]}{match[2]}{info}")
            fence_length = len(match[2])
            index += 1
            continue
        heading = heading_match(line)
        if heading and len(heading[1]) > 4:
            line = "####" + line[len(heading[1]) :]
        if line.startswith("|"):
            start = index
            while index < len(lines) and lines[index].startswith("|"):
                index += 1
            block = lines[start:index]
            formatted.extend(align_table(block) if any(is_separator_row(split_table_row(row)) for row in block) else block)
            continue
        formatted.extend(wrap_prose_line(line))
        index += 1

    return "\n".join(format_heading_spacing(formatted))


def validate_file(path: Path, contents: str) -> list[str]:
    """Return formatting errors for one Markdown file."""
    errors: list[str] = []
    lines = contents.split("\n")
    content_start = first_content_line(lines)
    prefix_end = frontmatter_end(lines) or 0
    if requires_h1(lines) and not H1_PATTERN.match(lines[content_start] if content_start < len(lines) else ""):
        line_number = content_start + 1 if content_start < len(lines) else 1
        errors.append(f"{path}:{line_number}: Markdown documents must begin with one H1 title.")

    fence_length = None
    fence_line = None
    for index, line in enumerate(lines):
        line_number = index + 1
        if re.search(r"\s+$", line):
            errors.append(f"{path}:{line_number}: Trailing whitespace.")

        if index < prefix_end:
            continue

        match = fence_match(line)
        if fence_length is not None:
            if match and is_fence_close(match, fence_length):
                fence_length = None
                fence_line = None
            continue
        if match:
            info = match[3].strip()
            if not info:
                errors.append(f"{path}:{line_number}: Fenced code blocks must declare a language.")
            elif info in {"bash", "sh"}:
                errors.append(f"{path}:{line_number}: Use the shell fence language instead of {info}.")
            fence_length = len(match[2])
            fence_line = line_number
            continue

        if line.startswith("|"):
            continue
        if len(line) > MAX_PROSE_LINE_LENGTH:
            errors.append(f"{path}:{line_number}: Prose exceeds {MAX_PROSE_LINE_LENGTH} characters.")

        heading = heading_match(line)
        if not heading or index == content_start:
            continue
        level = len(heading[1])
        if level >= 5:
            errors.append(f"{path}:{line_number}: Avoid heading levels 5 and deeper.")
        if "**" in line:
            errors.append(f"{path}:{line_number}: Do not use bold text in headings.")
        if re.search(r"[.:;!?]$", line):
            errors.append(f"{path}:{line_number}: Headings must not end with punctuation.")

        prior_index = index - 1
        while prior_index >= 0 and lines[prior_index].strip() == "":
            prior_index -= 1
        prior_line = lines[prior_index] if prior_index >= 0 else ""
        prior_heading = heading_match(prior_line)
        expected_blank_lines = 1 if prior_line == "----" or (prior_heading and level > len(prior_heading[1])) else 2
        actual_blank_lines = index - prior_index - 1
        if actual_blank_lines != expected_blank_lines:
            errors.append(
                f"{path}:{line_number}: Expected {expected_blank_lines} blank line(s) before this heading; "
                f"found {actual_blank_lines}."
            )

    if fence_length is not None:
        errors.append(f"{path}:{fence_line}: Fenced code block is not closed.")

    for start, block in table_blocks(lines):
        if any(is_separator_row(split_table_row(row)) for row in block) and block != align_table(block):
            errors.append(f"{path}:{start + 1}: Table columns are not aligned.")
    return errors


def markdown_files(paths: list[Path]) -> tuple[list[Path], list[str]]:
    """Collect Markdown files from files and directories."""
    files: set[Path] = set()
    errors: list[str] = []
    for path in paths:
        if not path.exists():
            errors.append(f"Not found: {path}")
        elif path.is_file():
            if path.suffix != MARKDOWN_SUFFIX:
                errors.append(f"Not a Markdown file: {path}")
            else:
                files.add(path)
        elif path.is_dir():
            files.update(Path(candidate) for candidate in path.rglob(f"*{MARKDOWN_SUFFIX}") if candidate.is_file())
    files_list: list[Path] = list(files)
    files_list.sort(key=str)
    return files_list, errors


def read_file(path: Path) -> str:
    """Read a Markdown file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


@app.command()
def check(paths: Paths) -> None:
    """Report Markdown formatting issues without changing files."""
    files, input_errors = markdown_files(paths)
    errors = list(input_errors)
    for path in files:
        errors.extend(validate_file(path, read_file(path)))
    if errors:
        typer.echo("\n".join(errors), err=True)
        raise typer.Exit(1)
    typer.echo(f"Markdown format check passed for {len(files)} file(s).")


@app.command("format")
def format_markdown(paths: Paths) -> None:
    """Format Markdown files in place and report issues that remain."""
    files, input_errors = markdown_files(paths)
    errors = list(input_errors)
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


if __name__ == "__main__":
    app()
