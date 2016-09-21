import sys, os, re, shutil
from datetime import datetime
from dot_tools.text_tools import underlined_header

class FileException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

def get_timestamp(datetime_instance=None, datetime_format=None):
    if datetime_instance is None:
        datetime_instance = datetime.now()
    if datetime_format is None:
        datetime_format = '%Y%m%d_%H%M%S'
    timestamp = datetime_instance.strftime(datetime_format)
    if timestamp == datetime_format:
        raise FileException("Invalid format string")
    return timestamp

def back(file_path, current_datetime=None, delete_existing=False, verbose=False):
    if not os.path.exists(file_path):
        raise FileException('Could not backup nonexistant file %s' % file_path)

    timestamp = get_timestamp(current_datetime)

    (file_directory, file_name) = os.path.split(file_path)
    tagged_file_name = '.%s.%s' % (file_name, timestamp)
    tagged_file_path = os.path.join(file_directory, tagged_file_name)

    try:
        if verbose:
            print("Backing up %s to %s" % (file_path, tagged_file_path), file=sys.stderr)
        shutil.copyfile(file_path, tagged_file_path)
    except IOError as error:
        raise FileException('Could not backup file to %s: %s' % (tagged_file_path, str(error)))

    try:
        if delete_existing:
            if verbose:
                print("Deleting original file %s" % file_path, file=sys.stderr)
            os.remove(file_path)
    except IOError as error:
        raise FileException('Could not remove original file %s' % file_path)

def back_recover(file_path, latest_datetime=None, verbose=False):
    if latest_datetime is None:
        latest_datetime = datetime.now()

    (file_directory, file_name) = os.path.split(file_path)

    regex = r'^\.' + file_name + r'\.\d{8}_\d{6}$'
    matching_files = [f for f in os.listdir(file_directory or '.') if re.match(regex, f)]
    if len(matching_files) == 0:
        raise IOError('Could not recover backup file: could not find matching backup files')
    matching_files.sort()

    comparison_file_name = '.%s.%s' % (file_name, get_timestamp(latest_datetime))
    closest_file_name = ''
    while True:
        closest_file_name = matching_files.pop()
        if len(matching_files) == 0 or closest_file_name <= comparison_file_name:
            break
    closest_file_path = os.path.join(file_directory, closest_file_name)

    try:
        if verbose == True:
            print("Recovering %s from backup %s" % (file_path, closest_file_path), file=sys.stderr)
        shutil.copyfile(closest_file_path, file_path)
    except IOError as error:
        raise FileException('Could not recover file from %s: %s' % (tagged_file_path, str(error)))

def back_cleanup(file_path, verbose=False):
    (file_directory, file_name) = os.path.split(file_path)

    regex = r'^\.' + file_name + r'\.\d{8}_\d{6}$'
    file_paths = [os.path.join(file_directory,f) for f in os.listdir(file_directory or '.') if re.match(regex, f)]
    for file_path in file_paths:
        if verbose == True:
            print("Cleaning up backup file %s " % file_path, file=sys.stderr)
        os.remove(file_path)

