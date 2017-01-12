import os, sys
from optparse import OptionParser
from dot_tools.file_tools import get_timestamp
from datetime import datetime

def main():
    parser = OptionParser(description="Generate a timestamp for the current time")
    parser.add_option(
        '-f',
        '--format',
        default = '%Y%m%d_%H%M%S',
        dest = 'datetime_format',
        help = "Set the TEXT format for the timestamp.  Default is YYYYMMDD_HHMMSS",
        metavar = 'TEXT',
    )
    (options, args) = parser.parse_args()

    try:
        current_datetime = datetime.now()
        timestamp = get_timestamp(current_datetime, datetime_format=options.datetime_format)
    except Exception as error:
        parser.error("Couldn't generate timestamp: %s" % str(error))

    print(timestamp)

if __name__ == '__main__':
    main()
