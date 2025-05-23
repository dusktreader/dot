import base64
from collections.abc import Generator
from dataclasses import dataclass, field
import re
from typing import override

import httpx
from loguru import logger
from typerdrive import TyperdriveClient, log_error

from dot_tools.exceptions import JiraError
from dot_tools.settings import JiraInfo


class AuthHandler(httpx.Auth):
    username: str
    api_key: str
    _auth: str = field(init=False, repr=False)

    def __init__(self, username: str, api_key: str):
        self.username = username
        self.api_key = api_key
        self._auth = base64.b64encode(f"{self.username}:{self.api_key}".encode("utf-8")).decode("utf-8")

    @override
    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        logger.debug("Adding auth header to request")
        request.headers["Authorization"] = f"Basic {self._auth}"
        request.headers["Content-Type"] = "application/json"
        yield request


class JiraManager:
    info: JiraInfo
    client: TyperdriveClient

    def __init__(self, info: JiraInfo):
        self.info = info
        base_url = f"{info.base_url}/{info.cloud_id}"
        self.client = TyperdriveClient(
            base_url=base_url,
            auth=httpx.BasicAuth(username="tucker.beck@gmail.com", password=info.api_key),
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


    def get_issue(self, key: str):
        print(self.info)
        JiraError.require_condition(
            re.match(r"^[A-Z]+-\d+$", key),
            f"Invalid JIRA key: {key}",
        )

        logger.debug(f"Fetching issue from JIRA using '{key}'")
        with JiraError.handle_errors("Couldn't get description from JIRA api", do_except=log_error):
            response = self.client.get(f"/rest/api/2/issue/{key}")
            print(response.status_code)
            print(response.text)
            print(response.json())


    def dummy(self, key: str):
        logger.debug("Calling JIRA")
        with JiraError.handle_errors("Couldn't complete request to JIRA api", do_except=log_error):
            print("Fetching server info")
