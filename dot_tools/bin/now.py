import click
import arrow

from dot_tools.misc_tools import get_timestamp


@click.command()
@click.argument('format', default='YYYYMMDD_HHmmss', required=False)
def main(format):
    """
    Generate a timestamp for the current time using FORMAT
    """
    print(get_timestamp(format=format))


if __name__ == '__main__':
    main()
