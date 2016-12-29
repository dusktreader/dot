import enum
import git
import inflection
import inspect
import json
import os
import re
import requests
import sys

from bidict import bidict
from getpass import getuser
from setuptools import find_packages
from socket import gethostname
from time import strftime


from dot_tools.misc_tools import call, command_assert, DotException


class GitException(DotException):
    pass


def is_git(directory=os.getcwd()):
    (success, output, errors) = call("git rev-parse --is-inside-work-tree")
    return success


def remote_url():
    (was_successful, output, errors) = call("git remote show -n origin")
    GitException.require_condition(
        was_successful,
        "Couldn't fetch remote info for origin: {}",
        errors,
    )

    match = re.search(r'Fetch URL: ([^\s]+)', output)
    GitException.require_condition(
        match is not None,
        "Couldn't find a fetch url for the current git repository",
    )

    return match.group(1)


def repo_name():
    url = remote_url()
    match = re.match(
        r'{url}{base}{repo}{extension}'.format(
            url=r'(?P<url>.+:)?',
            base=r'(?P<base>.+\/)?',
            repo=r'(?P<repo>\w+)',
            extension=r'(?P<extension>\.git)?',
            ),
        url,
        )
    GitException.require_condition(
        match is not None,
        "Couldn't parse remote url",
    )

    return match.groupdict()['repo']


def pwd_project():
    return repo_name()


def toplevel(relative=False):
    argument = ''
    if relative is True:
        argument = '--show-cdup'
    else:
        argument = '--show-toplevel'

    toplevel_path = command_assert(
        "git rev-parse %s" % argument,
        "Can't find git toplevel",
    )

    if toplevel_path == '':
        toplevel_path = '.' + os.sep

    # This is a horrible hack that I have to do because python insists
    # on expanding symlinks
    if relative is False:
        toplevel_path = re.sub(
            r'/mnt/.*/work/' + getuser() + r'/(.*' + pwd_project() + '.*)',
            os.path.join(
                os.path.expanduser('~'),
                'work',
                '\g<1>',
            ),
            toplevel_path
        )

    return toplevel_path


def branch():
    return command_assert(
        "git symbolic-ref --short HEAD",
        "Can't find current git branch",
    )


def changes():
    change_dict = {'add': [], 'mod': []}

    change_list = command_assert(
        'git status -s',
        "Couldn't check status for the current branch",
    )

    for line in change_list.split('\n'):
        line = line.strip()
        if line == '':
            continue
        (change, file_name) = line.split()
        if line[0] == 'A':
            change_dict['add'].append(line[3:])
        elif line[0] == 'M':
            change_dict['mod'].append(line[3:])
    return change_dict


def pull_request(start_commit=None, compact=False):
    if start_commit is None:
        start_commit = 'origin/master'

    current_toplevel = toplevel()
    current_branch = branch()
    hostname = gethostname()

    output = ''
    if compact:
        output = "%s:%s %s" % (hostname, current_toplevel, current_branch)
    else:
        output = command_assert(
            'git request-pull {start} {host}:{top}'.format(
                start=start_commit,
                host=hostname,
                top=current_toplevel
                ),
            "Couldn't get a pull request for the current branch",
            )

    return output


def diff(start_commit=None):
    if start_commit is None:
        start_commit = 'origin/master'

    output = command_assert(
        'git diff %s' % start_commit,
        "Couldn't get a diff for the current branch",
    )

    return output


def _detect_submodules(verbose=False):
    if verbose:
        print("Detecting submodules", file=sys.stderr)
    (was_successful, output, errors) = call('git submodule status')
    if verbose:
        if not was_successful:
            print("No sumbodules detected", file=sys.stderr)
        else:
            print("Detected submodules", file=sys.stderr)
    return was_successful


