import arrow
import csv
import inspect
import io
import json
import logbook
import os
import re
import requests
import sys
import urllib

from buzz import Buzz


class DotException(Buzz):

    @classmethod
    def die(cls, *format_args, message='DIED', **format_kwargs):
        raise cls(message, *format_args, **format_kwargs)


class DotError(DotException):
    """This is a stand-in until I just rename DotException project wide"""
    pass


def transpose_in_out(separator=','):
    sys.stdout.write(transpose(sys.stdin.read(), separator=separator))


def transpose(text, separator=','):

    in_stream = io.StringIO(text)
    out_stream = io.StringIO()

    csv.writer(out_stream).writerows(
        zip(*csv.reader(
            in_stream,
            skipinitialspace=True,
            delimiter=separator,
            quotechar="'",
        ))
    )

    return out_stream.getvalue()


def setup_logging(fd=sys.stdout, level=logbook.DEBUG):
    logbook.StreamHandler(fd, level=level).push_application()


def get_timestamp(instance=None, format='YYYYMMDD_HHmmss'):
    if instance is None:
        instance = arrow.now()
    timestamp = instance.format(format)
    DotError.require_condition(
        timestamp != format,
        "Couldn't generate timestamp",
    )
    return timestamp


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


def alert_hipchat_room(
        url, room, token, title, message,
        color='red', notify=True, format='medium',
):
    payload = json.dumps({
        "color": color,
        "notify": notify,
        "message_format": "html",
        "message": '<b>{}</b>'.format(title),
        "card": {
            "id": str(arrow.get().timestamp),
            "style": "application",
            "format": format,
            "title": title,
            "description": message,
            "activity": {
                "html": '<b>{}</b>'.format(title),
            },
        },
    })
    response = requests.post(
        '{url}/v2/room/{room}/notification'.format(
            url=url,
            room=urllib.parse.quote(room),
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        },
        data=payload,
    )
    DotError.require_condition(response.text == '', response.text)


def message_hipchat_room(
    message=None,
    url=None, room=None, token=None,
    color='gray', notify=True, users=[], verbose=False,
):
    DotError.require_condition(message is not None, "No message to post")
    if url is None or room is None or token is None:
        with open(os.path.expanduser('~/.hipchat.json')) as settings_file:
            settings = json.load(settings_file)
            if url is None:
                url = settings['default_url']
            if room is None:
                room = settings['urls'][url]['default_room']
            if token is None:
                token = settings['urls'][url]['rooms'][room]['token']

    logger = logbook.Logger('Hipchat')
    if verbose:
        logger.level = logbook.DEBUG
    logger.debug("Messaging room '{}' at '{}'".format(room, url))
    if len(users) > 0:
        message = '{users}: {message}'.format(
            users=', '.join(['@{}'.format(u) for u in users]),
            message=message,
        )
    logger.debug("Message is: {}".format(message))

    payload = {
        "color": color,
        "notify": notify,
        "message_format": "text",
        "message": '{}'.format(message),
    }
    logger.debug("Payload is: {}".format(payload))
    response = requests.post(
        '{url}/v2/room/{room}/notification'.format(
            url=url,
            room=urllib.parse.quote(room),
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        },
        data=json.dumps(payload),
    )
    DotError.require_condition(response.text == '', response.text)


def message_hipchat_user(url, user, token, message, notify=True):
    payload = json.dumps({
        "notify": notify,
        "message_format": "html",
        "message": message,
    })
    response = requests.post(
        '{url}/v2/user/{user}/message'.format(
            url=url,
            user=user,
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        },
        data=payload,
    )
    if response.text != '':
        raise Exception(response.text)


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
