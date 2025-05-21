import re

from loguru import logger
from jira import JIRA, Issue as JiraIssue

from dot_tools.exceptions import JiraError
from dot_tools.settings import JiraInfo


def get_issue_from_jira(key: str, jira_info: JiraInfo) -> JiraIssue:
    JiraError.require_condition(
        re.match(r"^[A-Z]+-\d+$", key),
        f"Invalid JIRA key: {key}",
    )

    issue = None
    logger.debug(f"Fetching issue from JIRA using '{key}'")
    with JiraError.handle_errors("Couldn't get description from JIRA api"):
        logger.debug("Fetching JIRA issue data from API")
        jira_server: JIRA = JIRA(
            basic_auth=(jira_info.username, jira_info.password),
            options=dict(
                server=jira_info.baseurl,
                verify=False,
            ),
        )
        return jira_server.issue(key)
