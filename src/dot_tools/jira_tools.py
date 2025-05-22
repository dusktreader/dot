import re

from loguru import logger
from jira import JIRA, Issue as JiraIssue

from dot_tools.exceptions import JiraError
from dot_tools.settings import JiraInfo


class JiraManager:
    info: JiraInfo
    server: JIRA

    def __init__(self, info: JiraInfo):
        self.info = info
        self.server = JIRA(
            str(info.base_url),
            basic_auth=("email", info.api_key),
            options=dict(verify=False),
        )

    @staticmethod
    def jira_key(branch_name: str):
        match = JiraError.enforce_defined(
            re.match(
                r"^(?:[^/]*/)?([a-z]+-\d+).*$",
                str(branch_name),
                flags=re.IGNORECASE,
            ),
            f"Can't extract a JIRA key from {branch_name}",
        )
        return match.group(1)


    def get_issue(self, key: str) -> JiraIssue:
        JiraError.require_condition(
            re.match(r"^[A-Z]+-\d+$", key),
            f"Invalid JIRA key: {key}",
        )

        logger.debug(f"Fetching issue from JIRA using '{key}'")
        with JiraError.handle_errors("Couldn't get description from JIRA api"):
            logger.debug("Fetching JIRA issue data from API")
            return self.server.issue(key)
