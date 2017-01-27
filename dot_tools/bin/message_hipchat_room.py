import click

from dot_tools.misc_tools import message_hipchat_room
from dot_tools.misc_tools import setup_logging


@click.command()
@click.option('-u', '--url', help="the base url for the hipchat server")
@click.option('-r', '--room', help="the id or name of the room to notify")
@click.option('-t', '--token', help="the auth token for the hipchat api")
@click.option(
    '-n/-N', '--notify/--do-not-notify', default=True,
    help="Should folks in room be notified of new message",
)
@click.option(
    '-c', '--color', default='gray',
    type=click.Choice(
        ['yellow', 'green', 'red', 'purple', 'gray', 'random']
    ),
    help="Color to highlight message with",
)
@click.option(
    '-u', '--mention-user', 'users', multiple=True,
    help="User(s) to @ mention in the room",
)
@click.option(
    '-v/-q',
    '--verbose/--quiet',
    default=False,
    help="control verbosity of status messages",
)
@click.argument('message', nargs=-1, required=True)
def main(*args, **kwargs):
    """Send a MESSAGE to a hipchat user"""
    if kwargs['verbose']:
        setup_logging()
    kwargs['message'] = ' '.join(kwargs['message'])

    message_hipchat_room(**kwargs)


if __name__ == '__main__':
    main()
