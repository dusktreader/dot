import click
import json
import logbook
import os
import requests

from dot_tools.misc_tools import setup_logging, DotError


@click.command()
@click.option(
    '-c', '--config-file', 'config_path',
    default='~/.duck/ravensroost.json',
    help="the config file to use for duckdns credentials",
)
@click.option(
    '-o', '--output-file', 'log_path',
    default='~/.duck/ravensroost.log',
    help="the log file for requests to duckdns",
)
def main(config_path, log_path):
    """
    Ping the duckdns server
    """
    config_path = os.path.expanduser(config_path)
    log_path = os.path.expanduser(log_path)

    with open(log_path, 'a') as log_file:
        setup_logging(fd=log_file)
        logger = logbook.Logger('DuckDNS')

        with open(config_path) as config_file:
            config = json.load(config_file)
            logger.debug("sending request to duckdns for domains {}".format(
                config['domains'],
            ))
            request = requests.get(
                'https://www.duckdns.org/update',
                params=config
            )
            if request.status_code != 200:
                logger.error('Failed to connect to duckdns: {}'.format(
                    request.text,
                ))
                return 1
            else:
                logger.debug("got response from duckdns: {}".format(request.text))


if __name__ == '__main__':
    main()
