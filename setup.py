import glob
import os
import sys

from setuptools import setup
from setuptools import find_packages
from setuptools.command.install import install as setuptools_install
from distutils.command.install import install as distutils_install


class CustomInstall(setuptools_install):
    """
    Custom post-install script as described here:
    http://stackoverflow.com/a/21196195/642511
    """
    user_options = setuptools_install.user_options + [
        ('target-dir=', 't', "The dir where dotfiles should go"),
        ('root-dir=', 't', "The dir where dotfiles come from"),
    ]

    def initialize_options(self):
        setuptools_install.initialize_options(self)
        self.target_dir = '~'
        self.root_dir = '~/dot'

    def run(self):
        ret = None
        if self.old_and_unmanageable or self.single_version_externally_managed:
            ret = distutils_install.run(self)
        else:
            caller = sys._getframe(2)
            caller_module = caller.f_globals.get('__name__', '')
            caller_name = caller.f_code.co_name

            if (
                caller_module != 'distutils.dist' or
                caller_name != 'run_commands'
            ):
                distutils_install.run(self)
            else:
                self.do_egg_install()

        from dot_tools.configure import DotInstaller
        installer = DotInstaller(
            home=os.path.expanduser(self.target_dir),
            root=os.path.expanduser(self.root_dir),
            name="dot-tools",
        )
        installer.install_dot()

        return ret


setup(
    name="dot",
    version="2.0",
    author="Tucker Beck",
    author_email='tucker.beck@gmail.com',
    install_requires=[
        'GitPython',
        'arrow',
        'bidict',
        'buzz-lightyear',
        'capturer',
        'cmdline',
        'flake8',
        'gitdb',
        'hjson',
        'inflection',
        'inflection',
        'jira',
        'ordereddict',
        'pytest',
        'pytest-virtualenv',
        'requests',
        'sh',
        'sh',
        'smmap',
        ],
    packages=find_packages(),
    data_files=[('etc', ['etc/install.json'])],
    tests_require=['pytest'],
    cmdclass={
        'install': CustomInstall,
    },
    scripts=glob.glob('bin/*'),
)
