import arrow
import json
import os
import requests
import sys
import urllib

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
    if response.text != '':
        raise Exception(response.text)


def message_hipchat_room(
        url, room, token, message,
        color='gray', notify=True, users=[], verbose=False,
):
    if verbose:
        print("Messaging room '{}' at '{}'".format(room, url))
    if len(users) > 0:
        message = '{users}: {message}'.format(
            users=', '.join(['@{}'.format(u) for u in users]),
            message=message,
        )
    if verbose:
        print("Message is: {}".format(message))

    payload = {
        "color": color,
        "notify": notify,
        "message_format": "text",
        "message": '{}'.format(message),
    }
    if verbose:
        print("Payload is: {}".format(payload))
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
    if response.text != '':
        raise Exception(response.text)


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
