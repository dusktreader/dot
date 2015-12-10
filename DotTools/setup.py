import os
from setuptools import setup

requirements_path = 'requirements.txt'
with open(requirements_path) as requirements_file:
    try:
        requirements = requirements_file.read().splitlines()
    except Exception as err:
        raise Exception("Failed to load requirements from {path}: {err}".format(
            path=requirements_path,
            err=err,
            ))

setup(
    name             = 'DotTools',
    author           = 'Tucker Beck',
    author_email     = 'tucker.beck@gmail.com',
    license          = 'LICENSE.txt',
    description      = 'General tools intended to be used mostly from a shell command line',
    long_description = open('README.txt').read(),
    install_requires = requirements,
    packages         = [
        'dot_tools'
    ],
    scripts = [ os.path.join('bin', b) for b in os.listdir('bin') ],
)

