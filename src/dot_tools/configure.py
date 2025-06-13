import filecmp
import fileinput
import platform
import shutil
import subprocess
from typing import Annotated

import buzz
import pydantic
import snick
import yaml
from loguru import logger
from pathlib import Path
from typerdrive import terminal_message

from dot_tools.exceptions import DotError
from dot_tools.spinner import report_block


CHECK = "" # Yellow
STATUS = "►" # Blue
CONFIRM = "" # Green
FAIL = "" # Red


def parse_octal(value: str) -> int:
    with buzz.handle_errors("Invalid octal value", raise_exc_class=ValueError):
        return int(value.removeprefix("0o"), 8)


class FileSpecs(pydantic.BaseModel):
    path: Path
    perms: Annotated[int, pydantic.BeforeValidator(parse_octal)]


class ScriptSpecs(pydantic.BaseModel):
    generic: str | None = None
    linux: str | None = None
    darwin: str | None = None


class ToolSpecs(pydantic.BaseModel):
    name: str
    check: str
    scripts: ScriptSpecs


class InstallManifest(pydantic.BaseModel):
    link_paths: Annotated[list[Path], pydantic.Field(default_factory=lambda: [])]
    copy_paths: Annotated[list[Path | FileSpecs], pydantic.Field(default_factory=lambda: [])]
    dotfile_paths: Annotated[list[Path], pydantic.Field(default_factory=lambda: [])]
    mkdir_paths: Annotated[list[Path], pydantic.Field(default_factory=lambda: [])]
    tools: Annotated[list[ToolSpecs], pydantic.Field(default_factory=lambda: [])]


