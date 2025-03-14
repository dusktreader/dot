import click
from dot_tools.text_tools import (
    sep_bar,
    SEP_BAR_MAX_LENGTH,
    SEP_BAR_DEFAULT_LENGTH,
    SEP_BAR_DEFAULT_SUBSTRING,
)


@click.command()
@click.option(
    "-l",
    "--bar-length",
    type=int,
    default=SEP_BAR_DEFAULT_LENGTH,
    help=(
        "Print BAR_LENGTH repetitions of the bar_substring."
        "(At least 1 will be printed)"
    ),
)
@click.option(
    "-s",
    "--bar_substring",
    default=SEP_BAR_DEFAULT_SUBSTRING,
    help=(
        "Print BAR_LENGTH repetitions of BAR_SUBSTRING."
        "(Truncated to {} characters)".format(SEP_BAR_MAX_LENGTH)
    ),
)
def main(**kwargs):
    print(sep_bar(**kwargs))
