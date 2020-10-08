import ast
import inspect
import os
import pendulum
import pprintpp
import re
import sys
from loguru import logger

from buzz import Buzz


class DotException(Buzz):
    @classmethod
    def die(cls, *format_args, message="DIED", **format_kwargs):
        raise cls(message, *format_args, **format_kwargs)


class DotError(DotException):
    """This is a stand-in until I just rename DotException project wide"""

    pass


def _get_transpose(in_stream):
    return zip(*[ast.literal_eval(r.strip()) for r in in_stream.readlines()])


def transpose(in_stream=sys.stdin, out_stream=sys.stdout, separator=","):
    for row in _get_transpose(in_stream):
        out_line = separator.join([repr(i) for i in row]) + separator
        print(out_line, file=out_stream)


def transpose_dict(in_stream=sys.stdin, out_stream=sys.stdout, separator=","):
    out_dict = {}
    for row in _get_transpose(in_stream):
        key = row[0]
        values = row[1:]
        if len(values) > 1:
            out_dict[key] = values
        else:
            out_dict[key] = values[0]
    pprintpp.pprint(out_dict, indent=4, width=1, stream=out_stream)


def setup_logging(sink=sys.stderr, verbose=False):
    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if verbose else "INFO")


def get_timestamp(instance=None, format="YYYYMMDD_HHmmss"):
    if instance is None:
        instance = pendulum.now()
    timestamp = instance.format(format)
    DotError.require_condition(
        timestamp != format,
        "Couldn't generate timestamp",
    )
    return timestamp


def call(command):
    # If the machine has at least python 2.4, use subprocess...sigh
    out_tmp = "/tmp/_call_stdout"
    err_tmp = "/tmp/_call_stderr"
    status = os.system("%s > %s 2> %s" % (command, out_tmp, err_tmp))
    was_successful = os.WEXITSTATUS(status) == 0
    out = open(out_tmp, "r").read().strip()
    err = open(err_tmp, "r").read().strip()
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


def print_var(value, print_fn=print):
    this_function_name = inspect.getframeinfo(inspect.currentframe()).function
    match = re.search(
        r"{}\((\w+)\)".format(this_function_name),
        inspect.getframeinfo(inspect.currentframe().f_back).code_context[0],
    )
    if match is None:
        print_fn("Couldn't interpret variable. Basic regex failed")
    var_name = match.group(1)
    print_fn("{}={}".format(var_name, value))
