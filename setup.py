import os
import re
import sys

from setuptools import setup
from setuptools import find_packages


if sys.version_info < (3, 0):
    sys.exit('dot requires python 3')


if sys.version_info < (3, 0):
    sys.exit('dot requires python 3')


def find_console_scripts():
    scripts = []
    for package in find_packages(exclude=["tests"]):
        if 'bin' not in package.split('.'):
            continue

        for module in os.listdir(package.replace('.', '/')):
            if not re.match(r'[^_].*\.py', module):
                continue

            module = module.replace('.py', '')
            dashed = module.replace('_', '-')
            script = '{dashed} = {package}.{module}:main'.format(**locals())
            scripts.append(script)
    print("found console scripts:")
    for script in scripts:
        print("    ", script)
    return scripts


setup(
    name="dot",
    version="2.0",
    author="Tucker Beck",
    author_email='tucker.beck@gmail.com',
    install_requires=[
        'GitPython',
        'arrow',
        'bidict',
        'click',
        'capturer',
        'cmdline',
        'flake8',
        'gitdb',
        'git-url-parse',
        'inflection',
        'jedi',
        'jira',
        'logbook',
        'ordereddict',
        'pprintpp',
        'py-buzz',
        'pydon',
        'pytest',
        'requests',
        'sh',
        'sh',
        'smmap',
    ],
    packages=find_packages(exclude=["tests"]),
    data_files=[('etc', ['etc/install.json'])],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': find_console_scripts(),
    },
)
