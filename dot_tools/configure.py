import filecmp
import fileinput
import json
import os
import platform
import sh
import shutil
import sys
import traceback

from textwrap import dedent

from loguru import logger

from dot_tools.misc_tools import DotError


class DotInstaller:

    def __init__(self, home, root, name='unnamed', setup_dict=None):
        self.home = os.path.abspath(os.path.expanduser(home))
        self.root = os.path.abspath(os.path.expanduser(root))

        bash_profile_path = os.path.join(self.home, '.bash_profile')
        bashrc_path = os.path.join(self.home, '.bashrc')
        if platform.system() == 'Darwin':
            bash_profile_path = os.path.join(self.home, '.bash_profile')
            with open(bash_profile_path, 'r') as bash_profile_file:
                bash_profile = bash_profile_file.read()
            if 'source {}'.format(bashrc_path) not in bash_profile:
                with open(bash_profile_path, 'a') as bash_profile_file:
                    bash_profile_file.write('source {}'.format(bashrc_path))

        self.startup_config = bashrc_path

        logger.debug("Initializing configure/install for {}".format(name))

        if setup_dict is None:
            install_json_file_path = os.path.join(self.root, 'etc', 'install.json')
            logger.debug(
                "Using {} as install configuration file",
                install_json_file_path,
            )
            with open(install_json_file_path) as install_json_file:
                self.setup_dict = json.load(install_json_file)
        else:
            self.setup_dict = setup_dict

        logger.debug(
            "Intantiated with {} as home, {} as root",
            self.home, self.root,
        )
        logger.debug(
            "Startup config file detected at {}",
            self.startup_config,
        )

    def _make_links(self):
        for path in self.setup_dict.get('links', []):
            link_path = os.path.join(self.home, path)
            target_path = os.path.join(self.root, path)
            logger.debug(
                "Preparing to create symlink {} -> {}",
                link_path, target_path,
            )
            DotError.require_condition(
                os.path.exists(target_path),
                "can't link to non-existent path {}".format(path),
            )
            if os.path.lexists(link_path):
                logger.debug("Link exists. Checking target")
                DotError.require_condition(
                    os.path.islink(link_path),
                    "Link path already exists but is not a symlink: {}".format(link_path),
                )
                existing_target_path = os.readlink(link_path)
                logger.debug(
                    "Existing target path: {}",
                    existing_target_path,
                )
                if not os.path.exists(existing_target_path):
                    logger.warning(
                        "Link exists target is missing: {}",
                        existing_target_path,
                    )
                    logger.debug("unlinking existing link")
                    os.unlink(link_path)
                elif not os.path.samefile(existing_target_path, target_path):
                    logger.warning(
                        "Link already exists but points to another target: {}",
                        existing_target_path,
                    )
                    logger.debug("unlinking existing link")
                    os.unlink(link_path)
                else:
                    logger.debug(
                        "Skipping symlink {}: already exists and is corret",
                        link_path,
                    )
                    continue
            logger.debug(
                "Creating symlink {} -> {}",
                link_path, target_path,
            )
            symlink_dir = os.path.dirname(link_path)
            if not os.path.exists(symlink_dir):
                logger.debug("Creating parent dirs for symlink")
                os.makedirs(symlink_dir)
            os.symlink(target_path, link_path)

    def _make_dirs(self):
        for path in self.setup_dict.get('mkdirs', []):
            target_path = os.path.join(self.home, path)
            logger.debug("Making target directory {}", target_path)
            try:
                os.makedirs(target_path)
                logger.debug("Created directory {}", target_path)
            except OSError:
                logger.debug(
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
                    "File exists at destination {} but doesn't match".format(dst_path),
                )
                logger.debug("Skipping {} it was already installed", path)
            else:
                logger.debug("Copying {} to {}", src_path, dst_path)
                copy_dir = os.path.dirname(dst_path)
                if not os.path.exists(copy_dir):
                    logger.debug("Creating parent directories for copy")
                    os.makedirs(copy_dir)
                shutil.copy(src_path, dst_path)
                if 'ssh' in src_path:
                    logger.debug(
                        "Updating permissions for ssh config file {}", dst_path,
                    )
                    sh.chmod('600', dst_path)

    def _extra_scripts(self):
        for path in self.setup_dict.get('scripts', []):
            exe_path = os.path.join(self.root, path)

            DotError.require_condition(
                os.path.exists(exe_path),
                "Extra script doesn't exist: {}".format(exe_path),
            )
            logger.debug("Executing extra script {}", path)
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
                    logger.debug(
                        "Adding {} to .extra_dotfiles", dotfile_path,
                    )
                    print(entry, file=dotfile_list_file)

    def _check_virtual_env(self):
        print('prefix: ', sys.prefix)
        print('base_prefix: ', sys.base_prefix)
        DotError.require_condition(
            sys.prefix == sys.base_prefix,
            "You must deactivate the virtual environment to install",
        )

    def _scrub_extra_dotfiles_block(self):
        logger.debug(
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
        logger.debug(
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
                    export DOT_HOME={root}
                    source {extra}
                fi
                # EXTRA DOTFILES END
                """.format(
                    root=self.root,
                    extra=extra_dotfiles_path,
                )
            ).strip())

    def _startup(self):
        logger.debug(
            "Using {} as startup config file",
            self.startup_config,
        )
        if not os.path.exists(self.startup_config):
            logger.debug(
                "{} doesn't exist. Creating it",
                self.startup_config,
            )
            sh.touch(self.startup_config)
        self._scrub_extra_dotfiles_block()
        self._add_extra_dotfiles_block()

    def install_dot(self):
        logger.info("Started Installing dot")
        with DotError.handle_errors('Install failed. Aborting'):
            logger.debug("Making sure virtualenv is not active")
            # self._check_virtual_env()

            logger.debug("Create needed directories")
            self._make_dirs()

            logger.debug("Making links")
            self._make_links()

            logger.debug("Copying files")
            self._copy_files()

            logger.debug("Adding in extra dotfiles")
            self._update_dotfiles()

            logger.debug("Executing extra scripts")
            self._extra_scripts()

            logger.debug("Setting up startup config to include dot")
            self._startup()

        logger.info("Finished installing dot")
        logger.info(
            "(To apply new changes, source {})",
            self.startup_config,
        )
