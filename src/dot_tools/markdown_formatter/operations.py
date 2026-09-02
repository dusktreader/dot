"""Filesystem operation contracts for Markdown formatting."""

from collections.abc import Sequence
from pathlib import Path

from .models import Operation, OperationResult, OperationStatus
from . import format_document
from .models import FileResult, FileStatus


def format_paths(paths: Sequence[Path], cwd: Path | None = None) -> OperationResult:
    """Format Markdown paths."""
    files = _collect(paths, cwd)
    results: list[FileResult] = []
    for path in files:
        try:
            source = path.read_bytes()
            output = format_document(source)
        except (OSError, ValueError, UnicodeError) as error:
            results.append(FileResult(path, FileStatus.READ_ERROR, "error", error=str(error)))
            continue
        if output == source:
            results.append(FileResult(path, FileStatus.UNCHANGED, "unchanged"))
        else:
            try:
                path.write_bytes(output)
            except OSError as error:
                results.append(FileResult(path, FileStatus.WRITE_ERROR, "error", error=str(error)))
            else:
                results.append(FileResult(path, FileStatus.FORMATTED, "formatted", output=output))
    return OperationResult(Operation.FORMAT, _status(results), tuple(results))


def check_paths(paths: Sequence[Path], cwd: Path | None = None) -> OperationResult:
    """Check Markdown paths."""
    files = _collect(paths, cwd)
    results: list[FileResult] = []
    for path in files:
        try:
            source = path.read_bytes()
            output = format_document(source)
        except (OSError, ValueError, UnicodeError) as error:
            results.append(FileResult(path, FileStatus.READ_ERROR, "error", error=str(error)))
            continue
        if output == source:
            results.append(FileResult(path, FileStatus.UNCHANGED, "unchanged"))
        else:
            results.append(FileResult(path, FileStatus.MISMATCH, "mismatch"))
    status = OperationStatus.MISMATCH if any(item.status == FileStatus.MISMATCH for item in results) else _status(results)
    return OperationResult(Operation.CHECK, status, tuple(results))


def _collect(paths: Sequence[Path], cwd: Path | None) -> list[Path]:
    """Collect sorted Markdown files from explicit paths."""
    base = cwd or Path.cwd()
    found: set[Path] = set()
    for item in paths:
        path = item if item.is_absolute() else base / item
        if path.is_dir():
            found.update(candidate.resolve() for candidate in path.rglob("*.md") if candidate.is_file())
        elif path.is_file() and path.suffix == ".md":
            found.add(path.resolve())
    return sorted(found)


def _status(results: Sequence[FileResult]) -> OperationStatus:
    """Map file statuses to an operation status."""
    if any(item.status == FileStatus.WRITE_ERROR for item in results):
        return OperationStatus.WRITE_ERROR
    if any(item.status == FileStatus.READ_ERROR for item in results):
        return OperationStatus.READ_ERROR
    return OperationStatus.SUCCESS
