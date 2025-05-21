from collections.abc import Generator
from pathlib import Path
from typing import cast

import git
import pytest

from dot_tools.exceptions import GitError
from dot_tools.git_tools import GitUrl, GitManager


class TestGitUrl:
    def test_parse_repo_url(self):

        parsed = GitUrl.parse('https://github.com/dusktreader/py-buzz.git')
        assert parsed.protocol == 'https'
        assert parsed.host == 'github.com'
        assert parsed.owner == 'dusktreader'
        assert parsed.repo == 'py-buzz'

        parsed = GitUrl.parse('git@github.com:dusktreader/py-buzz.git')
        assert parsed.protocol == 'ssh'
        assert parsed.host == 'github.com'
        assert parsed.owner == 'dusktreader'
        assert parsed.repo == 'py-buzz'

        with pytest.raises(GitError, match="Couldn't parse git url="):
            GitUrl.parse('/home/dusktreader/py-buzz/')


def init_empty_repo(path: Path) -> git.Repo:
    if not path.exists():
        path.mkdir(parents=True)
    repo = git.Repo.init(path)
    repo.index.commit("Initial Commit")
    return repo


def init_filled_repo(path: Path) -> git.Repo:
    repo = init_empty_repo(path)

    fake_readme = path / "README.md"
    fake_readme.write_text("# Fake Repo\n\nThis is a fake repo for testing purposes.")
    repo.index.add(str(fake_readme))
    repo.index.commit("Added README")

    fake_license = path / "LICENSE.md"
    fake_license.write_text("# Fuck It\n\nThis is a fake license for testing purposes.")
    other = repo.create_head("other")
    other.checkout()
    repo.index.add(str(fake_license))
    repo.index.commit("Added LICENSE")

    fake_make = path / "Makefile"
    fake_make.write_text("# This is a stupid Makefile for testing.")
    main = repo.heads["main"]
    main.checkout()
    repo.index.add(str(fake_make))
    repo.index.commit("Added Makefile")

    return repo


@pytest.fixture()
def fake_origin(tmp_path: Path) -> Generator[Path, None, None]:
    fake_root = tmp_path / "fake_origin"
    init_filled_repo(fake_root)
    yield fake_root


