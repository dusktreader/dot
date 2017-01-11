from optparse import OptionParser
from dot_tools.text_tools import sep_bar, \
    SEP_BAR_MAX_LENGTH,                   \
    SEP_BAR_DEFAULT_LENGTH,               \
    SEP_BAR_DEFAULT_SUBSTRING             \

def main():
    parser = OptionParser()
    parser.add_option(
        '-l',
        '--bar_length',
        type='int',
        default=SEP_BAR_DEFAULT_LENGTH,
        help="Print NUMBER repetitions of the bar_substring. (At least 1 will be printed)",
        metavar='NUMBER'
    )
    parser.add_option(
        '-s',
        '--bar_substring',
        default=SEP_BAR_DEFAULT_SUBSTRING,
        help="Print bar_length repetitions of the bar TEXT. (Truncated to %d characters)" % SEP_BAR_MAX_LENGTH,
        metavar='TEXT'
    )
    (options, args) = parser.parse_args()
    print(sep_bar(options.bar_length, options.bar_substring))

if __name__ == '__main__':
    main()

