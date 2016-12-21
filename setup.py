import glob
import os

from setuptools import setup
from setuptools import find_packages
from setuptools.command.install import install


class PostInstallCommand(install):

    user_options = install.user_options + [
        ('target-dir=', 't', "The dir where dotfiles should go"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.target_dir = '~'

    def run(self):
        super().do_egg_install()
        from dot_tools.configure import DotInstaller
        installer = DotInstaller(
            home=os.path.expanduser(self.target_dir),
            root=os.path.abspath(os.path.dirname(__file__)),
            name="dot-tools",
        )
        installer.install_dot()


setup(
    name="dot",
    version="2.0",
    author="Tucker Beck",
    author_email='tucker.beck@gmail.com',
    install_requires=[
        'gitdb',
        'GitPython',
        'ordereddict',
        'smmap',
        'jira',
        'flake8',
        'hjson',
        'sh',
        'pytest-virtualenv',
        'pytest',
        'cmdline',
        'capturer',
        'sh',
        'buzz-lightyear',
        'requests',
        'inflection',
        ],
    packages=find_packages(),
    data_files=[('etc', ['etc/install.json'])],
    tests_require=['pytest'],
    cmdclass={
        'install': PostInstallCommand,
    },
    scripts=glob.glob('bin/*'),
)