class TestGitManager:

    def test___init____with_provided_path(self, tmp_path: Path):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        test_path = fake_root / "jawa/ewok/hutt/pyke"
        test_path.mkdir(parents=True)

        git_man = GitManager(path=test_path)
        assert git_man.repo.working_dir == str(fake_root)

    def test___init____with_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        test_path = fake_root / "jawa/ewok/hutt/pyke"
        test_path.mkdir(parents=True)

        monkeypatch.chdir(test_path)
        git_man = GitManager(path=test_path)
        assert git_man.repo.working_dir == str(fake_root)

    def test___init____fails_if_no_repo_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        fake_root.mkdir()

        monkeypatch.chdir(fake_root)
        with pytest.raises(GitError, match="Path .* was not in a git repository"):
            GitManager()

    def test___init____fails_path_does_not_exist(self):
        fake_root = Path("jawa/ewok/hutt/pyke")

        with pytest.raises(GitError, match="Can't initialize GitManger with a path that doesn't exist"):
            GitManager(path=fake_root)

    def test_toplevel__works_in_subfolder(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        test_path = fake_root / "jawa/ewok/hutt/pyke"
        test_path.mkdir(parents=True)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        found_path = git_man.toplevel(start_path=test_path)
        assert found_path == fake_root

    def test_toplevel__works_in_root_folder(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        found_path = git_man.toplevel(start_path=fake_root)
        assert found_path == fake_root

    def test_toplevel__works_with_relative_flag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        test_path = fake_root / "jawa/ewok/hutt/pyke"
        test_path.mkdir(parents=True)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        found_path = git_man.toplevel(start_path=test_path, relative=True)
        assert found_path == Path("../../../..")

    def test_toplevel__works_with_no_start_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)
        test_path = fake_root / "jawa/ewok/hutt/pyke"
        test_path.mkdir(parents=True)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        monkeypatch.chdir(test_path)
        found_path = git_man.toplevel()
        assert found_path == fake_root

    def test_is_github_repo__returns_true_if_repo_is_cloned_from_github(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        repo = init_empty_repo(fake_root)
        repo.create_remote("origin", "git@github.com:duskterader/fake-project.git")

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        assert git_man.is_github_repo()

    def test_is_github_repo__returns_false_if_repo_is_cloned_from_another_provider(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        repo = init_empty_repo(fake_root)
        repo.create_remote("origin", "git@gitlab.com:duskterader/fake-project.git")

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        assert not git_man.is_github_repo()

    def test_is_github_repo__raises_error_if_repo_has_no_origin(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        repo = init_empty_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        with pytest.raises(GitError, match="Git repo has no remote named 'origin'"):
            git_man.is_github_repo()

    def test_checkout_new_branch__from_current_branch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        repo = init_filled_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        git_man.checkout_new_branch("test-branch")

        assert git_man.repo.active_branch.name == "test-branch"
        assert git_man.repo.active_branch.commit == repo.branches["main"].commit

        local_file = fake_root / "README.md"
        assert "fake repo" in local_file.read_text()

    def test_checkout_new_branch__from_named_branch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake_origin: Path):
        fake_root = tmp_path / "fake_root"
        fake_root.mkdir()
        repo = init_empty_repo(fake_root)
        remote = repo.create_remote("origin", str(fake_origin))
        infos = remote.fetch()
        origin_other = infos["origin/other"]
        repo.create_head("other", origin_other.commit.hexsha)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        git_man.checkout_new_branch("test-branch", base_name="other")

        assert git_man.repo.active_branch.name == "test-branch"
        assert git_man.repo.active_branch.commit == origin_other.commit

        local_file = fake_root / "README.md"
        assert "fake repo" in local_file.read_text()

        local_file = fake_root / "LICENSE.md"
        assert "Fuck It" in local_file.read_text()

    def test_checkout_new_branch__from_remote_branch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake_origin: Path):
        fake_root = tmp_path / "fake_root"
        fake_root.mkdir()
        repo = git.Repo.init(fake_root)
        repo.create_remote("origin", str(fake_origin))

        monkeypatch.chdir(fake_root)
        git_man = GitManager()
        git_man.checkout_new_branch("test-branch", base_name="other", remote_name="origin")
        assert git_man.repo.active_branch.name == "test-branch"

        local_file = fake_root / "README.md"
        assert "fake repo" in local_file.read_text()

        local_file = fake_root / "LICENSE.md"
        assert "Fuck It" in local_file.read_text()

    def test_checkout_branch_by_pattern__matches_one_local_branch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        repo = init_filled_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        git_man.checkout_branch_by_pattern("other")

        assert git_man.repo.active_branch.name == "other"
        assert git_man.repo.active_branch.commit == repo.branches["other"].commit

        local_file = fake_root / "LICENSE.md"
        assert "Fuck It" in local_file.read_text()


    def test_checkout_branch_by_pattern__matches_one_remote_branch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake_origin: Path):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()
        git_man.repo.create_remote("origin", str(fake_origin))

        git_man.checkout_branch_by_pattern("other")

        assert git_man.repo.active_branch.name == "other"

        local_file = fake_root / "LICENSE.md"
        assert "Fuck It" in local_file.read_text()

    def test_checkout_branch_by_pattern__matches_only_one_branch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake_origin: Path):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()
        remote = git_man.repo.create_remote("origin", str(fake_origin))
        fetch_info: git.FetchInfo = remote.fetch()["origin/other"]
        ref = GitError.ensure_type(fetch_info.ref, git.RemoteReference, f"Expected type {git.RemoteReference}, got {type(fetch_info.ref)}")
        git_man.repo.create_head(ref.remote_head, ref)
        origin = git.Repo(fake_origin)
        readme = fake_origin / "README.md"
        readme.write_text("NEW TEXT")
        origin.index.add(str(readme))
        origin.index.commit("New README text")

        git_man.checkout_branch_by_pattern("gin/oth")

        assert git_man.repo.active_branch.name == "other"

        assert "NEW TEXT" == readme.read_text()

    def test_checkout_branch_by_pattern__raises_error_on_multiple_matches(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_filled_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()
        git_man.repo.create_head("moth")

        with pytest.raises(GitError, match="Couldn't find exactly one branch"):
            git_man.checkout_branch_by_pattern("oth")

    def test_checkout_branch_by_pattern__raises_error_on_zero_matches(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        fake_root = tmp_path / "fake_root"
        init_empty_repo(fake_root)

        monkeypatch.chdir(fake_root)
        git_man = GitManager()

        with pytest.raises(GitError, match="Couldn't find exactly one branch"):
            git_man.checkout_branch_by_pattern("other")
