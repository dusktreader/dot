from importlib.metadata import version
import click


@click.command()
def main():
    """
    Get the version of dot
    """
    print(version("dot"))
