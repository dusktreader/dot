"""Verify the public formatter models and grouped command contract."""

import hashlib
from pathlib import Path
from typing import get_type_hints

from typer.testing import CliRunner

from dot_tools.cli.main import cli
from dot_tools.markdown_formatter import check_document, format_document
from dot_tools.markdown_formatter import operations
from dot_tools.markdown_formatter.models import (
    FileResult,
    FileSnapshot,
    FileStatus,
    Operation,
    OperationResult,
    OperationStatus,
)
from dot_tools.markdown_formatter.operations import check_paths, format_paths


def test_public_models_and_callable_signatures_are_stable() -> None:
    assert set(FileStatus) == {
        FileStatus.FORMATTED, FileStatus.UNCHANGED, FileStatus.MISMATCH,
        FileStatus.INPUT_ERROR, FileStatus.READ_ERROR, FileStatus.PREFLIGHT_ERROR, FileStatus.WRITE_ERROR,
    }
    assert set(OperationStatus) == {
        OperationStatus.SUCCESS, OperationStatus.MISMATCH, OperationStatus.INPUT_ERROR,
        OperationStatus.READ_ERROR, OperationStatus.PREFLIGHT_ERROR, OperationStatus.PARTIAL_WRITE,
        OperationStatus.WRITE_ERROR,
    }
    assert set(Operation) == {Operation.FORMAT, Operation.CHECK}
    assert list(get_type_hints(FileResult)) == ["path", "status", "message", "output", "error", "snapshot"]
    assert list(get_type_hints(OperationResult)) == ["operation", "status", "files", "diagnostics", "committed", "untouched"]
    assert format_document(b"# Title\n") == b"# Title\n"
    assert check_document(b"# Title") == b"# Title\n"
    assert format_paths.__annotations__["paths"]
    assert check_paths.__annotations__["cwd"]
    snapshot = FileSnapshot(b"x", hashlib.sha256(b"x").hexdigest(), 1, 2, 0o644, 0o100000)
    assert snapshot.content == b"x"


def test_format_and_check_have_exact_records_streams_and_exit_codes(tmp_path: Path) -> None:
    canonical = tmp_path / "a.md"
    mismatch = tmp_path / "b.md"
    canonical.write_bytes(b"# A\n")
    mismatch.write_bytes(b"# B")
    runner = CliRunner(mix_stderr=False)

    formatted = runner.invoke(cli, ["markdown", "format", str(mismatch)])
    assert formatted.exit_code == 0
    assert formatted.stdout == f"FORMATTED {mismatch}\nsummary format SUCCESS 1\n"
    assert formatted.stderr == ""

    checked = runner.invoke(cli, ["markdown", "check", str(canonical), str(mismatch)])
    assert checked.exit_code == 0
    assert checked.stdout == f"UNCHANGED {canonical}\nUNCHANGED {mismatch}\nsummary check SUCCESS 2\n"


def test_check_mismatch_has_digest_only_diagnostic_and_exit_one(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    source = b"# Title"
    path.write_bytes(source)

    result = CliRunner(mix_stderr=False).invoke(cli, ["markdown", "check", str(path)])

    expected = hashlib.sha256(b"# Title\n").hexdigest()
    actual = hashlib.sha256(source).hexdigest()
    assert result.exit_code == 1
    assert result.stdout == f"MISMATCH {path}\nsummary check MISMATCH 1\n"
    assert result.stderr == f"{path}: mismatch: expected SHA-256 {expected}, actual SHA-256 {actual}\n"
    assert "# Title" not in result.stderr


def test_input_error_is_reported_on_stderr_and_has_exit_two(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"

    result = CliRunner(mix_stderr=False).invoke(cli, ["markdown", "check", str(missing)])

    assert result.exit_code == 2
    assert result.stdout == f"INPUT_ERROR {missing}\nsummary check INPUT_ERROR 1\n"
    assert result.stderr == f"{missing}: INPUT_ERROR: path does not exist\n"


def test_mixed_outcome_precedence_prefers_input_over_mismatch(tmp_path: Path) -> None:
    mismatch = tmp_path / "mismatch.md"
    mismatch.write_bytes(b"# Title")
    missing = tmp_path / "missing.md"

    result = check_paths([mismatch, missing])

    assert result.status is OperationStatus.INPUT_ERROR
    assert [item.status for item in result.files] == [FileStatus.MISMATCH, FileStatus.INPUT_ERROR]


def test_zero_file_operation_is_success_with_empty_records(tmp_path: Path) -> None:
    result = check_paths([tmp_path / "empty"], cwd=tmp_path)

    assert result.status is OperationStatus.INPUT_ERROR
    assert len(result.files) == 1


def test_format_partial_write_has_sorted_records_and_streams(tmp_path: Path, monkeypatch) -> None:
    paths = [tmp_path / name for name in ("a.md", "b.md", "c.md")]
    for path in paths:
        path.write_bytes(f"# {path.stem}".encode())

    def fail_second(path: Path, output: bytes, snapshot: object) -> None:
        if path == paths[1]:
            raise OSError("simulated replacement failure")
        path.write_bytes(output)

    monkeypatch.setattr(operations, "_replace", fail_second)

    result = CliRunner(mix_stderr=False).invoke(cli, ["markdown", "format", *(str(path) for path in paths)])

    assert result.exit_code == 3
    assert result.stdout == (
        f"FORMATTED {paths[0]}\nWRITE_ERROR {paths[1]}\nFORMATTED {paths[2]}\n"
        "summary format PARTIAL_WRITE 3\n"
    )
    assert result.stderr == f"{paths[1]}: WRITE_ERROR: simulated replacement failure\n"
