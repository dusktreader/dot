import os
import sys
import re

from getpass import getuser
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
    if not was_successful:
        message = "Couldn't fetch remote info for origin: {}".format(errors)
        raise GitException(message)

    match = re.search(r'Fetch URL: ([^\s]+)', output)
    if match is None:
        message = "Couldn't find a fetch url for the current git repository"
        raise GitException(message)

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
    if match is None:
        raise GitException("Couldn't parse remote url")

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
            messsage = "Current branch is target branch.  Checking upstream"
            print(message, file=sys.stderr)
        current_upstream_branch = command_assert(
            'git rev-parse --abrev-ref @{upstream}',
            "Couldn't detect upstream branch",
        )
        if current_upstream_branch != target_upstream_branch:
            message = "Current upstream branch does not match target"
            message += "upstream branch"
            raise GitException(message)
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
        if current_upstream_branch != target_upstream_branch:
            message = "Upstream branch does not match target upstream branch"
            raise GitException(message)
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
    if _branch_exists(target_branch):
        message = "Target branch already exists.  Cannot create new branch"
        raise GitException(message)
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
    command_assert(
        'git push --set-upstream origin %s' % current_branch,
        "Couldn't checkout base branch",
    )
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
        if current_url != remote_url:
            message = 'Remote already exists but refers to a different url'
            message += ' than target of {}'.format(remote_url)
            raise GitException(message)
        elif verbose:
            print("Remote already exists", file=sys.stderr)
    else:
        command_assert(
            'git remote add %s %s' % (remote_alias, remote_url),
            "Couldn't add remote %s to %s" % (remote_alias, remote_url)
        )