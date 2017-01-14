import click

from dot_tools.text_tools import underlined_header, SEP_BAR_DEFAULT_SUBSTRING


@click.command()
@click.option(
    '-s', '--bar-substring',
    default=SEP_BAR_DEFAULT_SUBSTRING,
    help="Print the header using repeating BAR_SUBSTRING as the separator",
)
@click.option(
    '-f/-h', '--print-footer/--print-header', 'is_footer',
    default=False,
    help="Select whether to print header or footer",
)
@click.argument('message', nargs=-1, required=True)
def main(**kwargs):
    kwargs['message'] = ' '.join(kwargs['message'])
    print(underlined_header(**kwargs))


if __name__ == '__main__':
    main()
