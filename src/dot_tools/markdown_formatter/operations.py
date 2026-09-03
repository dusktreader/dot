"""Collect, check, and safely replace Markdown files."""

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
import hashlib
import fcntl
import os
from pathlib import Path
import stat

from . import format_document
from .models import FileResult, FileSnapshot, FileStatus, Operation, OperationResult, OperationStatus


def _absolute(path: Path, cwd: Path) -> Path:
    """Resolve a command operand without resolving symlinks."""
    candidate = path if path.is_absolute() else cwd / path
    return Path(os.path.normpath(os.path.abspath(candidate)))


def _collect(paths: Sequence[Path], cwd: Path | None) -> tuple[list[Path], list[FileResult]]:
    """Discover Markdown files and retain errors for explicit invalid operands."""
    base = (cwd or Path.cwd()).absolute()
    found: set[Path] = set()
    errors: list[FileResult] = []
    for operand in paths:
        path = _absolute(operand, base)
        try:
            if path.is_dir():
                for candidate in path.rglob("*.md"):
                    if candidate.is_file() and not candidate.is_symlink():
                        found.add(_absolute(candidate, base))
            elif path.is_file() and path.suffix == ".md":
                found.add(path)
            else:
                detail = "path does not exist" if not path.exists() else "path is not a Markdown file"
                errors.append(FileResult(path, FileStatus.INPUT_ERROR, "error", error=detail))
        except OSError as error:
            errors.append(FileResult(path, FileStatus.READ_ERROR, "error", error=str(error)))
    unique_errors = {result.path: result for result in errors}
    return sorted(found), [unique_errors[path] for path in sorted(unique_errors)]


def _snapshot(path: Path, content: bytes) -> FileSnapshot:
    """Capture bytes and lstat metadata for a destination."""
    metadata = path.lstat()
    return FileSnapshot(
        content,
        hashlib.sha256(content).hexdigest(),
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        stat.S_IFMT(metadata.st_mode),
    )


def _safe_destination(path: Path, snapshot: FileSnapshot) -> bool:
    """Return whether the destination is unchanged and safe to replace."""
    try:
        metadata = path.lstat()
        return (
            stat.S_ISREG(metadata.st_mode)
            and not path.is_symlink()
            and bool(snapshot.mode & 0o222)
            and (metadata.st_dev, metadata.st_ino, metadata.st_mode, stat.S_IFMT(metadata.st_mode))
            == (snapshot.device, snapshot.inode, snapshot.mode, snapshot.file_type)
            and path.read_bytes() == snapshot.content
        )
    except OSError:
        return False


@contextmanager
def _destination_lock(path: Path) -> Iterator[None]:
    """Hold the shared lock for the directory containing `path`.

    Formatter writers use this lock for temporary-file creation, the final
    snapshot check, and replacement. This serializes writers that honor the
    formatter protocol. It cannot prevent an unrelated process from
    modifying or renaming the destination without taking the lock.
    """
    lock_path = path.parent / ".dt-markdown-format.lock"
    with lock_path.open("a+") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _replace(path: Path, output: bytes, snapshot: FileSnapshot) -> None:
    """Replace one destination while holding its cooperating-writer lock."""
    temporary: Path | None = None
    temporary_identity: tuple[int, int] | None = None
    created = False
    primary_error: Exception | None = None
    with _destination_lock(path):
        try:
            temporary = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
            with temporary.open("xb") as handle:
                created = True
                metadata = os.fstat(handle.fileno())
                temporary_identity = (metadata.st_dev, metadata.st_ino)
                handle.write(output)
                os.chmod(temporary, stat.S_IMODE(snapshot.mode))
                handle.flush()
                os.fsync(handle.fileno())
            if not _safe_destination(path, snapshot):
                raise _PreflightFailure("destination changed, is not regular, or is read-only")
            os.replace(temporary, path)
            temporary = None
        except Exception as error:
            primary_error = error
            raise
        finally:
            if created and temporary is not None:
                try:
                    if temporary_identity is not None:
                        metadata = temporary.lstat()
                        if (metadata.st_dev, metadata.st_ino) == temporary_identity:
                            temporary.unlink()
                except FileNotFoundError:
                    pass
                except OSError:
                    if primary_error is None:
                        raise


class _PreflightFailure(OSError):
    """Report a destination that failed the immediate optimistic check."""


def _operation_status(operation: Operation, results: Sequence[FileResult], committed: Sequence[Path] = ()) -> OperationStatus:
    """Apply the documented mixed-result precedence."""
    statuses = {item.status for item in results}
    if FileStatus.INPUT_ERROR in statuses:
        return OperationStatus.INPUT_ERROR
    if FileStatus.PREFLIGHT_ERROR in statuses:
        return OperationStatus.PREFLIGHT_ERROR
    if FileStatus.READ_ERROR in statuses:
        return OperationStatus.READ_ERROR
    if FileStatus.WRITE_ERROR in statuses:
        return OperationStatus.PARTIAL_WRITE if committed else OperationStatus.WRITE_ERROR
    if operation is Operation.CHECK and FileStatus.MISMATCH in statuses:
        return OperationStatus.MISMATCH
    return OperationStatus.SUCCESS


