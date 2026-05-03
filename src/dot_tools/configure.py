import filecmp
import fileinput
import os
import platform
import select
import shutil
import subprocess
import sys
from typing import Annotated

import buzz
import pydantic
import snick
import yaml
from loguru import logger
from pathlib import Path
from typerdrive import terminal_message

from dot_tools.exceptions import DotError
from dot_tools.spinner import spinner, pause_live
from dot_tools.constants import Status


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


class SettingSpecs(pydantic.BaseModel):
    name: str
    check: str
    scripts: ScriptSpecs


class ToolSpecs(pydantic.BaseModel):
    name: str
    check: str
    scripts: ScriptSpecs


class ServiceSpecs(pydantic.BaseModel):
    name: str
    label: str
    executable: str
    args: Annotated[list[str], pydantic.Field(default_factory=lambda: [])]
    config_template: Path | None = None


class InstallManifest(pydantic.BaseModel):
    link_paths: Annotated[list[Path], pydantic.Field(default_factory=lambda: [])]
    copy_paths: Annotated[list[Path | FileSpecs], pydantic.Field(default_factory=lambda: [])]
    dotfile_paths: Annotated[list[Path], pydantic.Field(default_factory=lambda: [])]
    mkdir_paths: Annotated[list[Path], pydantic.Field(default_factory=lambda: [])]
    tools: Annotated[list[ToolSpecs], pydantic.Field(default_factory=lambda: [])]
    settings: Annotated[list[SettingSpecs], pydantic.Field(default_factory=lambda: [])]
    services: Annotated[list[ServiceSpecs], pydantic.Field(default_factory=lambda: [])]


