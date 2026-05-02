import base64
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_mock

from dot_tools.exceptions import JiraError
from dot_tools.jira_tools import AuthHandler, JiraManager
from dot_tools.settings import JiraInfo


def make_jira_man() -> JiraManager:
    return JiraManager(JiraInfo(
        base_url="https://dusktreader.atlassian.net",
        api_key="dummy-key",
        cloud_id="fake-cloud-id",
    ))


class TestAuthHandler:

    def test_auth_handler__sets_authorization_header(self):
        handler = AuthHandler(username="user@example.com", api_key="secret")
        expected = base64.b64encode(b"user@example.com:secret").decode("utf-8")

        request = httpx.Request("GET", "https://example.com")
        # auth_flow is a generator; drive it once
        gen = handler.auth_flow(request)
        next(gen)

        assert request.headers["Authorization"] == f"Basic {expected}"
        assert request.headers["Content-Type"] == "application/json"


class TestJiraManagerJiraKey:

    def test_jira_key__matches_jira_pattern(self):
        assert JiraManager.jira_key("JAWA-9999--utinni") == "JAWA-9999"
        assert JiraManager.jira_key("feat/HUTT-0000--oona-goota-solo") == "HUTT-0000"

    def test_jira_key__errors_if_no_pattern_matched(self):
        with pytest.raises(JiraError, match="Can't extract a JIRA key"):
            JiraManager.jira_key("jawa-XXXX--utinni")

        with pytest.raises(JiraError, match="Can't extract a JIRA key"):
            JiraManager.jira_key("feat/fix/HUTT-0000--oona-goota-solo")


class TestJiraManagerGetIssue:

    def test_get_issue__makes_request_with_valid_key(self, mocker: pytest_mock.MockFixture):
        jira_man = make_jira_man()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{}"
        mock_response.json.return_value = {}

        with mocker.patch.object(jira_man.client, "get", return_value=mock_response):
            jira_man.get_issue("JAWA-9999")
            jira_man.client.get.assert_called_once_with("/rest/api/2/issue/JAWA-9999")

    def test_get_issue__raises_on_invalid_key_pattern(self):
        jira_man = make_jira_man()

        with pytest.raises(JiraError, match="Invalid JIRA key"):
            jira_man.get_issue("jawa-9999")

    def test_get_issue__raises_on_lowercase_key(self):
        jira_man = make_jira_man()

        with pytest.raises(JiraError, match="Invalid JIRA key"):
            jira_man.get_issue("jawa-9999")


class TestJiraManagerDummy:

    def test_dummy__calls_jira_api(self, mocker: pytest_mock.MockFixture):
        jira_man = make_jira_man()
        mock_response = MagicMock()
        mock_response.status_code = 200

        with mocker.patch.object(jira_man.client, "get", return_value=mock_response):
            jira_man.dummy("anything")
