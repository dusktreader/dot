import pytest
import pytest_mock

from dot_tools.exceptions import JiraError
from dot_tools.jira_tools import JiraManager
from dot_tools.settings import JiraInfo


def test_jira_key__matches_jira_pattern():
    branch_name = "JAWA-9999--utinni"
    assert JiraManager.jira_key(branch_name) == "JAWA-9999"

    branch_name = "feat/HUTT-0000--oona-goota-solo"
    assert JiraManager.jira_key(branch_name) == "HUTT-0000"


def test_jira_key__errors_if_no_pattern_matched():
    branch_name = "jawa-XXXX--utinni"
    with pytest.raises(JiraError, match="Can't extract a JIRA key"):
        JiraManager.jira_key(branch_name)

    branch_name = "feat/fix/HUTT-0000--oona-goota-solo"
    with pytest.raises(JiraError, match="Can't extract a JIRA key"):
        JiraManager.jira_key(branch_name)


def test_get_issue_from_jira__fetches_issue_based_on_key(mocker: pytest_mock.MockFixture):
    jira_man = JiraManager(JiraInfo(
        base_url="https://dusktreader.atlassian.net",
        api_key="dummy-key",
    ))

    with mocker.patch.object(jira_man, "server") as mock_server:
        jira_man.get_issue("JAWA-9999")


def test_get_issue_from_jira__fails_on_invalid_key_pattern():
    jira_man = JiraManager(JiraInfo(
        base_url="https://dusktreader.atlassian.net",
        api_key="dummy-key",
    ))

    with pytest.raises(JiraError, match="Invalid JIRA key"):
        jira_man.get_issue("jawa-9999")
