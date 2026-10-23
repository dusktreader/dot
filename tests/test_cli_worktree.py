from pathlib import Path

import git
import pytest
from typer.testing import CliRunner

from dot_tools.cli.main import cli
from dot_tools.worktree_tools import BranchType, build_branch_name, parameterize_summary


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.mark.parametrize("group", ["worktree", "worktrees"])
def test_worktree_group_shows_help_without_subcommand(group: str, runner: CliRunner) -> None:
    result = runner.invoke(cli, [group])

    assert "Create and manage repository worktrees" in result.output
    assert "make" in result.output
    assert "grab" in result.output
    assert "jump" in result.output
    assert "list" in result.output
    assert "drop" in result.output
    assert "root" in result.output


def init_repo(path: Path) -> git.Repo:
    path.mkdir(parents=True)
    repo = git.Repo.init(path)
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")
    readme = path / "README"
    readme.write_text("test\n")
    repo.index.add([str(readme)])
    repo.index.commit("Initial commit")
    return repo


def add_worktree(repo: git.Repo, path: Path, branch: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    repo.git.worktree("add", "-b", branch, str(path))


def test_list_displays_worktree_branches_and_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    repo = init_repo(root)
    first_path = root / ".worktrees" / "feat" / "mud-first"
    second_path = root / ".worktrees" / "fix" / "mud-second"
    add_worktree(repo, first_path, "feat/mud-first")
    add_worktree(repo, second_path, "fix/mud-second")
    monkeypatch.chdir(root)

    result = runner.invoke(cli, ["worktree", "list"])

    assert result.exit_code == 0, result.output
    assert "Branch" in result.output
    assert "Path" in result.output
    assert "feat/mud-first" in result.output
    assert str(first_path.relative_to(root)) in result.output
    assert "fix/mud-second" in result.output
    assert str(second_path.relative_to(root)) in result.output


def test_list_reports_when_no_worktrees_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)

    result = runner.invoke(cli, ["worktree", "list"])

    assert result.exit_code == 0, result.output
    assert "No worktrees found" in result.output


def test_parameterize_summary_normalizes_and_truncates() -> None:
    summary = "Foo the Mud Shark " + "x" * 100

    result = parameterize_summary(summary)

    assert len(result) == 80
    assert result.startswith("foo-the-mud-shark-")


def test_build_branch_name_includes_optional_ticket() -> None:
    assert build_branch_name(BranchType.chore, "foo the mud shark", "FUS-999") == (
        "chore/FUS-999--foo-the-mud-shark"
    )


def test_make_creates_branch_and_worktree_and_requests_navigation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    repo = init_repo(root)
    monkeypatch.chdir(root)
    navigation_file = tmp_path / "navigation"

    result = runner.invoke(
        cli,
        ["worktree", "make", "--type=chore", "--ticket=FUS-999", "foo", "the", "mud", "shark"],
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    expected_branch = "chore/FUS-999--foo-the-mud-shark"
    expected_path = root / ".worktrees" / expected_branch
    assert result.exit_code == 0, result.output
    assert expected_branch in repo.heads
    assert expected_path.is_dir()
    assert navigation_file.read_text().strip() == str(expected_path)


def test_grab_uses_matching_local_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    repo = init_repo(root)
    branch = "feat/foo-mud-shark"
    repo.create_head(branch)
    monkeypatch.chdir(root)

    result = runner.invoke(cli, ["worktree", "grab", "foo", "mud", "shark"])

    worktree_path = root / ".worktrees" / branch
    assert result.exit_code == 0, result.output
    assert worktree_path.is_dir()
    assert git.Repo(worktree_path).active_branch.name == branch
    assert repo.heads[branch].commit == repo.head.commit


def test_grab_uses_origin_branch_when_no_local_branch_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    repo = init_repo(root)
    remote_path = tmp_path / "origin.git"
    git.Repo.init(remote_path, bare=True)
    repo.create_remote("origin", str(remote_path))
    branch = "feat/foo-mud-shark"
    repo.create_head(branch)
    repo.git.push("origin", branch)
    repo.delete_head(branch, force=True)
    monkeypatch.chdir(root)

    result = runner.invoke(cli, ["worktree", "grab", "foo", "mud", "shark"])

    worktree_path = root / ".worktrees" / branch
    assert result.exit_code == 0, result.output
    assert worktree_path.is_dir()
    assert git.Repo(worktree_path).active_branch.name == branch
    tracking_branch = repo.heads[branch].tracking_branch()
    assert tracking_branch is not None
    assert tracking_branch.name == f"origin/{branch}"
    assert repo.heads[branch].commit == repo.commit(f"origin/{branch}")


def test_grab_prompts_to_select_from_matching_local_and_remote_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    repo = init_repo(root)
    local_branch = "feat/foo-alpha-shark"
    remote_branch = "feat/foo-beta-shark"
    repo.create_head(local_branch)
    remote_path = tmp_path / "origin.git"
    git.Repo.init(remote_path, bare=True)
    repo.create_remote("origin", str(remote_path))
    repo.create_head(remote_branch)
    repo.git.push("origin", remote_branch)
    repo.delete_head(remote_branch, force=True)
    monkeypatch.chdir(root)

    result = runner.invoke(
        cli,
        ["worktree", "grab", "foo", "shark"],
        input="2\n",
    )

    worktree_path = root / ".worktrees" / remote_branch
    assert result.exit_code == 0, result.output
    assert "Select an existing branch" in result.output
    assert f"{local_branch} (local)" in result.output
    assert f"origin/{remote_branch} (remote)" in result.output
    assert worktree_path.is_dir()
    assert git.Repo(worktree_path).active_branch.name == remote_branch
    tracking_branch = repo.heads[remote_branch].tracking_branch()
    assert tracking_branch is not None
    assert tracking_branch.name == f"origin/{remote_branch}"


def test_make_defaults_to_feat_and_rejects_unknown_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)

    result = runner.invoke(cli, ["worktrees", "make", "foo", "mud", "shark"])

    assert result.exit_code == 0, result.output
    assert (root / ".worktrees" / "feat" / "foo-mud-shark").is_dir()

    invalid = runner.invoke(cli, ["worktree", "make", "--type=unknown", "summary"])
    assert invalid.exit_code != 0