def _diagnostics(results: Sequence[FileResult]) -> tuple[str, ...]:
    """Build sorted stable diagnostics, including only digest values for mismatches."""
    values: list[tuple[Path, str]] = []
    for result in results:
        if result.status is FileStatus.MISMATCH and result.snapshot is not None:
            expected = hashlib.sha256(format_document(result.snapshot.content)).hexdigest()
            values.append((result.path, f"{result.path}: mismatch: expected SHA-256 {expected}, actual SHA-256 {result.snapshot.digest}"))
        elif result.error is not None:
            values.append((result.path, f"{result.path}: {result.status.value}: {result.error}"))
    return tuple(text for _, text in sorted(values, key=lambda item: (item[0], item[1])))


def _prepare(paths: Sequence[Path], cwd: Path | None, operation: Operation) -> tuple[list[Path], list[FileResult], list[tuple[Path, bytes, bytes, FileSnapshot]]]:
    """Read, snapshot, and render every discovered file before writing."""
    discovered, errors = _collect(paths, cwd)
    files = sorted({path for path in discovered} | {result.path for result in errors})
    results = list(errors)
    prepared: list[tuple[Path, bytes, bytes, FileSnapshot]] = []
    for path in discovered:
        snapshot: FileSnapshot | None = None
        try:
            source = path.read_bytes()
            snapshot = _snapshot(path, source)
            output = format_document(source)
        except OSError as error:
            results.append(FileResult(path, FileStatus.READ_ERROR, "error", error=str(error)))
        except (UnicodeError, ValueError) as error:
            results.append(FileResult(path, FileStatus.INPUT_ERROR, "error", error=str(error), snapshot=snapshot))
        else:
            if operation is Operation.CHECK:
                status = FileStatus.UNCHANGED if source == output else FileStatus.MISMATCH
                results.append(FileResult(path, status, status.value.lower(), snapshot=snapshot))
            elif source == output:
                results.append(FileResult(path, FileStatus.UNCHANGED, "unchanged", snapshot=snapshot))
            else:
                prepared.append((path, source, output, snapshot))
    return files, results, prepared


def _complete_results(
    files: Sequence[Path],
    initial: Sequence[FileResult],
    prepared: Sequence[tuple[Path, bytes, bytes, FileSnapshot]],
    overrides: dict[Path, FileResult] | None = None,
) -> list[FileResult]:
    """Build exactly one result record for every discovered or explicit path."""
    by_path = {
        path: FileResult(path, FileStatus.FORMATTED, "formatted", output=output, snapshot=snapshot)
        for path, _, output, snapshot in prepared
    }
    by_path.update({result.path: result for result in initial})
    if overrides:
        by_path.update(overrides)
    return [by_path[path] for path in files]


def format_paths(paths: Sequence[Path], cwd: Path | None = None) -> OperationResult:
    """Format all operands, committing only after every file has been prepared."""
    files, results, prepared = _prepare(paths, cwd, Operation.FORMAT)
    if any(item.status in {FileStatus.INPUT_ERROR, FileStatus.READ_ERROR} for item in results):
        complete = _complete_results(files, results, prepared)
        return OperationResult(Operation.FORMAT, _operation_status(Operation.FORMAT, complete), tuple(complete), _diagnostics(complete), untouched=tuple(files))
    preflight_errors: dict[Path, FileResult] = {}
    for path, _, _, snapshot in prepared:
        if not _safe_destination(path, snapshot):
            preflight_errors[path] = FileResult(path, FileStatus.PREFLIGHT_ERROR, "error", error="destination changed, is not regular, or is read-only", snapshot=snapshot)
    if preflight_errors:
        complete = _complete_results(files, results, prepared, preflight_errors)
        return OperationResult(Operation.FORMAT, _operation_status(Operation.FORMAT, complete), tuple(complete), _diagnostics(complete), untouched=tuple(files))
    committed: list[Path] = []
    write_error: FileResult | None = None
    for path, _, output, snapshot in prepared:
        try:
            _replace(path, output, snapshot)
        except _PreflightFailure as error:
            write_error = FileResult(path, FileStatus.PREFLIGHT_ERROR, "error", error=str(error), snapshot=snapshot)
            break
        except OSError as error:
            write_error = FileResult(path, FileStatus.WRITE_ERROR, "error", error=str(error), snapshot=snapshot)
            break
        committed.append(path)
    untouched = tuple(path for path in files if path not in committed)
    overrides = {write_error.path: write_error} if write_error is not None else None
    complete = _complete_results(files, results, prepared, overrides)
    status = _operation_status(Operation.FORMAT, complete, committed)
    return OperationResult(Operation.FORMAT, status, tuple(complete), _diagnostics(complete), tuple(committed), untouched)


def check_paths(paths: Sequence[Path], cwd: Path | None = None) -> OperationResult:
    """Check operands against canonical output without changing them."""
    files, results, _ = _prepare(paths, cwd, Operation.CHECK)
    return OperationResult(Operation.CHECK, _operation_status(Operation.CHECK, results), tuple(sorted(results, key=lambda item: item.path)), _diagnostics(results), untouched=tuple(files))
