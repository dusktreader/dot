import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


MARKDOWN_SUFFIX = ".md"
FENCE_PATTERN = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+\S")


def fence_match(line: str) -> re.Match[str] | None:
    """Return a fenced-code match for a line, if present."""
    return FENCE_PATTERN.match(line)


def is_fence_close(match: re.Match[str], fence: str) -> bool:
    """Return whether a fence match closes the active fenced-code block."""
    return match[2][0] == fence[0] and len(match[2]) >= len(fence) and match[3].strip() == ""


def heading_match(line: str) -> re.Match[str] | None:
    """Return a heading match for a line, if present."""
    return HEADING_PATTERN.match(line)


def format_heading_spacing(lines: list[str]) -> list[str]:
    """Normalize blank lines before headings outside fenced code."""
    result: list[str] = []
    fence: str | None = None
    first_heading = True
    for line in lines:
        match = fence_match(line)
        if fence is not None:
            result.append(line)
            if match and is_fence_close(match, fence):
                fence = None
            continue
        if match:
            result.append(line)
            fence = match[2]
            continue

        heading = heading_match(line)
        if not heading:
            result.append(line)
            continue
        if first_heading:
            result.append(line)
            first_heading = False
            continue

        while result and result[-1].strip() == "":
            result.pop()
        prior_line = result[-1] if result else ""
        prior_heading = heading_match(prior_line)
        blank_lines = 1 if prior_line == "----" or (prior_heading and len(heading[1]) > len(prior_heading[1])) else 2
        result.extend([""] * blank_lines)
        result.append(line)
    return result


def format_contents(contents: str) -> str:
    """Normalize the repository's special Markdown heading spacing."""
    return "\n".join(format_heading_spacing(contents.split("\n")))


@dataclass
class FormatResult:
    messages: list[str]
    exit_code: int = 0


@dataclass
class MarkdownFilesResult:
    files: list[Path]
    errors: list[str]


def _run_rumdl(paths: list[Path], check: bool = False) -> int:
    command = ["rumdl", "fmt", "--disable", "MD022"]
    if check:
        command.append("--check")
    command.extend(str(path) for path in paths)
    return subprocess.run(command, check=False).returncode


def check_format(paths: list[Path]) -> FormatResult:
    """Check Markdown formatting with rumdl and the heading-spacing rules."""
    if not paths:
        return FormatResult([])
    try:
        rumdl_exit_code = _run_rumdl(paths, check=True)
    except FileNotFoundError:
        return FormatResult(["rumdl is required to format Markdown files but was not found on PATH."], 127)

    errors = []
    if rumdl_exit_code:
        errors.append(f"rumdl format check failed with status {rumdl_exit_code}.")
    for path in paths:
        contents = read_file(path)
        if format_contents(contents) != contents:
            errors.append(f"{path}: Markdown heading spacing is incorrect.")
    return FormatResult(errors, rumdl_exit_code or int(bool(errors)))


def apply_format(paths: list[Path]) -> FormatResult:
    """Format Markdown files with rumdl and the heading-spacing rules."""
    if not paths:
        return FormatResult([])
    try:
        rumdl_exit_code = _run_rumdl(paths)
    except FileNotFoundError:
        return FormatResult(["rumdl is required to format Markdown files but was not found on PATH."], 127)
    if rumdl_exit_code:
        return FormatResult([f"rumdl formatting failed with status {rumdl_exit_code}."], rumdl_exit_code)

    messages = []
    for path in paths:
        contents = read_file(path)
        formatted = format_contents(contents)
        if formatted != contents:
            path.write_text(formatted, encoding="utf-8")
            messages.append(f"formatted: {path}")
        else:
            messages.append(f"unchanged: {path}")
    return FormatResult(messages)


def find_markdown_files(paths: list[Path]) -> MarkdownFilesResult:
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
    return MarkdownFilesResult(files_list, errors)


def read_file(path: Path) -> str:
    """Read a Markdown file as UTF-8 text."""
    return path.read_text(encoding="utf-8")