def _bring_current(base_branch='master', remote=None, verbose=False):
    if verbose:
        print("Checking for changes", file=sys.stderr)
    current_changes = changes()
    add_change_count = len(current_changes['add'])
    mod_change_count = len(current_changes['mod'])
    has_changes = add_change_count > 0 or mod_change_count > 0
    stash_name = None
    if has_changes:
        stash_name = '%s-%s' % (strftime('%Y%m%d_%H%M%S'), branch())
        if verbose:
            print("Changes detected", file=sys.stderr)
            print(
                "Stashing current changes as {}".format(stash_name),
                file=sys.stderr
                )
        command_assert(
            'git stash save %s' % stash_name,
            "Couldn't stash changes for current branch",
        )
    else:
        if verbose:
            print("No changes detected", file=sys.stderr)

    if remote is not None:
        if verbose:
            print("Fetching from remote %s" % remote, file=sys.stderr)
        command_assert(
            'git fetch %s' % remote,
            "Couldn't fetch from remote %s" % remote,
        )

        base_branch = "%s/%s" % (remote, base_branch)

    if verbose:
        print("Rebasing on %s" % base_branch, file=sys.stderr)
    command_assert(
        'git rebase %s' % base_branch,
        "Couldn't rebase on %s" % base_branch,
    )

    submodules_detected = _detect_submodules(verbose)
    if submodules_detected:
        if verbose:
            print("Updating submodules", file=sys.stderr)
        command_assert(
            'git submodule update',
            "Couldn't update submodules",
        )

    if has_changes:
        if verbose:
            print("Unstashing changes", file=sys.stderr)
        command_assert(
            'git stash pop',
            "Couldn't pop changes from the stash",
        )


def _branch_exists(target_branch):
    command = 'git show-ref refs/heads/{}'.format(target_branch)
    (success, output, errors) = call(command)
    return success


def _checkout_tracking_branch(target_branch, remote, verbose=False):
    if verbose:
        message = "Checking out tracking branch {} from {}".format(
            target_branch,
            remote,
            )
        print(message, file=sys.stderr)
    current_branch = branch()
    target_upstream_branch = "%s/%s" % (remote, target_branch)
    if current_branch == target_branch:
        if verbose:
            message = "Current branch is target branch.  Checking upstream"
            print(message, file=sys.stderr)
        current_upstream_branch = command_assert(
            'git rev-parse --abrev-ref @{upstream}',
            "Couldn't detect upstream branch",
        )
        GitException.require_condition(
            current_upstream_branch == target_upstream_branch,
            "Current upstream branch does not match target upstream branch",
        )
        if verbose:
            print("Pulling changes from upstream", file=sys.stderr)
        command_assert(
            'git pull %s %s' % (remote, target_branch),
            "Couldn't pull from upstream branch",
        )

    elif _branch_exists(target_branch):
        if verbose:
            message = "Target branch already exists.  Checking upstream"
            print(message, file=sys.stderr)
        current_upstream_branch = command_assert(
            'git rev-parse --abrev-ref %s@{upstream}' % current_branch,
            "Couldn't detect upstream branch",
        )
        GitException.require_condition(
            current_upstream_branch == target_upstream_branch,
            "Upstream branch does not match target upstream branch",
        )
        _checkout_branch(target_branch, verbose)

    else:
        command_assert(
            'git checkout --track %s' % target_upstream_branch,
            "Coudln't checkout tracking branch",
        )
        if verbose:
            message = "Checked out tracking branch {}".format(target_branch)
            print(message, file=sys.stderr)


def _checkout_branch(target_branch, verbose=False):
    current_branch = branch()
    if current_branch == target_branch:
        if verbose:
            message = "Target branch is already currently checked out"
            print(message, file=sys.stderr)
    else:
        if verbose:
            print("Checking out branch %s" % target_branch, file=sys.stderr)
        command_assert(
            'git checkout %s' % target_branch,
            "Couldn't checkout branch",
        )
        if verbose:
            print("Checked out branch %s" % target_branch, file=sys.stderr)


def _checkout_new_branch(target_branch, verbose=False):
    GitException.require_condition(
        not _branch_exists(target_branch),
        "Target branch already exists.  Cannot create new branch",
    )
    if verbose:
        print("Checking out new branch %s" % target_branch, file=sys.stderr)
    command_assert(
        'git checkout -b %s' % target_branch,
        "Couldn't checkout new branch",
    )
    if verbose:
        print("Checked out new branch %s" % target_branch, file=sys.stderr)


def pushup(verbose=False):
    if verbose:
        print("Pushing branch to origin for first time", file=sys.stderr)
    current_branch = branch()
    print(command_assert(
        'git push --set-upstream origin %s' % current_branch,
        "Couldn't checkout base branch",
    ))
    if verbose:
        print("Pushed branch to origin", file=sys.stderr)


