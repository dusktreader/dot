import os
import re

from dot_tools.misc_tools import DotError, get_timestamp
from dot_tools.git_tools import GitManager


def find_test_file(file_path, git_man=None):
    DotError.require_condition(
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
        DotError.require_condition(
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
    DotError.require_condition(
        test_dir_path is not None,
        "Could not find a test dir path",
    )
    git_man.logger.debug('Base test path found at {}', test_dir_path)

    relative_file_path_from_source = os.path.relpath(
        file_path,
        source_dir_path,
    )
    (middle_path, filename) = os.path.split(relative_file_path_from_source)
    test_filename = 'test_' + filename
    git_man.logger.debug('Test file name should be {}', test_filename)
    test_path = os.path.join(
        test_dir_path,
        middle_path,
        'test_' + filename,
    )
    git_man.logger.debug('Test file path should be {}', test_path)
    return test_path


def find_source_file(test_path, git_man=None):
    DotError.require_condition(
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
    DotError.require_condition(
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
