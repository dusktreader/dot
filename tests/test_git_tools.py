import pytest

from dot_tools.git_tools import GitManager, GitError
from dot_tools.misc_tools import DotError


class TestGitManager:

    def test_parse_repo_url(self):
        git_man = GitManager()

        parsed_url = git_man.parse_repo_url(url='https://github.com/dusktreader/py-buzz.git')
        assert parsed_url.protocol == 'https'
        assert parsed_url.resource == 'github.com'
        assert parsed_url.owner == 'dusktreader'
        assert parsed_url.name == 'py-buzz'

        parsed_url = git_man.parse_repo_url(url='git@github.com:dusktreader/py-buzz.git')
        assert parsed_url.protocol == 'ssh'
        assert parsed_url.resource == 'github.com'
        assert parsed_url.owner == 'dusktreader'
        assert parsed_url.name == 'py-buzz'

        with pytest.raises(DotError) as err_info:
            git_man.parse_repo_url(url='/home/dusktreader/py-buzz/')
        assert "Couldn't parse url" in str(err_info.value)

    def test_find_source_path__success(self, tmp_path):
        fake_root = tmp_path / "fake_root"
        fake_root.mkdir()
        fake_root.joinpath("test.py").write_text("# dummy")
        fake_root.joinpath("non_package").mkdir()
        fake_root.joinpath("tests").mkdir()
        fake_root.joinpath("tests").joinpath("__init__.py").write_text("# test file")
        fake_root.joinpath("package").mkdir()
        fake_root.joinpath("package").joinpath("__init__.py").write_text("# package file")

        git_man = GitManager()
        found_path = git_man.find_source_path(str(fake_root))
        assert found_path == str(fake_root.joinpath("package"))

    def test_find_source_path__fails_if_it_finds_more_than_one_source_directory(self, tmp_path):
        fake_root = tmp_path / "fake_root"
        fake_root.mkdir()
        fake_root.joinpath("test.py").write_text("# dummy")
        fake_root.joinpath("other_package").mkdir()
        fake_root.joinpath("other_package").joinpath("__init__.py").write_text("# other package file")
        fake_root.joinpath("tests").mkdir()
        fake_root.joinpath("tests").joinpath("__init__.py").write_text("# test file")
        fake_root.joinpath("package").mkdir()
        fake_root.joinpath("package").joinpath("__init__.py").write_text("# package file")

        git_man = GitManager()
        with pytest.raises(GitError, match="Could not find one and only one source package"):
            git_man.find_source_path(str(fake_root))
