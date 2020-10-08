import click
import json
import os
import requests
from loguru import logger

from misc_tools import setup_logging


@click.command()
@click.option(
    "-c",
    "--config-file",
    "config_path",
    default="~/.duck/ravensroost.json",
    help="the config file to use for duckdns credentials",
)
@click.option(
    "-o",
    "--output-file",
    "log_path",
    default="~/.duck/ravensroost.log",
    help="the log file for requests to duckdns",
)
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    default=False,
    help="control verbosity of status messages",
)
def main(config_path, log_path, verbose):
    """
    Ping the duckdns server
    """
    config_path = os.path.expanduser(config_path)
    setup_logging(sink=config_path, verbose=verbose)

    with open(log_path, "a") as log_file:
        logger.add(log_file)

        with open(config_path) as config_file:
            config = json.load(config_file)
            logger.debug(
                "sending request to duckdns for domains {}".format(
                    config["domains"],
                )
            )
            request = requests.get("https://www.duckdns.org/update", params=config)
            if request.status_code != 200:
                logger.error(
                    "Failed to connect to duckdns: {}".format(
                        request.text,
                    )
                )
                return 1
            else:
                logger.debug("got response from duckdns: {}".format(request.text))
