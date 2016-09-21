import os, sys

class DotException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

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
    if not was_successful:
        raise DotException("%s: %s" % (error_message, errors))
    return output

def try_cd(path, verbose=False):
    if os.getcwd() != os.path.realpath(path):
        if verbose:
            print("Changing current directory to %s" % path, file=sys.stderr)
        try:
            os.chdir(path)
        except:
            raise DotException("Couldn't change to directory: %s" % path)

def require_condition(condition, message="required condition resolved to false"):
    if condition == False:
        raise DotException(message)

def die(message="DIED"):
    raise DotException(message)