def _add_remote(remote_alias, remote_url, verbose=False):
    if verbose:
        message = "Adding remote for {} as {}".format(remote_url, remote_alias)
        print(message, file=sys.stderr)
    command = 'git config --get remote.{}.url'.format(remote_alias)
    (was_successful, output, errors) = call(command)
    if was_successful:
        current_url = output
        GitException.require_condition(
            current_url == remote_url,
            'Remote already exists but with different url than target of {}',
            remote_url,
        )
        if verbose:
            print("Remote already exists", file=sys.stderr)
    else:
        command_assert(
            'git remote add %s %s' % (remote_alias, remote_url),
            "Couldn't add remote %s to %s" % (remote_alias, remote_url)
        )


def make_flake8_link(file_path):
    top = toplevel()
    config_path = os.path.join(top, '.flake8')
    if os.path.lexists(config_path):
        os.remove(config_path)
    target_config = ''
    if str(os.path.basename(file_path)).startswith('test_'):
        target_config = os.path.join(top, 'etc/flake8/test-style-config.ini')
    else:
        target_config = os.path.join(top, 'etc/flake8/src-style-config.ini')
    os.symlink(target_config, config_path)


def print_var(value, print_fn=print):
    this_function_name = inspect.getframeinfo(inspect.currentframe()).function
    match = re.search(
        r'{}\((\w+)\)'.format(this_function_name),
        inspect.getframeinfo(inspect.currentframe().f_back).code_context[0],
    )
    if match is None:
        print_fn("Couldn't interpret variable. Basic regex failed")
    var_name = match.group(1)
    print_fn("{}={}".format(var_name, value))


def find_source_path(top=None):
    if top is None:
        top = toplevel()

    possible_source_dirs = [
        p for p in find_packages(where=top)
        if '.' not in p and
        p not in ['tests', 'test']
    ]
    DotException.require_condition(
        len(possible_source_dirs) == 1,
        "Could not find one and only one source package",
    )
    return os.path.join(top, possible_source_dirs.pop())


def find_test_file(file_path):
    DotException.require_condition(
        os.path.exists(file_path),
        "Can't lookup test for non-extant source: {}",
        file_path,
    )
    top = toplevel()

    temp_dir = os.path.abspath(file_path)
    while temp_dir != top:
        DotException.require_condition(
            not os.path.basename(temp_dir).startswith('test'),
            "Found test file or dir in source file path",
        )
        temp_dir = os.path.dirname(temp_dir)

    source_dir_path = find_source_path(top)

    possible_test_dirs = [
        os.path.join(top, 'test'),
        os.path.join(top, 'tests'),
        os.path.join(source_dir_path, 'test'),
        os.path.join(source_dir_path, 'tests'),
    ]
    test_dir_path = None
    for possible_test_dir in possible_test_dirs:
        if os.path.exists(possible_test_dir):
            test_dir_path = possible_test_dir
    DotException.require_condition(
        test_dir_path is not None,
        "Could not find a test dir path",
    )

    relative_file_path_from_source = os.path.relpath(
        file_path,
        source_dir_path,
    )
    (middle_path, file_name) = os.path.split(relative_file_path_from_source)
    test_path = os.path.join(
        test_dir_path,
        middle_path,
        'test_' + file_name,
    )
    return test_path


def find_implementation_file(test_path):
    DotException.require_condition(
        os.path.exists(test_path),
        "Can't lookup implementation for non-extant test",
    )
    top = toplevel()

    possible_test_dirs = ['test', 'tests']
    test_dir_path = None
    temp_dir = os.path.abspath(test_path)
    while temp_dir != top:
        if os.path.basename(temp_dir) in possible_test_dirs:
            test_dir_path = temp_dir
        temp_dir = os.path.dirname(temp_dir)
    DotException.require_condition(
        test_dir_path is not None,
        "Can't find test dir. Must not be *in* test dir",
    )

    source_dir_path = find_source_path(top)

    relative_test_path_from_test = os.path.relpath(test_path, test_dir_path)
    (middle_path, test_name) = os.path.split(relative_test_path_from_test)
    source_path = os.path.join(
        source_dir_path,
        middle_path,
        test_name.lstrip('test_')
    )
    return source_path