class DotInstaller:
    root: Path
    home: Path
    startup_config: Path
    install_manifest: InstallManifest
    force: bool

    def __init__(self, root: Path, override_home: Path | None = None, force: bool = False):
        self.force = force
        self.root = root.expanduser().resolve().absolute()
        if override_home:
            self.home = override_home.expanduser().resolve().absolute()
        else:
            self.home = Path.home()
        logger.debug(f"Initializing with {self.home} as home, {self.root} as root")

        if platform.system() == "Darwin":
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
        with spinner("Linking files from manifest", context_level="DEBUG"):
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
        with spinner("Making directories from manifest", context_level="DEBUG"):
            for path in self.install_manifest.mkdir_paths:
                logger.debug(f"Processing {path}")

                target_path = self.home / path
                logger.debug(f"Checking/making target directory {target_path}")
                target_path.mkdir(parents=True, exist_ok=True)

    def _git_committed_content(self, path: Path) -> bytes | None:
        """Return the last-committed content of a path relative to self.root, or None if untracked."""
        rel = path.relative_to(self.root)
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            return None
        return result.stdout

    def _copy_files(self):
        with spinner("Copying files from manifest", context_level="DEBUG"):
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
                    if filecmp.cmp(src_path, dst_path, shallow=False):
                        logger.debug(f"Skipping {path} — already installed and identical")
                        continue

                    if self.force:
                        logger.warning(f"File at {dst_path} differs from source, overwriting (--force)")
                    else:
                        # Check if dst matches the last committed version of src.
                        # If it does, the user hasn't touched it — safe to overwrite with the new src.
                        # If it doesn't, the user has local changes — refuse to clobber.
                        committed = self._git_committed_content(src_path)
                        if committed is None:
                            raise DotError(
                                f"{src_path} is not tracked by git. Cannot determine if {dst_path} has local changes. Use --force to overwrite."
                            )
                        dst_content = dst_path.read_bytes()
                        if dst_content != committed:
                            raise DotError(
                                f"{dst_path} has local changes (differs from last committed version in dot repo). "
                                f"Resolve manually or use --force to overwrite."
                            )
                        logger.debug(f"{dst_path} matches last committed version — upstream changed, safe to overwrite")

                logger.debug(f"Copying {path}")
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_path, dst_path)
                if perms is not None:
                    logger.debug(f"Updating permissions for file {dst_path}")
                    dst_path.chmod(perms)

    def _install_tools(self):
        install_env = os.environ.copy()
        install_env["PYTHON_VERSION"] = platform.python_version()
        with spinner("Installing tools", context_level="DEBUG"):
            for tool in self.install_manifest.tools:
                with spinner(f"Installing {tool.name}", context_level="DEBUG"):
                    logger.debug(f"Checking if {tool.name} is installed", status=Status.CHECK)
                    result = subprocess.run(
                        tool.check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                    )
                    if result.returncode == 0:
                        logger.debug(f"{tool.name} is already installed", status=Status.CONFIRM)
                        continue

                    logger.debug(f"{tool.name} is not yet installed", status=Status.MISSING)
                    script: str
                    if tool.scripts.generic:
                        logger.debug("Using generic script for tool installation")
                        script = tool.scripts.generic
                    elif platform.system() == "Linux":
                        logger.debug("Using linux script for tool installation")
                        script = DotError.enforce_defined(tool.scripts.linux, "No linux script defined for tool")
                    elif platform.system() == "Darwin":
                        logger.debug("Using darwin script for tool installation")
                        script = DotError.enforce_defined(tool.scripts.darwin, "No darwin script defined for tool")
                    else:
                        raise DotError(f"Unsupported platform {platform.system()} for tool {tool.name}")

                    logger.debug(f"Running installation script for {tool.name}")
                    output_lines: list[str] = []

                    proc = subprocess.Popen(
                        script,
                        shell=True,
                        executable="/bin/bash",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=install_env,
                        text=True,
                    )
                    assert proc.stdout is not None
                    assert proc.stderr is not None

                    open_streams = [proc.stdout, proc.stderr]
                    while open_streams:
                        readable, _, _ = select.select(open_streams, [], [])
                        for stream in readable:
                            line = stream.readline()
                            if line:
                                stripped = line.rstrip()
                                output_lines.append(stripped)
                                logger.debug(stripped)
                            else:
                                open_streams.remove(stream)
                    proc.wait()

                    if proc.returncode != 0:
                        last_lines = "\n".join(output_lines[-20:])
                        raise DotError(f"Failed to install {tool.name}:\n{last_lines}")
                    logger.debug(f"Completed {tool.name} installation", status=Status.CONFIRM)

    def _apply_settings(self):
        with spinner("Applying settings", context_level="DEBUG"):
            for setting in self.install_manifest.settings:
                with spinner(f"Applying {setting.name}", context_level="DEBUG"):
                    logger.debug(f"Checking if {setting.name} is already applied", status=Status.CHECK)
                    result = subprocess.run(
                        setting.check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                    )
                    if result.returncode == 0:
                        logger.debug(f"{setting.name} is already applied", status=Status.CONFIRM)
                        continue

                    logger.debug(f"{setting.name} is not yet applied", status=Status.MISSING)
                    script: str
                    if setting.scripts.generic:
                        logger.debug("Using generic script for setting")
                        script = setting.scripts.generic
                    elif platform.system() == "Linux":
                        logger.debug("Using linux script for setting")
                        script = DotError.enforce_defined(setting.scripts.linux, "No linux script defined for setting")
                    elif platform.system() == "Darwin":
                        logger.debug("Using darwin script for setting")
                        script = DotError.enforce_defined(setting.scripts.darwin, "No darwin script defined for setting")
                    else:
                        raise DotError(f"Unsupported platform {platform.system()} for setting {setting.name}")

                    logger.debug(f"Running script for {setting.name}")
                    output_lines: list[str] = []

                    proc = subprocess.Popen(
                        script,
                        shell=True,
                        executable="/bin/bash",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    assert proc.stdout is not None
                    assert proc.stderr is not None

                    open_streams = [proc.stdout, proc.stderr]
                    while open_streams:
                        readable, _, _ = select.select(open_streams, [], [])
                        for stream in readable:
                            line = stream.readline()
                            if line:
                                stripped = line.rstrip()
                                output_lines.append(stripped)
                                logger.debug(stripped)
                            else:
                                open_streams.remove(stream)
                    proc.wait()

                    if proc.returncode != 0:
                        last_lines = "\n".join(output_lines[-20:])
                        raise DotError(f"Failed to apply {setting.name}:\n{last_lines}")
                    logger.debug(f"Applied {setting.name}", status=Status.CONFIRM)

    def _update_dotfiles(self):
        with spinner("Adding dotfiles from manifest", context_level="DEBUG"):
            dotfile_list_path = self.home / ".extra_dotfiles"
            if not dotfile_list_path.exists():
                dotfile_list_path.touch()

            with open(dotfile_list_path, "r+") as dotfile_list_file:
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
            if "EXTRA DOTFILES START" in line:
                in_extra_block = True
            if not in_extra_block:
                print(line, end="")
            if "EXTRA DOTFILES END" in line:
                in_extra_block = False

    def _add_extra_dotfiles_block(self):
        logger.debug(f"Adding extra dotfiles to startup in {self.startup_config}")
        extra_dotfiles_path = self.home / ".extra_dotfiles"
        with open(self.startup_config, "a") as startup_file:
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

                    """,
                    should_strip=False,
                )
            )

    def _github_cli_login(self):
        with spinner("Logging into github in CLI", context_level="DEBUG"):
            already_logged_in = (
                subprocess.run(["gh", "auth", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
            )
            if already_logged_in:
                logger.debug("Already logged in to github via cli. Skipping")
                return
            with pause_live():
                result = subprocess.run(
                    ["gh", "auth", "login", "--hostname", "github.com", "--git-protocol", "https", "--web"]
                )
            DotError.require_condition(result.returncode == 0, "Could not log in to github via cli")

    def _add_ssh_keys(self):
        user = os.getlogin()
        ssh_path = self.home / ".ssh"
        key_path = ssh_path / f"{user}.ed25519"
        hostname = platform.node()
        with spinner(f"Adding ssh keys for {user}", context_level="DEBUG"):
            if key_path.exists():
                logger.debug(f"SSH key {key_path} already exists. Skipping")
                return
            result = subprocess.run(f"ssh-keygen -t ed25519 -f {key_path} -N ''", shell=True, stderr=subprocess.PIPE)
            DotError.require_condition(result.returncode == 0, f"Could not create ssh keys: {result.stderr.decode()}")

        with spinner("Adding ssh keys to github", context_level="DEBUG"):
            result = subprocess.run(
                f"gh ssh-key add {key_path} --title {user}@{hostname}", shell=True, stderr=subprocess.PIPE
            )
            DotError.require_condition(result.returncode == 0, f"Could not create ssh keys: {result.stderr.decode()}")

    def _install_services(self):
        def _launchd_plist(service: ServiceSpecs, executable: str, args: list[str]) -> str:
            args_xml = "\n".join(
                f"        <string>{arg}</string>" for arg in args
            )
            return snick.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
                  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>{service.label}</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>{executable}</string>
                {args_xml}
                    </array>
                    <key>RunAtLoad</key>
                    <true/>
                    <key>KeepAlive</key>
                    <true/>
                    <key>StandardOutPath</key>
                    <string>{self.home}/Library/Logs/{service.label}.log</string>
                    <key>StandardErrorPath</key>
                    <string>{self.home}/Library/Logs/{service.label}.error.log</string>
                </dict>
                </plist>
                """
            )

        def _systemd_unit(service: ServiceSpecs, executable: str, args: list[str]) -> str:
            args_str = " ".join(args)
            exec_start = f"{executable} {args_str}".strip()
            return snick.dedent(
                f"""
                [Unit]
                Description={service.name}
                After=network.target

                [Service]
                ExecStart={exec_start}
                Restart=always
                RestartSec=5

                [Install]
                WantedBy=default.target
                """
            )

        with spinner("Installing services", context_level="DEBUG"):
            for service in self.install_manifest.services:
                with spinner(f"Installing service {service.name}", context_level="DEBUG"):
                    executable = shutil.which(service.executable)
                    DotError.require_condition(
                        executable is not None,
                        f"Executable '{service.executable}' not found on PATH for service {service.name}. "
                        "Ensure the tool is installed before registering its service.",
                    )
                    assert executable is not None  # for type narrowing

                    expanded_args = [arg.replace("$HOME", str(self.home)) for arg in service.args]

                    if service.config_template is not None:
                        template_path = self.home / service.config_template
                        DotError.require_condition(
                            template_path.exists(),
                            f"config_template {template_path} not found for service {service.name}",
                        )
                        resolved_path = template_path.parent / (template_path.stem + "-resolved" + template_path.suffix)
                        resolved_content = template_path.read_text().replace("$HOME", str(self.home))
                        if not resolved_path.exists() or resolved_path.read_text() != resolved_content:
                            logger.debug(f"Writing resolved config for {service.name} to {resolved_path}")
                            resolved_path.write_text(resolved_content)
                        expanded_args = [arg.replace("$CONFIG", str(resolved_path)) for arg in expanded_args]

                    if platform.system() == "Darwin":
                        agents_dir = self.home / "Library" / "LaunchAgents"
                        agents_dir.mkdir(parents=True, exist_ok=True)
                        plist_path = agents_dir / f"{service.label}.plist"
                        plist_content = _launchd_plist(service, executable, expanded_args)

                        needs_reload = False
                        if plist_path.exists():
                            if plist_path.read_text() == plist_content:
                                logger.debug(f"Service {service.name} plist is already up to date")
                            else:
                                logger.debug(f"Service {service.name} plist changed; unloading")
                                subprocess.run(
                                    ["launchctl", "unload", str(plist_path)],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                )
                                needs_reload = True
                        else:
                            needs_reload = True

                        if needs_reload:
                            logger.debug(f"Writing plist for service {service.name} to {plist_path}")
                            plist_path.write_text(plist_content)
                            result = subprocess.run(
                                ["launchctl", "load", "-w", str(plist_path)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            )
                            DotError.require_condition(
                                result.returncode == 0,
                                f"Failed to load launchd service {service.name}: {result.stderr.decode()}",
                            )
                            logger.debug(f"Loaded launchd service {service.name}", status=Status.CONFIRM)

                    elif platform.system() == "Linux":
                        unit_dir = self.home / ".config" / "systemd" / "user"
                        unit_dir.mkdir(parents=True, exist_ok=True)
                        unit_path = unit_dir / f"{service.label}.service"
                        unit_content = _systemd_unit(service, executable, expanded_args)

                        needs_reload = False
                        if unit_path.exists():
                            if unit_path.read_text() == unit_content:
                                logger.debug(f"Service {service.name} unit is already up to date")
                            else:
                                logger.debug(f"Service {service.name} unit changed; reloading")
                                needs_reload = True
                        else:
                            needs_reload = True

                        if needs_reload:
                            logger.debug(f"Writing systemd unit for service {service.name} to {unit_path}")
                            unit_path.write_text(unit_content)
                            subprocess.run(
                                ["systemctl", "--user", "daemon-reload"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            )
                            result = subprocess.run(
                                ["systemctl", "--user", "enable", "--now", f"{service.label}.service"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                            )
                            DotError.require_condition(
                                result.returncode == 0,
                                f"Failed to enable systemd service {service.name}: {result.stderr.decode()}",
                            )
                            logger.debug(f"Enabled systemd service {service.name}", status=Status.CONFIRM)
                    else:
                        raise DotError(f"Unsupported platform {platform.system()} for service {service.name}")

    def _startup(self):
        with spinner(f"Using {self.startup_config} as startup config file", context_level="DEBUG"):
            if not self.startup_config.exists():
                logger.debug("{self.startup_config} doesn't exist. Creating it")
                self.startup_config.touch()
            self._scrub_extra_dotfiles_block()
            self._add_extra_dotfiles_block()

    def install_dot(self):
        with spinner("Installing dot", context_level="INFO"):
            with DotError.handle_errors(
                "Install failed. Aborting",
                do_except=lambda dep: print(dep.final_message, file=sys.stderr),
            ):
                self._make_dirs()
                self._make_links()
                self._copy_files()
                self._install_tools()
                self._apply_settings()
                self._update_dotfiles()
                self._github_cli_login()
                self._add_ssh_keys()
                self._startup()
                self._install_services()

        terminal_message(
            f"""
            Dot installation complete!

            Install directory: {self.home}
            Dot root directory: {self.root}
            """,
            subject="Finished installing dot!",
            footer=f"Restart your terminal or source {self.startup_config} to apply changes.",
        )
