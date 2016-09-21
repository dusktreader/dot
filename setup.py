import glob
import sys
import os

from setuptools import setup
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
from setuptools.command.install import install


requirements_path = 'etc/setuptools/requirements.txt'
with open(requirements_path) as requirements_file:
    requirements = requirements_file.read().splitlines()
    if len(requirements) == 0:
        message = "Failed to load requirements from {}".format(
            requirements_path
        )
        raise Exception(message)


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.pytest_args += " -c etc/pytest/pytest.ini"
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class PostInstallCommand(install):

    user_options = install.user_options + [
        ('target-dir=', 't', "The dir where dotfiles should go"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.target_dir = '~'

    def finalize_options(self):
        super().finalize_options()

    def run(self):
        super().run()
        from dot_tools.configure import DotInstaller
        installer = DotInstaller(home=os.path.expanduser(self.target_dir))
        installer.install_dot()


setup(
    name="tab's dot magic",
    author="Tucker Beck",
    author_email='tucker.beck@gmail.com',
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest,
        'install': PostInstallCommand,
    },
    scripts=glob.glob('bin/*'),
)