def is_github_repo():
    repo = git.Repo(os.getcwd())
    remote = repo.remote(name='origin')
    urls = list(remote.urls)
    DotException.require_condition(
        len(urls) == 1,
        "Remote 'origin' should only have one url",
    )
    url = urls.pop()
    return 'github.com' in url


class VersionType(enum.IntEnum):
    major = 1
    minor = 2
    patch = 3
    release_candidate = 4
    beta = 5
    alpha = 6

    @classmethod
    def short_dict(cls):
        return bidict(
            M=cls.major,
            m=cls.minor,
            p=cls.patch,
            a=cls.alpha,
            b=cls.beta,
            rc=cls.release_candidate,
        )

    @classmethod
    def all_names(cls):
        return [e.name for e in cls]

    @classmethod
    def all_keys(cls):
        return [e.name for e in cls] + [k for k in cls.short_dict()]

    @classmethod
    def special(cls):
        return [e for e in cls if e > cls.patch]

    @classmethod
    def lookup(cls, key):
        key = key.lower()
        return (cls.short_dict().get(key) or getattr(cls, key))


class Version:

    def __init__(self, *args, **kwargs):
        self.set_version(*args, **kwargs)

    @classmethod
    def from_string(cls, text):
        match = re.match(
            r'^v?(\d+)\.(\d+)\.(\d+)(?:-(\w+)(\d+))?$',
            text,
        )
        DotException.require_condition(
            match is not None,
            "Couldn't parse version",
        )
        return cls(*match.groups())

    def __repr__(self):
        text = '{}.{}.{}'.format(
            self.d[VersionType.major],
            self.d[VersionType.minor],
            self.d[VersionType.patch],
        )
        if self.current_special_type is not None:
            text = '{}-{}{}'.format(
                text,
                VersionType.short_dict().inv[self.current_special_type],
                self.d[self.current_special_type],
            )
        return text

    def __str__(self):
        return 'v' + repr(self)

    def major_minor(self):
        return '{}.{}'.format(
            self.d[VersionType.major],
            self.d[VersionType.minor],
        )

    @property
    def current_special_type(self):
        for special_type in VersionType.special():
            if self.d.get(special_type) is not None:
                return special_type
        return None

    def set_version(
        self, major_num, minor_num, patch_num, extra_type=None, extra_num=None
    ):
        self.d = {
            VersionType.major: int(major_num),
            VersionType.minor: int(minor_num),
            VersionType.patch: int(patch_num),
        }

        if extra_type is not None:
            with DotException.handle_errors("Can't parse extra version info"):
                if not isinstance(extra_type, VersionType):
                    extra_type = VersionType.lookup(extra_type)
                self.d[extra_type] = int(extra_num)

    def bump(self, bump_type=VersionType.patch):
        if not isinstance(bump_type, VersionType):
            bump_type = VersionType.lookup(bump_type)

        if bump_type is VersionType.major:
            self.set_version(self.d[VersionType.major] + 1, 0, 0)

        elif bump_type is VersionType.minor:
            self.set_version(
                self.d[VersionType.major],
                self.d[VersionType.minor] + 1,
                0
            )

        elif bump_type is VersionType.patch:
            self.set_version(
                self.d[VersionType.major],
                self.d[VersionType.minor],
                self.d[VersionType.patch] + 1,
            )

        else:
            current_type = self.current_special_type
            if current_type is None:
                self.d[VersionType.patch] += 1
                self.d[bump_type] = 1
            elif current_type is bump_type:
                self.d[bump_type] += 1
            elif bump_type.value > current_type.value:
                raise DotException(
                    "Cannot bump from {} to {}",
                    current_type.name,
                    bump_type.name,
                )
            else:
                del self.d[current_type]
                self.d[bump_type] = 1


def _count_changes(repo):
    len(repo.index.diff("HEAD"))


def get_current_version(path=None, metadata=None):
    if metadata is None:
        with open(path, 'r') as metadata_file:
            metadata = json.load(metadata_file)
    return Version.from_string(metadata['release'])


