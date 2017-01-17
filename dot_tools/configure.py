import filecmp
import fileinput
import json
import logbook
import os
import platform
import sh
import shutil
import traceback

from textwrap import dedent

from dot_tools.misc_tools import DotError


class DotInstaller:

    def __init__(self, home, root, name='unnamed', logger=None):
        if logger is None:
            self.logger = logbook.Logger('DotInstaller')
            self.logger.level = logbook.DEBUG
        else:
            self.logger = logger

        self.home = os.path.abspath(os.path.expanduser(home))
        self.root = os.path.abspath(os.path.expanduser(root))

        if platform.system() == 'Darwin':
            self.startup_config = os.path.join(self.home, '.bash_profile')
        else:
            self.startup_config = os.path.join(self.home, '.bashrc')

        self.logger.debug("Initializing configure/install for {}".format(name))

        install_json_file_path = os.path.join(self.root, 'etc', 'install.json')
        self.logger.debug(
            "Using {} as install configuration file",
            install_json_file_path,
        )
        with open(install_json_file_path) as install_json_file:
            self.setup_dict = json.load(install_json_file)

        self.logger.debug(
            "Intantiated with {} as home, {} as root",
            self.home, self.root,
        )
        self.logger.debug(
            "Startup config file detected at {}",
            self.startup_config,
        )

    def init_indent(self):
        self.cruft_depth = None
        return self.inject_func

    def inject_func(self, record):
        stack = traceback.extract_stack()
        if self.cruft_depth is None:
            self.cruft_depth = 2
            print(stack[-self.cruft_depth])
            while 'logbook' in stack[-self.cruft_depth][0]:
                self.cruft_depth += 1
        current_frame = stack[-self.cruft_depth]
        function_name = current_frame[2]
        prefix = '[{:^20}]'.format(function_name[:18])

        indentation_level = len(stack) - self.cruft_depth

        record.message = prefix + '..' * indentation_level + record.message

    def _make_links(self):
        for path in self.setup_dict.get('links', []):
            link_path = os.path.join(self.home, path)
            target_path = os.path.join(self.root, path)
            self.logger.debug(
                "Preparing to create symlink {} -> {}",
                link_path, target_path,
            )
            DotError.require_condition(
                os.path.exists(target_path),
                "can't link to non-existent path {}",
                path,
            )
            if os.path.lexists(link_path):
                self.logger.debug("Link exists. Making sure it is correct")
                DotError.require_condition(
                    os.path.islink(link_path),
                    "Link path already exists but is not a symlink",
                )
                existing_target_path = os.readlink(link_path)
                self.logger.debug("Existing target path: {}", existing_target_path)
                DotError.require_condition(
                    os.path.samefile(existing_target_path, target_path),
                    "Link already exists but points to another target: {}",
                    existing_target_path,
                )
                self.logger.debug(
                    "Skipping symlink {}: already exists",
                    link_path,
                )
            else:
                self.logger.debug(
                    "Creating symlink {} -> {}",
                    link_path, target_path,
                )
                symlink_dir = os.path.dirname(link_path)
                if not os.path.exists(symlink_dir):
                    self.logger.debug("Creating parent dirs for symlink")
                    os.makedirs(symlink_dir)
                os.symlink(target_path, link_path)

    def _make_dirs(self):
        for path in self.setup_dict.get('mkdirs', []):
            target_path = os.path.join(self.home, path)
            self.logger.debug("Making target directory {}", target_path)
            try:
                os.makedirs(target_path)
                self.logger.debug("Created directory {}", target_path)
            except OSError:
                self.logger.debug(
                    "Skipping directory creation for {}. Already exists",
                    target_path,
                )

    def _copy_files(self):
        for path in self.setup_dict.get('copy', []):
            src_path = os.path.join(self.root, path)
            dst_path = os.path.join(self.home, path)

            if os.path.exists(dst_path):
                DotError.require_condition(
                    filecmp.cmp(src_path, dst_path, shallow=False),
                    "File exists at destination {} but doesn't match", dst_path,
                )
                self.logger.debug("Skipping {} it was already installed", path)
            else:
                self.logger.debug("Copying {} to {}", src_path, dst_path)
                copy_dir = os.path.dirname(dst_path)
                if not os.path.exists(copy_dir):
                    self.logger.debug("Creating parent directories for copy")
                    os.makedirs(copy_dir)
                shutil.copy(src_path, dst_path)
                if 'ssh' in src_path:
                    self.logger.debug(
                        "Updating permissions for ssh config file {}", dst_path,
                    )
                    sh.chmod('600', dst_path)

    def _extra_scripts(self):
        for path in self.setup_dict.get('scripts', []):
            exe_path = os.path.join(self.root, path)

            DotError.require_condition(
                os.path.exists(exe_path),
                "Extra script doesn't exist: {}",
                exe_path)
            self.logger.debug("Executing extra script {}", path)
            extra_command = sh.Command(exe_path)
            extra_command()

    def _update_dotfiles(self):
        dotfile_list_path = os.path.join(self.home, '.extra_dotfiles')
        if not os.path.exists(dotfile_list_path):
            sh.touch(dotfile_list_path)
        with open(dotfile_list_path, 'r+') as dotfile_list_file:
            all_entries = [l.strip() for l in dotfile_list_file.readlines()]
            for path in self.setup_dict['dotfiles']:
                dotfile_path = os.path.join(self.root, path)
                entry = 'source {}'.format(dotfile_path)
                if entry not in all_entries:
                    self.logger.debug(
                        "Adding {} to .extra_dotfiles", dotfile_path,
                    )
                    print(entry, file=dotfile_list_file)

    def _check_virtual_env(self):
        DotError.require_condition(
            'env' not in sh.which("python"),
            "You must deactivate the virtual environment to install",
        )

    def _scrub_extra_dotfiles_block(self):
        self.logger.debug(
            "Scrubbing extra dotfiles block from {}",
            self.startup_config,
        )
        in_extra_block = False
        for line in fileinput.input(self.startup_config, inplace=True):
            if 'EXTRA DOTFILES START' in line:
                in_extra_block = True
            if not in_extra_block:
                print(line, end='')
            if 'EXTRA DOTFILES END' in line:
                in_extra_block = False

    def _add_extra_dotfiles_block(self):
        self.logger.debug(
            "Adding extra dotfiles to startup in {}",
            self.startup_config,
        )
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
        self.logger.debug(
            "Using {} as startup config file",
            self.startup_config,
        )
        if not os.path.exists(self.startup_config):
            self.logger.debug(
                "{} doesn't exist. Creating it",
                self.startup_config,
            )
            sh.touch(self.startup_config)
        self._scrub_extra_dotfiles_block()
        self._add_extra_dotfiles_block()

    def install_dot(self):
        self.logger.info("Started Installing dot")
        with DotError.handle_errors('Install failed. Aborting'):
            with logbook.Processor(self.init_indent()):
                self.logger.debug("Making sure virtualenv is not active")
                # self._check_virtual_env()

                self.logger.debug("Create needed directories")
                self._make_dirs()

                self.logger.debug("Making links")
                self._make_links()

                self.logger.debug("Copying files")
                self._copy_files()

                self.logger.debug("Adding in extra dotfiles")
                self._update_dotfiles()

                self.logger.debug("Executing extra scripts")
                self._extra_scripts()

                self.logger.debug("Setting up startup config to include dot")
                self._startup()

        self.logger.info("Finished installing dot")
        self.logger.info(
            "(To apply new changes, source {})",
            self.startup_config,
        )
