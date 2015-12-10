import os
import sys
from dot_tools.misc_tools import call, DotException


class WorkstationException(DotException):
    pass


def _devise_paths(server, target):
    remote_path = ''
    if target == 'root':
        remote_path = server + ':/'
    elif target == 'home':
        remote_path = server + ':' + os.path.expanduser('~')
    else:
        raise WorkstationException("Invalid remote target %s" % target)
    local_path = os.path.expanduser('~/remote/') + '%s-%s' % (server, target)
    return (remote_path, local_path)


def _already_mounted(remote_path, local_path):
    (was_successful, output, errors) = call('mount -l')
    if not was_successful:
        raise WorkstationException("Couldn't check extant mounts: %s" % errors)
    mount_line = "%s on %s" % (remote_path, local_path)
    return mount_line in output


def mount_remote(server, target, verbose=False):
    (remote_path, local_path) = _devise_paths(server, target)
    if verbose:
        print(
            "      Mounting remote path {} at local {}".format(
                remote_path,
                local_path
                ),
            file=sys.stderr
            )

    if not os.path.exists(local_path):
        if verbose:
            print("      Creating local path %s" % local_path, file=sys.stderr)
        try:
            os.makedirs(local_path)
        except Exception as error:
            message = "Couldn't create local path: {}".format(error)
            raise WorkstationException(message)

    if not _already_mounted(remote_path, local_path):

        # TODO:  ignore dolphin poop in git config
        dolphin_poop = os.path.join(local_path, ".directory")
        if os.path.exists(dolphin_poop):
            if verbose:
                print(
                    "      Cleaning up dolphin poop in {}".format(local_path),
                    file=sys.stderr,
                    )
            try:
                os.remove(dolphin_poop)
            except Exception as error:
                message = "Couldn't clean up dolphin poop: {}".format(error)
                raise WorkstationException(message)

        mount_command = 'sshfs {key_check} {follow} {remote} {local}'.format(
            key_check='-o StrictHostKeyChecking=no',
            follow='-o follow_symlinks',
            remote=remote_path,
            local=local_path,
            )
        (was_successful, output, errors) = call(mount_command)
        if not was_successful:
            message = "Couldn't mount remote {} at local {}: {}".format(
                remote_path,
                local_path,
                errors
                )
            raise WorkstationException(message)
        elif verbose:
            message = "      Remote {} mounted at local {}".format(
                remote_path,
                local_path
                )
            print(message, file=sys.stderr)

    elif verbose:
        message = "      {} is already mounted at {}".format(
            remote_path,
            local_path,
            )
        print(message, file=sys.stderr)


def dismount_remote(server, target, verbose=False):
    (remote_path, local_path) = _devise_paths(server, target)
    if verbose:
        print("      Dismounting %s" % local_path, file=sys.stderr)

    if _already_mounted(remote_path, local_path):
        dismount_command = 'fusermount -u %s' % local_path
        (was_successful, output, errors) = call(dismount_command)
        if not was_successful:
            raise WorkstationException("Couldn't dismount %s" % local_path)
        elif verbose:
            print("      Dismounted %s" % local_path, file=sys.stderr)
    else:
        message = "Remote {} is not mounted at local {}".format(
            remote_path,
            local_path,
            )
        raise WorkstationException()
