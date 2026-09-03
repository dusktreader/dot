from pathlib import Path
import os
import threading

import pytest

from dot_tools.markdown_formatter.models import FileStatus, OperationStatus
from dot_tools.markdown_formatter import operations
from dot_tools.markdown_formatter.operations import check_paths, format_paths


def test_collects_recursively_sorts_and_deduplicates(tmp_path: Path) -> None:
    (tmp_path / "z.md").write_bytes(b"# Z\n")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.md").write_bytes(b"# A\n")

    result = check_paths([Path("."), Path("z.md")], cwd=tmp_path)

    assert [file.path for file in result.files] == sorted([tmp_path / "z.md", nested / "a.md"])
    assert result.status is OperationStatus.SUCCESS


def test_deduplicates_lexical_path_aliases_without_resolving_symlinks(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    path.write_bytes(b"# X\n")
    (tmp_path / "a").mkdir()
    result = check_paths([Path("x.md"), Path("a/../x.md")], cwd=tmp_path)
    assert [file.path for file in result.files] == [path]


def test_zero_discovery_is_success_with_no_records(tmp_path: Path) -> None:
    result = check_paths([tmp_path], cwd=tmp_path)

    assert result.status is OperationStatus.SUCCESS
    assert result.files == ()
    assert result.diagnostics == ()
    assert result.committed == ()
    assert result.untouched == ()


def test_recursive_discovery_oserror_is_a_read_error_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_discovery(self: Path, pattern: str):
        raise OSError("discovery fail")

    monkeypatch.setattr(Path, "rglob", fail_discovery)

    result = check_paths([tmp_path])

    assert result.status is OperationStatus.READ_ERROR
    assert len(result.files) == 1
    assert result.files[0].status is FileStatus.READ_ERROR
    assert result.files[0].message == "error"
    assert result.files[0].output is None
    assert result.files[0].error == "discovery fail"
    assert result.diagnostics == (f"{tmp_path}: READ_ERROR: discovery fail",)


def test_format_preflights_all_files_before_writing(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_bytes(b"# Good\n")
    bad.write_bytes(b"not a heading\n")

    result = format_paths([good, bad])

    assert result.status is OperationStatus.INPUT_ERROR
    assert good.read_bytes() == b"# Good\n"
    assert result.committed == ()


def test_input_error_after_successful_read_retains_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "invalid.md"
    path.write_bytes(b"not a heading\n")

    result = check_paths([path])

    file_result = result.files[0]
    assert file_result.status is FileStatus.INPUT_ERROR
    assert file_result.output is None
    assert file_result.snapshot is not None
    assert file_result.snapshot.content == path.read_bytes()


def test_check_reports_digest_for_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# Title")

    result = check_paths([path])

    assert result.files[0].status is FileStatus.MISMATCH
    assert result.files[0].output is None
    assert "SHA-256" in result.diagnostics[0]
    assert b"# Title\n" not in result.diagnostics[0].encode()


def test_format_reports_prepared_and_error_paths_after_preflight_failure(tmp_path: Path) -> None:
    first = tmp_path / "a.md"
    second = tmp_path / "b.md"
    first.write_bytes(b"# A")
    second.write_bytes(b"# B")
    (second).chmod(0o444)

    result = format_paths([first, second])

    assert result.status is OperationStatus.PREFLIGHT_ERROR
    assert [file.path for file in result.files] == [first, second]
    assert [file.status for file in result.files] == [FileStatus.FORMATTED, FileStatus.PREFLIGHT_ERROR]
    assert result.committed == ()
    assert result.untouched == (first, second)
    assert result.files[0].output == b"# A\n"
    assert result.files[0].error is None
    assert result.files[1].output is None
    assert result.files[1].error is not None


def test_format_reports_failed_and_later_paths_after_first_write_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = tmp_path / "a.md"
    failed = tmp_path / "b.md"
    later = tmp_path / "c.md"
    for path in (first, failed, later):
        path.write_bytes(f"# {path.stem}".encode())

    def fail_second(path: Path, output: bytes, snapshot: object) -> None:
        if path == failed:
            raise OSError("simulated replacement failure")
        path.write_bytes(output)

    monkeypatch.setattr(operations, "_replace", fail_second)

    result = format_paths([later, failed, first])

    assert result.status is OperationStatus.PARTIAL_WRITE
    assert [item.path for item in result.files] == [first, failed, later]
    assert [item.status for item in result.files] == [FileStatus.FORMATTED, FileStatus.WRITE_ERROR, FileStatus.FORMATTED]
    assert result.files[0].output == b"# a\n"
    assert result.files[1].output is None
    assert result.files[2].output == b"# c\n"
    assert result.committed == (first,)
    assert result.untouched == (failed, later)
    assert result.diagnostics == (f"{failed}: WRITE_ERROR: simulated replacement failure",)


def test_format_revalidates_each_destination_immediately_before_replacement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = tmp_path / "a.md"
    later = tmp_path / "b.md"
    first.write_bytes(b"# a")
    later.write_bytes(b"# b")
    original_safe_destination = operations._safe_destination
    checks = 0

    def mutate_after_batch_preflight(path: Path, snapshot: object) -> bool:
        nonlocal checks
        checks += 1
        if checks == 3:
            later.write_bytes(b"concurrent edit")
        return original_safe_destination(path, snapshot)  # type: ignore[arg-type]

    monkeypatch.setattr(operations, "_safe_destination", mutate_after_batch_preflight)

    result = format_paths([first, later])

    assert result.status is OperationStatus.PREFLIGHT_ERROR
    assert result.committed == (first,)
    assert result.untouched == (later,)
    assert [item.status for item in result.files] == [FileStatus.FORMATTED, FileStatus.PREFLIGHT_ERROR]
    assert later.read_bytes() == b"concurrent edit"


def test_format_rejects_symlink_destination(tmp_path: Path) -> None:
    target = tmp_path / "target.md"
    path = tmp_path / "link.md"
    target.write_bytes(b"# target")
    path.symlink_to(target)

    result = format_paths([path])

    assert result.status is OperationStatus.PREFLIGHT_ERROR
    assert result.files[0].status is FileStatus.PREFLIGHT_ERROR
    assert path.is_symlink()
    assert target.read_bytes() == b"# target"


def test_competing_formatter_lock_attempt_is_serialized(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    replacement_started = threading.Event()
    competing_acquired = threading.Event()
    original_replace = operations.os.replace

    def slow_replace(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> None:
        replacement_started.set()
        assert not competing_acquired.wait(timeout=0.05)
        original_replace(source, destination)

    result_holder = []

    def format_in_thread() -> None:
        result_holder.append(format_paths([path]))

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(operations.os, "replace", slow_replace)
    formatter = threading.Thread(target=format_in_thread)
    formatter.start()
    assert replacement_started.wait(timeout=2)

    def competing_writer() -> None:
        with operations._destination_lock(path):
            competing_acquired.set()

    writer = threading.Thread(target=competing_writer)
    writer.start()
    formatter.join(timeout=2)
    writer.join(timeout=2)
    monkeypatch.undo()

    assert not formatter.is_alive()
    assert not writer.is_alive()
    assert result_holder[0].status is OperationStatus.SUCCESS
    assert competing_acquired.is_set()
    assert path.read_bytes() == b"# source\n"




def test_destination_mutation_before_lock_revalidation_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    snapshot = operations._snapshot(path, path.read_bytes())
    mutation_done = threading.Event()

    def competing_writer() -> None:
        with operations._destination_lock(path):
            path.write_bytes(b"# changed before validation\n")
            mutation_done.set()

    writer = threading.Thread(target=competing_writer)
    writer.start()
    assert mutation_done.wait(timeout=2)
    writer.join(timeout=2)

    with pytest.raises(operations._PreflightFailure):
        operations._replace(path, b"# formatted\n", snapshot)

    assert path.read_bytes() == b"# changed before validation\n"
    assert not list(tmp_path.glob("*.dt-tmp-*"))


def test_temp_collision_does_not_delete_preexisting_file(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    collision = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
    collision.write_bytes(b"unrelated")

    with pytest.raises(OSError):
        operations._replace(path, b"# formatted\n", operations._snapshot(path, path.read_bytes()))

    assert collision.read_bytes() == b"unrelated"


def test_temp_collision_reports_complete_write_failure_without_cleanup_side_effects(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    collision = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
    collision.write_bytes(b"unrelated")

    result = format_paths([path])

    assert result.status is OperationStatus.WRITE_ERROR
    assert len(result.files) == 1
    assert result.files[0].path == path
    assert result.files[0].status is FileStatus.WRITE_ERROR
    assert result.files[0].output is None
    assert result.files[0].error is not None
    assert result.committed == ()
    assert result.untouched == (path,)
    assert result.diagnostics == (f"{path}: WRITE_ERROR: [Errno 17] File exists: '{collision}'",)
    assert collision.read_bytes() == b"unrelated"


def test_fstat_failure_leaves_unverified_temp_path_untouched(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "doc.md"
    original = b"# source"
    path.write_bytes(original)

    def fail_fstat(fd: int) -> os.stat_result:
        raise OSError("fstat failure")

    monkeypatch.setattr(operations.os, "fstat", fail_fstat)
    result = format_paths([path])

    assert result.status is OperationStatus.WRITE_ERROR
    assert result.files[0].status is FileStatus.WRITE_ERROR
    assert path.read_bytes() == original
    temporary = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
    assert temporary.exists()


def test_fstat_failure_does_not_unlink_pathname_substitution_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    temporary = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
    sentinel = b"unrelated sentinel"

    def fail_fstat(fd: int) -> os.stat_result:
        temporary.unlink()
        temporary.write_bytes(sentinel)
        raise OSError("fstat failure")

    monkeypatch.setattr(operations.os, "fstat", fail_fstat)
    result = format_paths([path])

    assert result.status is OperationStatus.WRITE_ERROR
    assert result.files[0].status is FileStatus.WRITE_ERROR
    assert temporary.read_bytes() == sentinel


def test_successful_replace_is_not_changed_to_write_error_by_cleanup_lstat_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    temporary = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
    original_lstat = Path.lstat

    def fail_temporary_lstat(candidate: Path) -> os.stat_result:
        if candidate == temporary:
            raise OSError("cleanup lstat failure")
        return original_lstat(candidate)

    monkeypatch.setattr(Path, "lstat", fail_temporary_lstat)
    result = format_paths([path])

    assert result.status is OperationStatus.SUCCESS
    assert result.committed == (path,)
    assert result.untouched == ()
    assert result.files[0].status is FileStatus.FORMATTED
    assert path.read_bytes() == b"# source\n"


def test_replacement_error_is_not_masked_by_cleanup_lstat_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "doc.md"
    path.write_bytes(b"# source")
    temporary = path.with_name(f".{path.name}.dt-tmp-{os.getpid()}")
    original_lstat = Path.lstat

    def fail_replace(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> None:
        raise OSError("replacement failure")

    def fail_temporary_lstat(candidate: Path) -> os.stat_result:
        if candidate == temporary:
            raise OSError("cleanup lstat failure")
        return original_lstat(candidate)

    monkeypatch.setattr(operations.os, "replace", fail_replace)
    monkeypatch.setattr(Path, "lstat", fail_temporary_lstat)

    result = format_paths([path])

    assert result.status is OperationStatus.WRITE_ERROR
    assert result.files[0].error == "replacement failure"
    assert path.read_bytes() == b"# source"


@pytest.mark.parametrize("name", ["missing.md", "plain.txt"])
def test_duplicate_explicit_invalid_paths_have_one_record_and_diagnostic(tmp_path: Path, name: str) -> None:
    path = tmp_path / name
    for operation in (check_paths, format_paths):
        result = operation([path, Path(".") / name], cwd=tmp_path)

        assert [item.path for item in result.files] == [path]
        assert len(result.diagnostics) == 1
