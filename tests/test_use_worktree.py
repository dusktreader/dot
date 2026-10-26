import json
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / ".agents" / "tools" / "create-agent-worktree.py"


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


def create_agent_worktree(root: Path, workflow: str = "task") -> dict[str, object]:
    parent_branch = run_git(root, "branch", "--show-current")
    parent_base = run_git(root, "rev-parse", "HEAD")
    result = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repository",
            str(root),
            "--parent-worktree",
            str(root),
            "--parent-branch",
            parent_branch,
            "--parent-base",
            parent_base,
            "--workflow",
            workflow,
            "--type",
            "feat",
            "--task-id",
            "ABC-123",
            "--slug",
            "add-retry-logic",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_creates_regular_branch_and_worktree_from_main(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")

    result = create_agent_worktree(root)

    expected_branch = "feat/ABC-123--add-retry-logic"
    expected_path = root / ".worktrees" / expected_branch
    assert result["agent_branch"] == expected_branch
    assert result["parent_branch"] == "main"
    assert result["agent_worktree"] == str(expected_path)
    assert result["worktree_created"] is True
    assert run_git(expected_path, "branch", "--show-current") == expected_branch


def test_reuses_regular_branch_without_creating_another_worktree(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    run_git(root, "checkout", "-b", "feat/current")

    result = create_agent_worktree(root, "feature")

    assert result["agent_branch"] == "feat/current"
    assert result["agent_worktree"] == str(root)
    assert result["worktree_created"] is False
    assert run_git(root, "worktree", "list", "--porcelain").count("worktree ") == 1


def test_uses_next_branch_suffix_when_requested_branch_exists(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    run_git(root, "branch", "feat/ABC-123--add-retry-logic")

    result = create_agent_worktree(root)

    expected_branch = "feat/ABC-123--add-retry-logic-02"
    assert result["agent_branch"] == expected_branch
    assert (root / ".worktrees" / expected_branch).is_dir()


def test_rejects_parent_worktree_that_is_not_repository_root(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    other_path = tmp_path / "other"
    other_path.mkdir()
    parent_base = run_git(root, "rev-parse", "HEAD")

    result = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--repository",
            str(root),
            "--parent-worktree",
            str(other_path),
            "--parent-branch",
            "main",
            "--parent-base",
            parent_base,
            "--workflow",
            "task",
            "--type",
            "feat",
            "--task-id",
            "ABC-123",
            "--slug",
            "add-retry-logic",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "parent worktree must be the repository root" in result.stderr
