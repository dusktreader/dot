import pytest

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import DotError


class TestGitManager:

    def test_parse_repo_url(self):
        git_man = GitManager()

        parsed_url = git_man.parse_repo_url(url='https://github.com/dusktreader/py-buzz.git')
        assert parsed_url.protocol == 'https'
        assert parsed_url.domain == 'github.com'
        assert parsed_url.owner == 'dusktreader'
        assert parsed_url.repo == 'py-buzz'

        parsed_url = git_man.parse_repo_url(url='git@github.com:dusktreader/py-buzz.git')
        assert parsed_url.protocol == 'ssh'
        assert parsed_url.domain == 'github.com'
        assert parsed_url.owner == 'dusktreader'
        assert parsed_url.repo == 'py-buzz'

        with pytest.raises(DotError) as err_info:
            git_man.parse_repo_url(url='/home/dusktreader/py-buzz/')
        assert "Couldn't parse url" in str(err_info.value)
