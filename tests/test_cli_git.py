from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from dot_tools.cli.git import cli
from dot_tools.exceptions import GitError

from tests.test_git_tools import init_empty_repo, init_conflicted_repo


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestToplevel:

    def test_toplevel__prints_repo_root(self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        monkeypatch.chdir(fake_root)

        result = runner.invoke(cli, ["toplevel"])
        assert result.exit_code == 0
        assert str(fake_root) in result.output

    def test_toplevel__prints_relative_path_with_flag(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        subdir = fake_root / "a/b"
        subdir.mkdir(parents=True)
        monkeypatch.chdir(subdir)

        result = runner.invoke(cli, ["toplevel", "--relative"])
        assert result.exit_code == 0
        assert "../.." in result.output

    def test_toplevel__fails_outside_git_repo(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli, ["toplevel"])
        assert result.exit_code != 0


class TestCrack:

    def test_crack__calls_resolve_conflicts(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        fake_root = tmp_path / "conflicted"
        init_conflicted_repo(fake_root)
        monkeypatch.chdir(fake_root)

        with patch("dot_tools.git_tools.subprocess.call"):
            result = runner.invoke(cli, ["crack"])
        assert result.exit_code == 0

    def test_crack__fails_when_no_conflicts(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        fake_root = tmp_path / "clean"
        init_empty_repo(fake_root)
        monkeypatch.chdir(fake_root)

        result = runner.invoke(cli, ["crack"])
        assert result.exit_code != 0


class TestCojira:

    def test_cojira__checks_out_matching_branch(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        from tests.test_git_tools import init_filled_repo
        fake_root = tmp_path / "fake_root"
        init_filled_repo(fake_root)
        monkeypatch.chdir(fake_root)

        result = runner.invoke(cli, ["cojira", "other"])
        assert result.exit_code == 0

    def test_cojira__fails_on_no_match(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        monkeypatch.chdir(fake_root)

        result = runner.invoke(cli, ["cojira", "nonexistent"])
        assert result.exit_code != 0


class TestIssue:

    def test_issue__always_raises_not_implemented(self, runner: CliRunner):
        with patch("dot_tools.cli.git.JiraManager") as mock_jira_cls:
            mock_jira = MagicMock()
            mock_jira_cls.return_value = mock_jira
            result = runner.invoke(cli, ["issue", "JAWA-9999"],
                                   env={"TYPERDRIVE_APP_NAME": "test"})
        assert result.exit_code != 0
