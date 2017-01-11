from optparse import OptionParser
from dot_tools.git_tools import is_git, pushup

def main():
    parser = OptionParser(usage = "usage: %prog [%prog_options]")
    parser.add_option(
        '-v',
        '--verbose',
        action = 'store_true',
        default = False,
        help = "Print the status of the actions as execution proceeds",
    )
    parser.disable_interspersed_args()
    (options, args) = parser.parse_args()

    if not is_git():
        parser.error("Can't push a branch from a non-git directory")

    pushup(verbose=options.verbose)

if __name__ == '__main__':
    main()

