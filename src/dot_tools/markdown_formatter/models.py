"""Public result models for Markdown formatting operations."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class FileStatus(StrEnum):
    FORMATTED = "FORMATTED"
    UNCHANGED = "UNCHANGED"
    MISMATCH = "MISMATCH"
    INPUT_ERROR = "INPUT_ERROR"
    READ_ERROR = "READ_ERROR"
    PREFLIGHT_ERROR = "PREFLIGHT_ERROR"
    WRITE_ERROR = "WRITE_ERROR"


class OperationStatus(StrEnum):
    SUCCESS = "SUCCESS"
    MISMATCH = "MISMATCH"
    INPUT_ERROR = "INPUT_ERROR"
    READ_ERROR = "READ_ERROR"
    PREFLIGHT_ERROR = "PREFLIGHT_ERROR"
    PARTIAL_WRITE = "PARTIAL_WRITE"
    WRITE_ERROR = "WRITE_ERROR"


class Operation(StrEnum):
    FORMAT = "format"
    CHECK = "check"


@dataclass(frozen=True)
class FileSnapshot:
    """Capture the destination state used to protect an atomic replacement."""

    content: bytes
    digest: str
    device: int
    inode: int
    mode: int
    file_type: int


@dataclass(frozen=True)
class FileResult:
    """Describe one file's formatting result."""

    path: Path
    status: FileStatus
    message: str
    output: bytes | None = None
    error: str | None = None
    snapshot: FileSnapshot | None = None


@dataclass(frozen=True)
class OperationResult:
    """Describe a complete format or check operation."""

    operation: Operation
    status: OperationStatus
    files: tuple[FileResult, ...]
    diagnostics: tuple[str, ...] = ()
    committed: tuple[Path, ...] = ()
    untouched: tuple[Path, ...] = ()