def test_jump_fuzzy_matches_worktree_branch_and_requests_navigation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)
    worktree_path = root / ".worktrees" / "feat" / "foo-mud-shark"
    add_worktree(git.Repo(root), worktree_path, "feat/foo-mud-shark")
    navigation_file = tmp_path / "navigation"

    result = runner.invoke(
        cli,
        ["jump", "fms"],
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    assert result.exit_code == 0, result.output
    assert navigation_file.read_text().strip() == str(worktree_path)


def test_jump_matches_ticket_without_punctuation_and_requests_navigation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)
    worktree_path = root / ".worktrees" / "chore" / "FUS-999--foo-the-mud-shark"
    add_worktree(git.Repo(root), worktree_path, "chore/FUS-999--foo-the-mud-shark")
    navigation_file = tmp_path / "navigation"

    result = runner.invoke(
        cli,
        ["jump", "fus999"],
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    assert result.exit_code == 0, result.output
    assert navigation_file.read_text().strip() == str(worktree_path)


def test_jump_uses_picker_when_multiple_worktrees_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)
    first = root / ".worktrees" / "feat" / "mud-first"
    second = root / ".worktrees" / "fix" / "mud-second"
    add_worktree(git.Repo(root), first, "feat/mud-first")
    add_worktree(git.Repo(root), second, "fix/mud-second")
    navigation_file = tmp_path / "navigation"
    monkeypatch.setattr("dot_tools.worktree_tools.shutil.which", lambda _: None)

    result = runner.invoke(
        cli,
        ["worktree", "jump", "mud"],
        input="2\n",
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    assert result.exit_code == 0, result.output
    assert "Select a worktree" in result.output
    assert navigation_file.read_text().strip() == str(second)


def test_drop_confirms_removes_worktree_and_navigates_to_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)
    worktree_path = root / ".worktrees" / "feat" / "mud-shark"
    add_worktree(git.Repo(root), worktree_path, "feat/mud-shark")
    navigation_file = tmp_path / "navigation"

    result = runner.invoke(
        cli,
        ["worktree", "drop", "mud", "--branch"],
        input="y\n",
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    assert result.exit_code == 0, result.output
    assert not worktree_path.exists()
    assert "feat/mud-shark" not in git.Repo(root).heads
    assert navigation_file.read_text().strip() == str(root)


def test_drop_declined_keeps_worktree_and_does_not_navigate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.chdir(root)
    worktree_path = root / ".worktrees" / "feat" / "mud-shark"
    add_worktree(git.Repo(root), worktree_path, "feat/mud-shark")
    navigation_file = tmp_path / "navigation"

    result = runner.invoke(
        cli,
        ["drop", "mud"],
        input="n\n",
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    assert result.exit_code != 0
    assert worktree_path.is_dir()
    assert not navigation_file.exists()


def test_root_requests_project_root_navigation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    subdirectory = root / "nested"
    subdirectory.mkdir()
    monkeypatch.chdir(subdirectory)
    navigation_file = tmp_path / "navigation"

    result = runner.invoke(
        cli,
        ["worktree", "root"],
        env={"DT_NAVIGATION_FILE": str(navigation_file)},
    )

    assert result.exit_code == 0, result.output
    assert navigation_file.read_text().strip() == str(root)
