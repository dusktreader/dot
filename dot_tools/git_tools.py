import getpass
import git
import giturlparse
import inflection
import jira.client
import json
import logbook
import os
import re
import requests
import setuptools


from dot_tools.misc_tools import DotError


class GitError(DotError):
    pass


class GitManager:

    def __init__(self, path=None, logger=None):
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = os.path.abspath(os.path.expanduser(path))
        GitError.require_condition(
            os.path.exists(self.path),
            "Can't initialize GitManger with nonextant path",
        )

        if logger is None:
            self.logger = logbook.Logger('GitManager')
            self.logger.level = logbook.DEBUG
        else:
            self.logger = logger

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
                "Path {} was not in a git repository",
                self.path
            )
            self.gitter = self.repo.git
            self.logger.debug("Initialized GitManger for {}", self.repo)

    def remote(self, remote_name='origin'):
        return self.repo.remote(name=remote_name)

    def remote_url(self, remote=None):
        if remote is None:
            remote = self.remote()
        urls = list(remote.urls)
        DotError.require_condition(
            len(urls) == 1,
            "Remote {} had more than one url",
            remote.name,
        )
        url = urls.pop()
        return url

    def parse_repo_url(self, url=None):
        if url is None:
            url = self.remote_url()
        parsed_url = giturlparse.parse(url)
        DotError.require_condition(parsed_url.valid, "Couldn't parse url")
        return parsed_url

    def toplevel(self, start_path=None, relative=False):
        path = self.repo.working_dir
        if start_path is None:
            start_path = path
        self.logger.debug("Toplevel path is {}", path)
        if relative:
            self.logger.debug("Finding relative path from {}", start_path)
            path = os.path.relpath(path, start_path)
        self.logger.debug("Toplevel path is {}", path)
        return path

    def is_github_repo(self):
        parsed_url = self.parse_repo_url()
        return parsed_url.domain == 'github.com'

    def find_source_path(self, top=None):
        if top is None:
            top = self.toplevel()
        self.logger.debug("Looking for 'source' path from {}", top)

        packages = setuptools.find_packages(where=top, exclude=['test*'])
        unique_roots = set([p.split('.')[0] for p in packages])
        GitError.require_condition(
            len(unique_roots) == 1,
            "Could not find one and only one source package",
        )
        source_path = os.path.join(top, unique_roots.pop())
        self.logger.debug("Source path found at {}", source_path)
        return source_path

    def count_changes(self):
        return len(self.repo.index.diff("HEAD"))

    def checkout_new_branch(self, branch_name, base=None):

        ref = None
        with DotError.handle_errors("Couldn't find a ref for that base"):
            if base is None:
                base = self.repo.active_branch
                ref = self.repo.active_branch
            else:
                self.logger.debug("Evaluating ref from base {}".format(base))
                ref = self.repo.refs[base]

        if 'origin' in str(base):
            self.logger.debug("Fetching")
            self.remote().fetch()

        self.logger.debug("Creating new branch named {} based on {}".format(
            branch_name,
            base
        ))
        self.repo.create_head(branch_name, ref)

        self.logger.debug("Checking out new branch")
        self.repo.git.checkout(branch_name)

    def get_issue_from_jira(self, key):
        GitError.require_condition(
            re.match(r'^[A-Z]+-\d+$', key),
            "Invalid JIRA key: {}",
            key,
        )

        issue = None
        self.logger.debug("Fetching issue from JIRA using '{}'".format(key))
        with GitError.handle_errors("Couldn't get description from JIRA api"):

            cred_path = os.path.expanduser('~/.jira.json')

            self.logger.debug("Loading JIRA creds from {}".format(cred_path))
            with open(cred_path) as cred_file:
                creds = json.load(cred_file)

            self.logger.debug("Fetching JIRA issue data from API")
            jira_server = jira.client.JIRA(
                basic_auth=(creds['username'], creds['password']),
                options={'server': creds['url_base']},
            )
            issue = jira_server.issue(key)

        return dict(
            key=key,
            user=getpass.getuser(),
            prefix='personal/',
            desc=issue.fields.summary,
        )

    def get_issue_from_github(self, key):
        parsed_url = self.parse_repo_url()
        owner = parsed_url.owner
        repo_name = parsed_url.repo

        self.logger.debug("Building github api url to fetch issue")
        api_url = os.path.join(
            'https://api.github.com/repos',
            owner,
            repo_name,
            'issues',
            str(key),
        )
        self.logger.debug("url built as {}".format(api_url))

        self.logger.debug("Getting github issue details from api")
        response = requests.get(api_url)
        DotError.require_condition(
            response.status_code == 200,
            "Couldn't find issue number {}",
            key,
        )
        issue = response.json()

        self.logger.debug("Finding current git user")
        reader = self.repo.config_reader()
        try:
            user = reader.get_value('github', 'user')
        except:
            with DotError.handle_error("couldn't determine a username"):
                user = reader.get_value('user', 'name')

        return dict(
            key=key,
            user=user,
            prefix='',
            desc=issue['title'],
        )

    def make_branch(self, key, base=None):
        key = str(key).upper()
        issue_fetcher = None
        if not self.is_github_repo():
            self.logger.debug("repo is not a github repo")
            issue_fetcher = self.get_issue_from_jira
        else:
            self.logger.debug("repo is a github repo")
            issue_fetcher = self.get_issue_from_github
        branch_parts = issue_fetcher(key)
        branch_parts['desc'] = inflection.parameterize(branch_parts['desc'])
        branch_name = '{prefix}{user}/{key}--{desc}'.format(**branch_parts)
        self.logger.debug("branch name built as {}".format(branch_name))
        self.checkout_new_branch(branch_name, base=base)

    def jira_key(self):
        current_branch = self.repo.active_branch
        GitError.require_condition(
            current_branch != 'master',
            "Can't extract a JIRA key from master branch",
        )

        match = re.match(
            r'(?:.*/)?([a-z]+-\d+).*',
            str(current_branch),
            flags=re.IGNORECASE,
            )
        GitError.require_condition(
            match is not None,
            "Can't extract a JIRA key from {}",
            current_branch,
        )

        return match.group(1)

    def checkout_branch_by_pattern(self, pattern):
        self.logger.debug("Searching for branch matching: {}", pattern)
        matching_branches = [
            b for b
            in self.repo.branches
            if re.search(pattern, str(b), re.IGNORECASE)
        ]
        GitError.require_condition(
            len(matching_branches) == 1,
            "Couldn't find one branch matching {}: matches: {}",
            pattern,
            [str(b) for b in matching_branches],
        )
        branch = matching_branches.pop()
        self.logger.debug("Checking out matching branch: {}", branch)
        branch.checkout()
        self.logger.debug("Branch {} checked out", branch)

    def pushup(self):
        self.logger.debug("Pushing branch to origin for first time")
        self.gitter.push('origin', self.repo.active_branch, set_upstream=True)
        self.logger.debug("Pushed branch to origin")