def tag_version(comment=None, bump_type=None, path=None, verbose=False):
    with DotException.handle_errors("Couldn't tag version"):
        if verbose:
            print("Started tagging version")

        repo = git.Repo(os.getcwd())
        gitter = repo.git

        if verbose:
            print("Reading metadata file: {}".format(path))
        with open(path, 'r') as metadata_file:
            metadata = json.load(metadata_file)

        if verbose:
            print("Extracting version from metadata")
        version = get_current_version(path, metadata=metadata)
        if verbose:
            print("Extracted version as: {}".format(version))

        if bump_type is not None:
            version.bump(bump_type)
            if verbose:
                print("Version bumped to: {}".format(version))
            metadata['release'] = repr(version)
            metadata['version'] = version.major_minor()
            with open(path, 'w') as metadata_file:
                json.dump(metadata, metadata_file, sort_keys=True, indent=4)

            DotException.require_condition(
                len(repo.index.diff("HEAD")) == 0,
                "There must be no staged files before the tag can be made",
            )

            if verbose:
                print("Attempting to edit change-log")
            top = toplevel()
            changelog_files = [
                os.path.join(top, f)
                for f in os.listdir(top)
                if re.search(r'(CHANGELOG|HISTORY|RELEASE)', f)
            ]
            if len(changelog_files) == 1:
                changelog = changelog_files.pop()
                os.system('$EDITOR {}'.format(changelog))
                gitter.add(changelog)
            elif verbose:
                print("Skipping edit changelog: didn't find 1 changelog")

            if verbose:
                print("Adding {} for commit".format(path))
            gitter.add(path)
            if verbose:
                print("Commiting changes")
            gitter.commit(m="Version bumped to: {}".format(version))
            if verbose:
                print("Pushing changes")
            gitter.push()

        if verbose:
            print("Formatting comment '{}' with metadata".format(comment))
        if comment is None:
            comment = "{name} version {release}"
        comment = comment.format(**metadata)
        if verbose:
            print("Formatted comment is '{}'".format(comment))

        if verbose:
            print("Creating tag")
        gitter.tag(
            "'{}'".format(str(version)),
            annotate=True,
            message="'{}'".format(comment),
        )

        if verbose:
            print("Pushing tags")
        gitter.push(tags=True)

        if verbose:
            print("Finished tagging version")


def make_github_branch(issue_number, base=None, verbose=False):
    repo = git.Repo(os.getcwd())
    remote = repo.remote(name='origin')
    ref = None
    if base is None:
        base = repo.active_branch
        ref = repo.active_branch
    else:
        with DotException.handle_errors("Couldn't find a ref for that base"):
            if verbose:
                print("Evaluating ref from base".format(base))
            ref = repo.refs[base]

    if 'origin' in str(base):
        if verbose:
            print("Fetching")
        remote.fetch()

    if verbose:
        print("Parsing remote url")
    urls = list(remote.urls)
    DotException.require_condition(
        len(urls) == 1,
        "Remote 'origin' should only have one url",
    )
    url = urls.pop()
    if verbose:
        print("url is: {}".format(url))
    match = re.match(r'.*github\.com[:/]([\w-]+)/([\w-]+).*', url)
    DotException.require_condition(
        match is not None,
        "remote url must be a github hosted repo",
    )
    (owner, repo_name) = match.groups()

    if verbose:
        print("Building github api url to fetch issue")
    api_url = os.path.join(
        'https://api.github.com/repos',
        owner,
        repo_name,
        'issues',
        str(issue_number),
    )
    if verbose:
        print("url built as {}".format(api_url))

    if verbose:
        print("Getting issue details")
    response = requests.get(api_url)
    DotException.require_condition(
        response.status_code == 200,
        "Couldn't find issue number {}",
        issue_number,
    )
    issue = response.json()

    if verbose:
        print("Finding current git user")
    reader = repo.config_reader()
    try:
        user = reader.get_value('github', 'user')
    except:
        with DotException.handle_error("couldn't determine a username"):
            user = reader.get_value('user', 'name')

    if verbose:
        print("Building branch name")
    branch_name = '{}/{}--{}'.format(
        user,
        issue_number,
        inflection.parameterize(issue['title']),
    )
    if verbose:
        print("branch name built as {}".format(branch_name))

    if verbose:
        print("Creating new branch named {}".format(branch_name))
    repo.create_head(branch_name, ref)

    if verbose:
        print("Checking out new branch")
    repo.git.checkout(branch_name)
