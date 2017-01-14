import os, sys
import arrow
from optparse import OptionParser
from dot_tools.file_tools import back, back_recover, back_cleanup
from distutils.util import strtobool
from datetime import datetime

def main():
    parser = OptionParser(description="Copies files to hidden, timestamped backups in the same directory")
    parser.add_option(
        '-r',
        '--recover',
        action = 'store_true',
        default = False,
        help = "Recover data from backup files",
    )
    parser.add_option(
        '-d',
        '--delete_existing',
        action = 'store_true',
        default = False,
        help = "Delete existing original file after backing up.  Only used when not recovering or cleaning up",
    )
    parser.add_option(
        '-c',
        '--cleanup',
        action = 'store_true',
        default = False,
        help = "Delete any backup files",
    )
    parser.add_option(
        '-t',
        '--timestamp',
        default = None,
        help = "Set the timestamp manually",
        metavar = 'TEXT',
    )
    parser.add_option(
        '-f',
        '--force',
        action = 'store_true',
        default = False,
        help = "Peform recover or cleanup without prompting for confirmation",
    )
    parser.add_option(
        '-v',
        '--verbose',
        action = 'store_true',
        default = False,
        help = "Print information about the actions being taken",
    )
    (options, args) = parser.parse_args()

    file_paths = [os.path.expanduser(f) for f in args]

    if options.timestamp != None:
        with DotException.handle_errors("Could not parse timestamp"):
            options.timestamp = arrow.get(options.timestamp)

    for file_path in file_paths:
        if options.recover == False and options.cleanup == False:
            try:
                back(
                    file_path,
                    current_datetime=options.timestamp,
                    delete_existing=options.delete_existing,
                    verbose=options.verbose
                )
            except Exception as error:
                print("Could not backup file: %s" % str(error), file=sys.stderr)
        else:
            if options.recover == True:
                try:
                    back_recover(file_path, latest_datetime=options.timestamp, verbose=options.verbose)
                except Exception as error:
                    print("Could not recover backup file: %s" % str(error), file=sys.stderr)
            if options.cleanup == True:
                try:
                    back_cleanup(file_path, verbose=options.verbose)
                except Exception as error:
                    print("Could not clean up backup files: %s" % str(error), file=sys.stderr)

if __name__ == '__main__':
    main()

