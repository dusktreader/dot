import click
import pendulum


@click.command()
@click.argument("format", default="YYYYMMDD_HHmmss", required=False)
def main(format):
    """
    Generate a timestamp for the current time using FORMAT
    """
    print(pendulum.now().format(format))
