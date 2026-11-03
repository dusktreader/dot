import importlib.util
import subprocess
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest


SCRIPT = Path(__file__).parents[1] / ".agents" / "tools" / "create-artifact-dir.py"


def load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("create_artifact_dir", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(path: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=path, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    run_git(path, "init", "--initial-branch=main")
    run_git(path, "config", "user.name", "Test User")
    run_git(path, "config", "user.email", "test@example.com")
    (path / "README").write_text("test\n")
    run_git(path, "add", "README")
    run_git(path, "commit", "-m", "Initial commit")
    return path


def checkout_branch(path: Path, branch: str) -> None:
    run_git(path, "checkout", "-b", branch)


def test_creates_dated_directory_from_worktree_inputs(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    checkout_branch(root, "fix/incorrect-branch-label")
    tool = load_tool()

    artifact_dir = tool.create_artifact_dir("Close leak", tool.BranchType.fix, "ABC-123", root, date(2026, 6, 26))

    assert artifact_dir == root / ".artifacts" / "20260626--fix--ABC-123--close-leak"
    assert artifact_dir.is_dir()


def test_rejects_invalid_ticket(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    tool = load_tool()

    with pytest.raises(tool.ArtifactDirectoryError, match="Ticket must contain only"):
        tool.create_artifact_dir("Close leak", tool.BranchType.fix, "ABC 123", root)


def test_finds_worktree_root_from_nested_directory(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    nested = root / ".agents" / "procedures"
    nested.mkdir(parents=True)
    tool = load_tool()

    artifact_dir = tool.create_artifact_dir("Add retry", tool.BranchType.feat, "ABC-123", nested, date(2026, 6, 26))

    assert artifact_dir == root / ".artifacts" / "20260626--feat--ABC-123--add-retry"


def test_reuses_existing_directory_on_later_date(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    tool = load_tool()

    first = tool.create_artifact_dir("Improve output", tool.BranchType.chore, "ABC-123", root, date(2026, 6, 26))
    second = tool.create_artifact_dir("Improve output", tool.BranchType.chore, "ABC-123", root, date(2026, 6, 27))

    assert second == first
    assert list((root / ".artifacts").iterdir()) == [first]


def test_rejects_multiple_directories_for_same_task(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    artifact_root = root / ".artifacts"
    first = artifact_root / "20260625--fix--ABC-123--close-leak"
    second = artifact_root / "20260626--fix--ABC-123--close-leak"
    first.mkdir(parents=True)
    second.mkdir()
    tool = load_tool()

    with pytest.raises(tool.ArtifactDirectoryError, match="Multiple artifact directories"):
        tool.create_artifact_dir("Close leak", tool.BranchType.fix, "ABC-123", root, date(2026, 6, 27))
