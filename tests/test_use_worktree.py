import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest


SCRIPT = Path(__file__).parents[1] / ".agents" / "tools" / "use-worktree.py"


def load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("use_worktree", SCRIPT)
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


def test_creates_worktree_and_returns_handoff(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = init_repo(tmp_path / "repo")
    navigation = tmp_path / "navigation"
    monkeypatch.setenv("DT_NAVIGATION_FILE", str(navigation))

    result = load_tool().use_worktree("Add retry logic", "feat", "ABC-123", root)

    expected_branch = "feat/ABC-123--add-retry-logic"
    expected_path = root / ".worktrees" / expected_branch
    assert result["action"] == "created"
    assert result["branch"] == expected_branch
    assert result["parent_branch"] == "main"
    assert result["worktree"] == str(expected_path)
    assert result["worktree_created"] is True
    assert navigation.read_text().strip() == str(expected_path)
    assert run_git(expected_path, "branch", "--show-current") == expected_branch


def test_rejects_non_main_project_root(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    run_git(root, "branch", "feature/current")
    run_git(root, "checkout", "feature/current")

    with pytest.raises(load_tool().WorktreeError, match="Switch it to main or master"):
        load_tool().use_worktree("Add retry logic", "feat", "ABC-123", root)


def test_returns_to_project_root_then_creates_requested_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = init_repo(tmp_path / "repo")
    other_path = root / ".worktrees" / "feat" / "other-task"
    other_path.parent.mkdir(parents=True)
    run_git(root, "worktree", "add", "-b", "feat/other-task", str(other_path))
    navigation = tmp_path / "navigation"
    monkeypatch.setenv("DT_NAVIGATION_FILE", str(navigation))

    result = load_tool().use_worktree("Add retry logic", "feat", "ABC-123", other_path)

    expected_path = root / ".worktrees" / "feat" / "ABC-123--add-retry-logic"
    assert result["action"] == "created"
    assert result["parent_worktree"] == str(root)
    assert result["parent_branch"] == "main"
    assert result["worktree"] == str(expected_path)
    assert navigation.read_text().strip() == str(expected_path)


def test_resumes_matching_dirty_worktree_without_pulling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = init_repo(tmp_path / "repo")
    branch = "feat/ABC-123--add-retry-logic"
    worktree = root / ".worktrees" / branch
    worktree.parent.mkdir(parents=True)
    run_git(root, "worktree", "add", "-b", branch, str(worktree))
    (worktree / "uncommitted.txt").write_text("keep this\n")
    navigation = tmp_path / "navigation"
    monkeypatch.setenv("DT_NAVIGATION_FILE", str(navigation))

    result = load_tool().use_worktree("Add retry logic", "feat", "ABC-123", worktree)

    assert result["action"] == "resumed"
    assert result["worktree_created"] is False
    assert "uncommitted changes" in result["error"]
    assert navigation.read_text().strip() == str(worktree)