class DotInstaller:
    root: Path
    home: Path
    startup_config: Path
    install_manifest: InstallManifest

    def __init__(self, root: Path, override_home: Path | None = None):
        self.root = root.resolve().absolute()
        self.home = override_home or Path.home().absolute()
        logger.debug(f"Initializing with {self.home} as home, {self.root} as root")

        if platform.system() == 'Darwin':
            rc_path = self.home / ".zshrc"
        else:
            rc_path = self.home / ".bashrc"

        self.startup_config = rc_path
        logger.debug(f"Startup config file detected at {self.startup_config}")

        logger.debug("Configuring dot!")

        manifest_path = self.root / "etc/install.yaml"
        logger.debug(f"Using {manifest_path} as install manifest")
        self.install_manifest = InstallManifest(**yaml.safe_load(manifest_path.read_text()))

        logger.debug(f"Loaded install manifest from {manifest_path}")

    def _make_links(self):
        logger.debug("Linking files from manifest")
        for path in self.install_manifest.link_paths:
            logger.debug(f"Processing {path}")

            link_path: Path = self.home / path
            target_path: Path = self.root / path
            logger.debug(f"Preparing to create symlink {link_path} -> {target_path}")

            DotError.require_condition(target_path.exists(), f"can't link to non-existent path {target_path}")
            if link_path.exists(follow_symlinks=False):
                logger.debug("Link exists. Checking target")

                DotError.require_condition(link_path.is_symlink(), "Link path already exists but is not a symlink")
                existing_target_path = link_path.readlink()

                logger.debug(f"Found existing target path: {existing_target_path}")
                if not existing_target_path.exists():
                    logger.warning(f"Link exists target is missing: {existing_target_path}")
                    logger.debug("Unlinking existing link")
                    link_path.unlink()
                elif not existing_target_path.samefile(target_path):
                    logger.warning(f"Link already exists but points to another target: {existing_target_path}")
                    logger.debug("Unlinking existing link")
                    link_path.unlink()
                else:
                    logger.debug(f"Skipping symlink {link_path} as it already exists and is correct")
                    continue

            logger.debug(f"Creating symlink {link_path} -> {target_path}")
            if not link_path.parent.exists():
                logger.debug("Creating parent dirs for symlink")
                link_path.parent.mkdir(parents=True)
            link_path.symlink_to(target_path)

    def _make_dirs(self):
        logger.debug("Making directories from manifest")
        for path in self.install_manifest.mkdir_paths:
            logger.debug(f"Processing {path}")

            target_path = self.home / path
            logger.debug(f"Checking/making target directory {target_path}")
            target_path.mkdir(parents=True, exist_ok=True)

    def _copy_files(self):
        logger.debug("Copying files from manifest")
        for item in self.install_manifest.copy_paths:
            path: Path
            perms: int | None
            if isinstance(item, FileSpecs):
                path = item.path
                perms = item.perms
            else:
                path = item
                perms = None

            logger.debug(f"Processing {path}")

            src_path = self.root / path
            dst_path = self.home / path
            logger.debug(f"Preparing to copy file {src_path} -> {dst_path}")

            if dst_path.exists():
                DotError.require_condition(
                    filecmp.cmp(src_path, dst_path, shallow=False),
                    f"File exists at destination {dst_path} but doesn't match",
                )
                logger.debug(f"Skipping {path} it was already installed")
            else:
                logger.debug(f"Copying {path}")
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_path, dst_path)
                if perms is not None:
                    logger.debug(f"Updating permissions for file {dst_path}")
                    dst_path.chmod(perms)

    def _install_tools(self):
        from time import sleep
        with report_block(f"Installing tools", context_level="DEBUG"):
            sleep(1)
            for tool in self.install_manifest.tools:
                with report_block(f"Installing {tool.name}", context_level="DEBUG"):
                    sleep(1)
                    with DotError.handle_errors(f"Failed to install tool {tool.name}"):
                        logger.debug(f"{CHECK} Checking if {tool.name} is installed")
                        result = subprocess.run(tool.check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        if result.returncode == 0:
                            logger.debug(f"{CONFIRM} {tool.name} is already installed")
                            continue

                        script: str
                        if tool.scripts.generic:
                            logger.debug("Using generic script for tool installation")
                            script = tool.scripts.generic
                        elif platform.system() == 'Linux':
                            logger.debug("Using linux script for tool installation")
                            script = DotError.enforce_defined(tool.scripts.linux, "No linux script defined for tool")
                        elif platform.system() == 'Darwin':
                            logger.debug("Using darwin script for tool installation")
                            script = DotError.enforce_defined(tool.scripts.darwin, "No darwin script defined for tool")
                        else:
                            raise DotError(f"Unsupported platform {platform.system()} for tool {tool.name}")

                        logger.debug(f"Running installation script for {tool.name}")
                        result = subprocess.run(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        DotError.require_condition(result.returncode == 0, f"Failed to install {tool.name}: {result.stdout.decode()}")
                        logger.debug(f"{CONFIRM} completed {tool.name} installation")

    def _update_dotfiles(self):
        logger.debug("Adding dotfiles from manifest")
        dotfile_list_path = self.home / ".extra_dotfiles"
        if not dotfile_list_path.exists():
            dotfile_list_path.touch()

        with open(dotfile_list_path, 'r+') as dotfile_list_file:
            all_entries = [l.strip() for l in dotfile_list_file.readlines()]

            for path in self.install_manifest.dotfile_paths:
                logger.debug(f"Processing {path}")

                dotfile_path = self.root / path
                entry = f"source {dotfile_path}"
                if entry not in all_entries:
                    logger.debug(f"Adding {dotfile_path} to .extra_dotfiles")
                    print(entry, file=dotfile_list_file)

    def _scrub_extra_dotfiles_block(self):
        logger.debug(f"Scrubbing extra dotfiles block from {self.startup_config}")
        in_extra_block = False
        for line in fileinput.input(self.startup_config, inplace=True):
            if 'EXTRA DOTFILES START' in line:
                in_extra_block = True
            if not in_extra_block:
                print(line, end='')
            if 'EXTRA DOTFILES END' in line:
                in_extra_block = False

    def _add_extra_dotfiles_block(self):
        logger.debug(f"Adding extra dotfiles to startup in {self.startup_config}")
        extra_dotfiles_path = self.home / ".extra_dotfiles"
        with open(self.startup_config, 'a') as startup_file:
            startup_file.write(
                snick.dedent(
                    f"""
                    # EXTRA DOTFILES START
                    if [[ -e {extra_dotfiles_path} ]]
                    then
                        export DOT_HOME={self.root}
                        source {extra_dotfiles_path}
                    fi
                    # EXTRA DOTFILES END
                    """
                )
            )

    def _startup(self):
        logger.debug(f"Using {self.startup_config} as startup config file")
        if not self.startup_config.exists():
            logger.debug("{self.startup_config} doesn't exist. Creating it")
            self.startup_config.touch()
        self._scrub_extra_dotfiles_block()
        self._add_extra_dotfiles_block()

    def install_dot(self):
        logger.info("Started Installing dot")
        with DotError.handle_errors("Install failed. Aborting"):
            logger.debug("Create needed directories")
            self._make_dirs()

            logger.debug("Making links")
            self._make_links()

            logger.debug("Copying files")
            self._copy_files()

            logger.debug("Installing tools")
            self._install_tools()

            logger.debug("Adding in extra dotfiles")
            self._update_dotfiles()

            logger.debug("Setting up startup config to include dot")
            self._startup()

        terminal_message(
            f"""
            Dot installation complete!

            Install directory: {self.home}
            Dot root directory: {self.root}
            """,
            subject="Finished installing dot!",
            footer=f"Restart your terminal or source {self.startup_config} to apply changes."
        )
