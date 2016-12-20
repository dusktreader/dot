import os
import sys

from buzz import Buzz


class DotException(Buzz):

    @classmethod
    def die(cls, *format_args, message='DIED', **format_kwargs):
        raise cls(message, *format_args, **format_kwargs)


def call(command):
    # If the machine has at least python 2.4, use subprocess...sigh
    out_tmp = '/tmp/_call_stdout'
    err_tmp = '/tmp/_call_stderr'
    status = os.system('%s > %s 2> %s' % (command, out_tmp, err_tmp))
    was_successful = os.WEXITSTATUS(status) == 0
    out = open(out_tmp, 'r').read().strip()
    err = open(err_tmp, 'r').read().strip()
    return (was_successful, out, err)


def command_assert(command, error_message):
    (was_successful, output, errors) = call(command)
    DotException.require_condition(
        was_successful,
        "{}: {}".format(error_message, errors),
    )
    return output


def try_cd(path, verbose=False):
    if os.getcwd() != os.path.realpath(path):
        if verbose:
            print("Changing current directory to %s" % path, file=sys.stderr)
        message = "Couldn't change to directory: {}".format(path)
        with DotException.handle_errors(message):
            os.chdir(path)
