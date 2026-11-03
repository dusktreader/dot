import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner


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


def test_switch_creates_worktree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = init_repo(tmp_path / "repo")
    navigation = tmp_path / "navigation"
    monkeypatch.setenv("DT_NAVIGATION_FILE", str(navigation))
    monkeypatch.chdir(root)

    result = CliRunner().invoke(
        load_tool().app, ["switch", "Add retry logic", "--type", "feat", "--ticket", "ABC-123"]
    )

    expected_branch = "feat/ABC-123--add-retry-logic"
    expected_path = root / ".worktrees" / expected_branch
    assert result.exit_code == 0, result.output
    assert "Created worktree" in result.output
    assert run_git(expected_path, "branch", "--show-current") == expected_branch
    assert navigation.read_text().strip() == str(expected_path)


def test_switch_reuses_existing_worktree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = init_repo(tmp_path / "repo")
    branch = "feat/ABC-123--add-retry-logic"
    worktree = root / ".worktrees" / branch
    worktree.parent.mkdir(parents=True)
    run_git(root, "worktree", "add", "-b", branch, str(worktree))
    (worktree / "uncommitted.txt").write_text("keep this\n")
    navigation = tmp_path / "navigation"
    monkeypatch.setenv("DT_NAVIGATION_FILE", str(navigation))
    monkeypatch.chdir(root)

    result = CliRunner().invoke(
        load_tool().app, ["switch", "Add retry logic", "--type", "feat", "--ticket", "ABC-123"]
    )

    assert result.exit_code == 0, result.output
    assert "Using existing worktree" in result.output
    assert (worktree / "uncommitted.txt").exists()
    assert navigation.read_text().strip() == str(worktree)


def test_search_finds_similar_branch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = init_repo(tmp_path / "repo")
    run_git(root, "branch", "feat/ABC-123--add-retry-logic")
    monkeypatch.chdir(root)

    result = CliRunner().invoke(load_tool().app, ["search", "Add retry logic", "--ticket", "ABC-123"])

    assert result.exit_code == 0, result.output
    assert "feat/ABC-123--add-retry-logic" in result.output
