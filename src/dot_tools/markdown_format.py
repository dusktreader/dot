import subprocess
from dataclasses import dataclass
from pathlib import Path


MARKDOWN_SUFFIX = ".md"


@dataclass
class FormatResult:
    messages: list[str]
    exit_code: int = 0


@dataclass
class MarkdownFilesResult:
    files: list[Path]
    errors: list[str]


def _run_rumdl(paths: list[Path], check: bool = False) -> int:
    command = ["rumdl", "fmt"]
    if check:
        command.append("--check")
    command.extend(str(path) for path in paths)
    return subprocess.run(command, check=False).returncode


def check_format(paths: list[Path]) -> FormatResult:
    """Check Markdown formatting with rumdl."""
    if not paths:
        return FormatResult([])
    try:
        rumdl_exit_code = _run_rumdl(paths, check=True)
    except FileNotFoundError:
        return FormatResult(["rumdl is required to format Markdown files but was not found on PATH."], 127)
    if rumdl_exit_code:
        return FormatResult([f"rumdl format check failed with status {rumdl_exit_code}."], rumdl_exit_code)
    return FormatResult([])


def apply_format(paths: list[Path]) -> FormatResult:
    """Format Markdown files with rumdl."""
    if not paths:
        return FormatResult([])
    original_contents = {path: read_file(path) for path in paths}
    try:
        rumdl_exit_code = _run_rumdl(paths)
    except FileNotFoundError:
        return FormatResult(["rumdl is required to format Markdown files but was not found on PATH."], 127)
    if rumdl_exit_code:
        return FormatResult([f"rumdl formatting failed with status {rumdl_exit_code}."], rumdl_exit_code)

    messages = []
    for path in paths:
        if read_file(path) != original_contents[path]:
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

