import re
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Self
from urllib.parse import urlparse, ParseResult

import git
from loguru import logger

from dot_tools.exceptions import DotError, GitError


class GitProtocol(StrEnum):
    ssh = auto()
    https = auto()


@dataclass
class GitUrl:
    protocol: GitProtocol
    host: str
    owner: str
    repo: str

    @classmethod
    def parse(cls, url: str) -> Self:
        with GitError.handle_errors(f"Couldn't parse git {url=}"):
            ssh_match = re.match(r"^git@(?P<host>[\w\.]+):(?P<owner>\w+)/(?P<repo>[\w-]+)(\.git)?$", url)
            if ssh_match:
                return cls(
                    protocol=GitProtocol.ssh,
                    **ssh_match.groupdict(),
                )
            else:
                parsed: ParseResult = urlparse(url)
                host = GitError.enforce_defined(parsed.hostname, "Couldn't parse host")
                path = Path(parsed.path)
                return cls(
                    protocol=GitProtocol[parsed.scheme],
                    host=host,
                    owner=path.parent.name,
                    repo=path.stem,
                )


class GitManager:
    repo: git.Repo

    def __init__(self, path: Path | None = None):
        if path is None:
            path = Path.cwd()
        else:
            path = path.expanduser().resolve().absolute()
        GitError.require_condition(
            path.exists(),
            "Can't initialize GitManger with a path that doesn't exist",
        )

        temp_path: Path = path
        while temp_path != Path("/"):
            try:
                self.repo = git.Repo(temp_path)
                break
            except git.InvalidGitRepositoryError:
                temp_path = temp_path.parent
        else:
            raise GitError(f"Path {path} was not in a git repository")

        logger.debug(f"Initialized GitManger for {self.repo}")

    def remote(self, remote_name: str = "origin") -> git.Remote:
        return self.repo.remote(name=remote_name)

    def remote_url(self, remote: git.Remote | None = None):
        if remote is None:
            remote = self.remote()
        urls: list[str] = list(remote.urls)
        DotError.require_condition(
            len(urls) == 1,
            f"Remote {remote.name} did not have exactly one url",
        )
        return urls[0]

    @property
    def current_branch(self) -> git.Reference:
        return self.repo.active_branch


    def toplevel(self, *, start_path: Path | None = None, relative: bool = False) -> Path:
        logger.debug(f"Finding {'relative' if relative else 'absolute'} toplevel path for {start_path}")
        root_path = Path(self.repo.working_dir)
        logger.debug(f"Toplevel is {root_path=}")
        if not relative:
            return root_path

        if not start_path:
            start_path = Path.cwd()
            logger.debug(f"Finding relative path from {start_path=}")
        start_path = start_path.expanduser().resolve().absolute()
        return root_path.relative_to(start_path, walk_up=True)

    def is_github_repo(self) -> bool:
        with GitError.handle_errors("Git repo has no remote named 'origin'"):
            origin = self.repo.remote("origin")
        parsed_url = GitUrl.parse(origin.url)
        return parsed_url.host == "github.com"

    def checkout_new_branch(self, branch_name: str, *, base_name: str |  None = None, remote_name: str | None = None):
        base: git.SymbolicReference
        if base_name:
            with GitError.handle_errors(f"Couldn't find branch named {base_name!r}"):
                if remote_name:
                    remote = self.remote(remote_name)
                    branches = remote.fetch()
                    fetch_info = branches["/".join([remote_name, base_name])]
                    base = fetch_info.ref
                else:
                    base = self.repo.heads[base_name]
        else:
            with GitError.handle_errors("Repo has no active branch!"):
                base = self.current_branch

        logger.debug(f"Evaluating ref from base {base}")

        logger.debug(f"Creating new branch named {branch_name} based on {base}")
        _ = self.repo.create_head(branch_name, base)

        logger.debug("Checking out new branch")
        self.repo.git.checkout(branch_name)

#     def get_issue_from_github(self, key):
#         parsed_url: giturlparse.GitUrlParsed = self.parse_repo_url()
#         owner = parsed_url.owner
#         repo_name = parsed_url.name
#
#         logger.debug("Building github api url to fetch issue")
#         api_url = os.path.join(
#             "https://api.github.com/repos",
#             owner,
#             repo_name,
#             "issues",
#             str(key),
#         )
#         logger.debug(f"url built as {api_url}")
#
#         logger.debug("Getting github issue details from api")
#         response = requests.get(api_url)
#         DotError.require_condition(
#             response.status_code == 200,
#             f"Couldn't find issue number {key}",
#         )
#         issue = response.json()
#
#         logger.debug("Finding current git user")
#         reader = self.repo.config_reader()
#         try:
#             user = reader.get_value("github", "user")
#         except Exception:
#             with DotError.handle_error("couldn't determine a username"):
#                 user = reader.get_value("user", "name")
#
#         return dict(
#             key=key,
#             user=user,
#             prefix="",
#             desc=issue["title"],
#         )
#
#     def make_branch(self, key: str, base_name: str |  None = None):
#         key = str(key).upper()
#         issue_fetcher = None
#         if not self.is_github_repo():
#             logger.debug("repo is not a github repo")
#             issue_fetcher = self.get_issue_from_jira
#         else:
#             logger.debug("repo is a github repo")
#             issue_fetcher = self.get_issue_from_github
#         branch_parts = issue_fetcher(key)
#         branch_parts["desc"] = inflection.parameterize(branch_parts["desc"])
#         branch_name = "{prefix}{user}/{key}--{desc}".format(**branch_parts)[:60]
#         logger.debug(f"branch name built as {branch_name}")
#         self.checkout_new_branch(branch_name, base=base)
#
    def checkout_branch_by_pattern(self, pattern: str):
        matching_refs: list[git.Head | git.SymbolicReference] = [
            b for b in self.repo.heads if re.search(pattern, b.name, re.IGNORECASE)
        ]
        if len(matching_refs) == 0:
            for remote in self.repo.remotes:
                for item in remote.fetch():
                    if re.search(pattern, item.name, re.IGNORECASE):
                        matching_refs.append(item.ref)
        GitError.require_condition(
            len(matching_refs) == 1,
            f"Couldn't find exactly one branch matching {pattern}: matches: {[str(b) for b in matching_refs]}",
        )
        ref = matching_refs.pop()
        if isinstance(ref, git.RemoteReference):
            logger.debug(f"Attempting to checkout remote branch: {ref.name}")
            new_head = self.repo.create_head(ref.remote_head, ref)
            new_head.checkout()
        else:
            logger.debug(f"Trying to checkout local branch: {ref.name}")
            old_head = GitError.ensure_type(ref, git.Head)
            old_head.checkout()

        logger.debug(f"Branch {ref.name} checked out")
