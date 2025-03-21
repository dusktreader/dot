import addict
import git
import giturlparse
import inflection
import jira
import json
import keyring
import os
import pathlib
import re
import requests
from loguru import logger

from dot_tools.misc_tools import DotError


class GitError(DotError):
    pass


class GitManager:
    def __init__(self, path=None):
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = os.path.abspath(os.path.expanduser(path))
        GitError.require_condition(
            os.path.exists(self.path),
            "Can't initialize GitManger with nonextant path",
        )

        with GitError.handle_errors("Couldn't initialize git manager"):
            self.repo = None
            temp_path = self.path
            while not os.path.ismount(temp_path):
                try:
                    self.repo = git.Repo(temp_path)
                    break
                except git.InvalidGitRepositoryError:
                    temp_path = os.path.dirname(temp_path)
            GitError.require_condition(
                self.repo is not None,
                f"Path {self.path} was not in a git repository",
            )
            self.gitter = self.repo.git
            logger.debug(f"Initialized GitManger for {self.repo}")

    def remote(self, remote_name="origin"):
        return self.repo.remote(name=remote_name)

    def remote_url(self, remote=None):
        if remote is None:
            remote = self.remote()
        urls = list(remote.urls)
        DotError.require_condition(
            len(urls) == 1,
            f"Remote {remote.name} had more than one url",
        )
        url = urls.pop()
        return url

    def parse_repo_url(self, url=None):
        if url is None:
            url = self.remote_url()
        if not url.endswith(".git"):
            url += ".git"
        logger.debug(f"Attempting to parse url: {url}")
        with DotError.handle_errors(f"Couldn't parse url {url}"):
            parsed_url = giturlparse.parse(url)
        logger.debug(f"URL parsed as: {parsed_url.href}")
        return parsed_url

    def toplevel(self, start_path=None, relative=False):
        path = self.repo.working_dir
        if start_path is None:
            start_path = path
        logger.debug(f"Toplevel path is {path}")
        if relative:
            logger.debug(f"Finding relative path from {start_path}")
            path = os.path.relpath(path, start_path)
        logger.debug(f"Toplevel path is {path}")
        return path

    def is_github_repo(self):
        parsed_url = self.parse_repo_url()
        return parsed_url.resource == "github.com"

    def find_source_path(self, top=None):
        if top is None:
            top = self.toplevel()
        logger.debug("Looking for 'source' path from {top}")

        packages = [
            p
            for p in pathlib.Path(top).iterdir()
            if p.is_dir() and p.joinpath("__init__.py").exists() and p.name != "tests"
        ]
        GitError.require_condition(
            len(packages) == 1,
            f"Could not find one and only one source package. Found {packages=}",
        )
        source_path = os.path.join(top, str(packages.pop()))
        logger.debug(f"Source path found at {source_path}")
        return source_path

    def count_changes(self):
        return len(self.repo.index.diff("HEAD"))

    def checkout_new_branch(self, branch_name, base=None):

        ref = None
        with DotError.handle_errors("Couldn't find a ref for that base"):
            if base is None:
                base = self.current_branch
                ref = self.current_branch
            else:
                logger.debug(f"Evaluating ref from base {base}")
                ref = self.repo.refs[base]

        if "origin" in str(base):
            logger.debug("Fetching")
            self.remote().fetch()

        logger.debug(f"Creating new branch named {branch_name} based on {base}")
        self.repo.create_head(branch_name, ref)

        logger.debug("Checking out new branch")
        self.repo.git.checkout(branch_name)

    def save_jira_password(self, password):
        jira_path = os.path.expanduser("~/.jira.json")
        with open(jira_path) as jira_file:
            jira_info = addict.Dict(json.load(jira_file))

        keyring.set_password(
            jira_info.keyring_service,
            jira_info.username,
            password,
        )

    def get_issue_from_jira(self, key):
        GitError.require_condition(
            re.match(r"^[A-Z]+-\d+$", key),
            f"Invalid JIRA key: {key}",
        )

        issue = None
        logger.debug(f"Fetching issue from JIRA using '{key}'")
        with GitError.handle_errors("Couldn't get description from JIRA api"):

            jira_path = os.path.expanduser("~/.jira.json")
            with open(jira_path) as jira_file:
                jira_info = addict.Dict(json.load(jira_file))

            logger.debug(f"Loading JIRA creds from keyring")
            password = keyring.get_password(
                jira_info.keyring_service,
                jira_info.username,
            )

            logger.debug("Fetching JIRA issue data from API")
            jira_server = jira.JIRA(
                basic_auth=(jira_info.username, password),
                options=dict(
                    server=jira_info.url_base,
                    verify=False,
                ),
            )
            issue = jira_server.issue(key)

        return dict(
            key=key,
            user=jira_info.branch_user_prefix,
            prefix="",
            desc=issue.fields.summary,
        )

    def get_issue_from_github(self, key):
        parsed_url = self.parse_repo_url()
        owner = parsed_url.owner
        repo_name = parsed_url.name

        logger.debug("Building github api url to fetch issue")
        api_url = os.path.join(
            "https://api.github.com/repos",
            owner,
            repo_name,
            "issues",
            str(key),
        )
        logger.debug(f"url built as {api_url}")

        logger.debug("Getting github issue details from api")
        response = requests.get(api_url)
        DotError.require_condition(
            response.status_code == 200,
            f"Couldn't find issue number {key}",
        )
        issue = response.json()

        logger.debug("Finding current git user")
        reader = self.repo.config_reader()
        try:
            user = reader.get_value("github", "user")
        except Exception:
            with DotError.handle_error("couldn't determine a username"):
                user = reader.get_value("user", "name")

        return dict(
            key=key,
            user=user,
            prefix="",
            desc=issue["title"],
        )

    def make_branch(self, key, base=None):
        key = str(key).upper()
        issue_fetcher = None
        if not self.is_github_repo():
            logger.debug("repo is not a github repo")
            issue_fetcher = self.get_issue_from_jira
        else:
            logger.debug("repo is a github repo")
            issue_fetcher = self.get_issue_from_github
        branch_parts = issue_fetcher(key)
        branch_parts["desc"] = inflection.parameterize(branch_parts["desc"])
        branch_name = "{prefix}{user}/{key}--{desc}".format(**branch_parts)[:60]
        logger.debug(f"branch name built as {branch_name}")
        self.checkout_new_branch(branch_name, base=base)

    @property
    def current_branch(self):
        return self.repo.active_branch

    def jira_key(self):
        current_branch = self.repo.active_branch
        GitError.require_condition(
            current_branch != "master",
            "Can't extract a JIRA key from master branch",
        )

        match = re.match(
            r"(?:.*/)?([a-z]+-\d+).*",
            str(current_branch),
            flags=re.IGNORECASE,
        )
        GitError.require_condition(
            match is not None,
            f"Can't extract a JIRA key from {current_branch}",
        )

        return match.group(1)

    def checkout_branch_by_pattern(self, pattern):
        checkout_kwargs = {}
        matching_branches = [
            b for b in self.repo.branches if re.search(pattern, str(b), re.IGNORECASE)
        ]
        if len(matching_branches) == 0:
            checkout_kwargs["track"] = True
            for remote in self.repo.remotes:
                matching_branches += [
                    b for b in remote.refs if re.search(pattern, str(b), re.IGNORECASE)
                ]
        GitError.require_condition(
            len(matching_branches) == 1,
            f"Couldn't find one branch matching {pattern}: matches: {[str(b) for b in matching_branches]}",
        )
        branch = matching_branches.pop()
        logger.debug(f"Checking out matching branch: {branch}")
        branch.checkout(**checkout_kwargs)
        logger.debug(f"Branch {branch} checked out")
