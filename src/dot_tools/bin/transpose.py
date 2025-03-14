import click

from dot_tools.misc_tools import transpose, transpose_dict


@click.command()
@click.option("-s", "--separator", default=",")
@click.option("-d", "--to-dict", is_flag=True)
def main(separator, to_dict):
    if to_dict:
        transpose_dict(separator=separator)
    else:
        transpose(separator=separator)
