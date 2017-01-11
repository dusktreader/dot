from optparse import OptionParser
from dot_tools.text_tools import underlined_header, SEP_BAR_DEFAULT_SUBSTRING

def main():
    parser = OptionParser()
    parser.add_option(
        '-s',
        '--bar_substring',
        default = SEP_BAR_DEFAULT_SUBSTRING,
        help = "Print the header using repeating TEXT as the separator",
        metavar = 'TEXT',
    )
    parser.add_option(
        '-f',
        '--print_footer',
        action = 'store_true',
        help = "Print a footer instead of a header",
    )
    (options, args) = parser.parse_args()
    print((underlined_header(' '.join(args), is_footer=options.print_footer, bar_substring=options.bar_substring)))

if __name__ == '__main__':
    main()

