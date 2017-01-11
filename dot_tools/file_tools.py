import os
import re
import shutil
import sys

from datetime import datetime

from dot_tools.misc_tools import DotException
from dot_tools.git_tools import GitManager


class FileException(DotException):
    pass


def get_timestamp(datetime_instance=None, datetime_format=None):
    if datetime_instance is None:
        datetime_instance = datetime.now()
    if datetime_format is None:
        datetime_format = '%Y%m%d_%H%M%S'
    timestamp = datetime_instance.strftime(datetime_format)
    # TODO: Use arrow
    FileException.require_condition(
        timestamp != datetime_format,
        "Invalid format string",
    )
    return timestamp


def back(
    file_path, current_datetime=None, delete_existing=False, verbose=False,
):
    FileException.require_condition(
        os.path.exists(file_path),
        'Could not backup nonexistant file {}',
        file_path,
    )
    timestamp = get_timestamp(current_datetime)

    (file_directory, file_name) = os.path.split(file_path)
    tagged_file_name = '.%s.%s' % (file_name, timestamp)
    tagged_file_path = os.path.join(file_directory, tagged_file_name)

    with FileException.handle_errors(
        'Could not backup file to {}',
        tagged_file_path,
    ):
        if verbose:
            print(
                "Backing up {} to {}".format(file_path, tagged_file_path),
                file=sys.stderr,
            )
        shutil.copyfile(file_path, tagged_file_path)

    if delete_existing:
        with FileException.handle_errors(
            'Could not remove original file {}',
            file_path,
        ):
            if verbose:
                print("Deleting original file %s" % file_path, file=sys.stderr)
            os.remove(file_path)


def back_recover(file_path, latest_datetime=None, verbose=False):
    if latest_datetime is None:
        latest_datetime = datetime.now()

    (file_directory, file_name) = os.path.split(file_path)

    regex = r'^\.' + file_name + r'\.\d{8}_\d{6}$'
    matching_files = [
        f for f
        in os.listdir(file_directory or '.')
        if re.match(regex, f)
    ]
    FileException.require_condition(
        len(matching_files) > 0,
        'Could not recover backup file: could not find matching backup files',
    )
    matching_files.sort()

    comparison_file_name = '.{}.{}'.format(
        file_name,
        get_timestamp(latest_datetime),
    )
    closest_file_name = ''
    while True:
        closest_file_name = matching_files.pop()
        if len(matching_files) == 0:
            break
        if closest_file_name <= comparison_file_name:
            break
    closest_file_path = os.path.join(file_directory, closest_file_name)

    with FileException.handle_errors(
        'Could not recover file from {}',
        file_path,
    ):
        if verbose:
            print(
                "Recovering %s from backup {}".format(
                    file_path, closest_file_path
                ),
                file=sys.stderr,
            )
        shutil.copyfile(closest_file_path, file_path)


def back_cleanup(file_path, verbose=False):
    (file_directory, file_name) = os.path.split(file_path)

    regex = r'^\.' + file_name + r'\.\d{8}_\d{6}$'
    file_paths = [
        os.path.join(file_directory, f) for f
        in os.listdir(file_directory or '.')
        if re.match(regex, f)
    ]
    for file_path in file_paths:
        if verbose:
            print("Cleaning up backup file %s " % file_path, file=sys.stderr)
        os.remove(file_path)


def find_test_file(file_path, git_man=None):
    DotException.require_condition(
        os.path.exists(file_path),
        "Can't lookup test for non-extant source: {}",
        file_path,
    )
    if git_man is None:
        git_man = GitManager(file_path)
    top = git_man.toplevel(file_path)

    git_man.logger.debug('Making sure source path is not a test path')
    temp_dir = os.path.abspath(file_path)
    while temp_dir != top:
        DotException.require_condition(
            not os.path.basename(temp_dir).startswith('test'),
            "Found test file or dir in source file path",
        )
        temp_dir = os.path.dirname(temp_dir)

    source_dir_path = git_man.find_source_path(top)

    git_man.logger.debug('Searching for test base path')
    possible_test_dirs = [
        os.path.join(top, 'test'),
        os.path.join(top, 'tests'),
        os.path.join(source_dir_path, 'test'),
        os.path.join(source_dir_path, 'tests'),
    ]
    test_dir_path = None
    for possible_test_dir in possible_test_dirs:
        if os.path.exists(possible_test_dir):
            test_dir_path = possible_test_dir
    DotException.require_condition(
        test_dir_path is not None,
        "Could not find a test dir path",
    )
    git_man.logger.debug('Base test path found at {}', test_dir_path)

    relative_file_path_from_source = os.path.relpath(
        file_path,
        source_dir_path,
    )
    (middle_path, file_name) = os.path.split(relative_file_path_from_source)
    test_file_name = 'test_' + file_name
    git_man.logger.debug('Test file name should be {}', test_file_name)
    test_path = os.path.join(
        test_dir_path,
        middle_path,
        'test_' + file_name,
    )
    git_man.logger.debug('Test file path should be {}', test_path)
    return test_path


def find_source_file(test_path, git_man=None):
    DotException.require_condition(
        os.path.exists(test_path),
        "Can't lookup source for non-extant test",
    )
    if git_man is None:
        git_man = GitManager(test_path)
    top = git_man.toplevel(test_path)

    possible_test_dirs = ['test', 'tests']
    test_dir_path = None
    temp_dir = os.path.abspath(test_path)
    git_man.logger.debug('Looking for base test directory')
    while temp_dir != top:
        if os.path.basename(temp_dir) in possible_test_dirs:
            test_dir_path = temp_dir
        temp_dir = os.path.dirname(temp_dir)
    DotException.require_condition(
        test_dir_path is not None,
        "Can't find test dir. Must not be *in* test dir",
    )
    git_man.logger.debug('Detected {} as test dir', test_dir_path)

    source_dir_path = git_man.find_source_path(top)

    relative_test_path_from_test = os.path.relpath(test_path, test_dir_path)
    (middle_path, test_name) = os.path.split(relative_test_path_from_test)
    source_name = re.sub(r'^test_', '', test_name)
    git_man.logger.debug('Source file name should be {}', source_name)
    source_path = os.path.join(source_dir_path, middle_path, source_name)
    git_man.logger.debug('Source file path should be {}', source_path)
    return source_path
