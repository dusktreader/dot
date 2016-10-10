import filecmp
import fileinput
import json
import logging
import os
import platform
import sh
import shutil
import traceback

from textwrap import dedent
from contextlib import contextmanager


class IndentLoggingAdapter(logging.LoggerAdapter):
    @staticmethod
    def indent():
        indentation_level = len(traceback.extract_stack())

        # Remove pre-existing frames:
        # 2 frames for module and main() method
        # 4 frames for logging infrastructure
        return indentation_level - 6

    def process(self, msg, kwargs):
        return ('{}{}'.format('.' * self.indent() * 2, msg), kwargs)


@contextmanager
def require_condition(*args, **kwargs):

    class Accumulator:

        def __init__(self):
            self._acc = True

        def __iadd__(self, evaluated_expression):
            self._acc = self._acc and evaluated_expression

    fail_message = None
    if len(args) > 0:
        fail_message = args[0].format(*args[1:], **kwargs)
    accumulator = Accumulator()
    yield accumulator

    if not accumulator._acc:
        raise Exception("Condition failed{}".format(': ' + fail_message if fail_message else ''))


class DotInstaller:
    setup_dict = {}

    def __init__(self, home, root, message=''):
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.DEBUG)
        self.home = home
        self.root = root

        if platform.system() == 'Darwin':
            self.startup_config = os.path.join(self.home, '.bash_profile')
        else:
            self.startup_config = os.path.join(self.home, '.bashrc')

        formatter = logging.Formatter("%(asctime)s: %(levelname)8s: %(message)s")
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger = IndentLoggingAdapter(self.logger, {})

        self.message = message
        self.debug("Initializing configure/install: {}".format(message))

        install_json_file_path = os.path.join(self.root, 'etc', 'install.json')
        self.debug("Using {} as install configuration file".format(install_json_file_path))
        with open(install_json_file_path) as install_json_file:
            self.setup_dict = json.load(install_json_file)

        self.debug("Intantiated with {} as home, {} as root".format(self.home, self.root))
        self.debug("Startup config file detected at {}".format(self.statup_config))

    def __getattr__(self, name):
        if name in ['debug', 'info', 'error', 'warning']:
            return getattr(self.logger, name)

    def _make_links(self):
        for path in self.setup_dict.get('links', []):
            link_path = os.path.join(self.home, path)
            target_path = os.path.join(self.root, path)
            self.debug("Preparing to create symlink {} -> {}".format(link_path, target_path))
            with require_condition("can't link to non-existent path {}", path) as checker:
                checker += os.path.exists(target_path)
            if os.path.exists(link_path):
                if os.path.islink(link_path):
                    existing_target_path = os.readlink(link_path)
                    message = "Link already exists but points to different target: {}"
                    with require_condition(message, existing_target_path) as checker:
                        checker += os.path.samefile(existing_target_path, target_path)
                    self.debug("Skipping symlink {}: already exists".format(link_path))
                else:
                    self.debug("entity: " + str(sh.ls('-l', os.path.dirname(link_path))))
                    raise Exception("Link path already exists but is not a symlink")
            else:
                self.debug("Creating symlink {} -> {}".format(link_path, target_path))
                symlink_dir = os.path.dirname(link_path)
                if not os.path.exists(symlink_dir):
                    self.debug("Creating parent directories for symlink")
                    os.makedirs(symlink_dir)
                os.symlink(target_path, link_path)

    def _make_dirs(self):
        for path in self.setup_dict.get('mkdirs', []):
            target_path = os.path.join(self.home, path)
            self.debug("Making target directory {}".format(target_path))
            try:
                os.makedirs(target_path)
                self.debug("Created directory {}".format(target_path))
            except OSError:
                self.debug("Skipping directory creation for {}. Already exists".format(target_path))

    def _copy_files(self):
        for path in self.setup_dict.get('copy', []):
            src_path = os.path.join(self.root, path)
            dst_path = os.path.join(self.home, path)

            if os.path.exists(dst_path):
                if filecmp.cmp(src_path, dst_path, shallow=False):
                    self.debug("Skipping {}; it was already installed".format(path))
                else:
                    raise Exception("File exists at destination {} but doesn't match".format(dst_path))
            else:
                self.debug("Copying {} to {}".format(src_path, dst_path))
                copy_dir = os.path.dirname(dst_path)
                if not os.path.exists(copy_dir):
                    self.debug("Creating parent directories for copy")
                    os.makedirs(copy_dir)
                shutil.copy(src_path, dst_path)
                if 'ssh' in src_path:
                    self.debug("Updating permissions for ssh config file {}".format(dst_path))
                    sh.chmod('600', dst_path)

    def _update_dotfiles(self):
        dotfile_list_path = os.path.join(self.home, '.extra_dotfiles')
        with open(dotfile_list_path, 'a+') as dotfile_list_file:
            all_entries = dotfile_list_file.readlines()
            for path in self.setup_dict['dotfiles']:
                dotfile_path = os.path.join(self.root, path)
                entry = 'source {}'.format(dotfile_path)
                if entry not in all_entries:
                    self.logger.debug("Adding {} to .extra_dotfiles".format(dotfile_path))
                    print(entry, file=dotfile_list_file)

    def _check_virtual_env(self):
        if 'env' in sh.which("python"):
            raise Exception("You must deactivate the virtual environment to install")

    def _scrub_extra_dotfiles_block(self):
        self.debug("Scrubbing extra dotfiles block from {}".format(self.startup_config))
        in_extra_block = False
        for line in fileinput.input(self.startup_config, inplace=True):
            if 'EXTRA DOTFILES START' in line:
                in_extra_block = True
            if not in_extra_block:
                print(line, end='')
            if 'EXTRA DOTFILES END' in line:
                in_extra_block = False

    def _add_extra_dotfiles_block(self):
        self.debug("Adding extra dotfiles to startup in {}".format(self.startup_config))
        extra_dotfiles_path = os.path.join(self.home, '.extra_dotfiles')
        with open(self.startup_config, 'a') as startup_file:
            startup_file.write(dedent(
                """
                # EXTRA DOTFILES START
                if [[ -e {extra} ]]
                then
                    source {extra}
                fi
                # EXTRA DOTFILES END
                """.format(extra=extra_dotfiles_path)
            ))

    def _startup(self):
        self.debug("Using {} as startup config file".format(self.startup_config))
        if not os.path.exists(self.startup_config):
            self.debug("{} doesn't exist. Creating it")
            sh.touch(self.startup_config)
        self._scrub_extra_dotfiles_block()
        self._add_extra_dotfiles_block()

    def _extra_tasks(self):
        self.info("Installing powerline font")
        powerline_command = sh.Command(os.path.join(
            self.root, '.vim/fonts/powerline/install.sh',
        ))
        powerline_command()

    def install_dot(self):
        try:
            self.info("Making sure virtualenv is not active")
            # self._check_virtual_env()

            self.info("Create needed directories")
            self._make_dirs()

            self.info("Making links")
            self._make_links()

            self.info("Copying files")
            self._copy_files()

            self.info("Adding in extra dotfiles")
            self._update_dotfiles()

            self.info("Performing extra tasks")
            self._extra_tasks()

            self.info("Setting up startup config to include dot")
            self._startup()

            self.info("Finished installing dot")
            self.info("(To apply new changes, source {})".format(self.startup_config))

        except Exception as err:
            self.error(str(err) + ' -- aborting')
            raise

if __name__ == '__main__':
    installer = DotInstaller()
    installer.install_dot()
