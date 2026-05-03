import os
import subprocess
from pathlib import Path

import paramiko
import typer
from loguru import logger

from dot_tools.exceptions import DotError
from dot_tools.spinner import spinner
from dot_tools.constants import Status


def _ssh_config_path() -> Path:
    return Path.home() / ".ssh" / "config"


def _default_key_path() -> Path:
    return Path.home() / ".ssh" / f"{os.getlogin()}.ed25519"


def _run_remote(client: paramiko.SSHClient, command: str) -> tuple[int, str]:
    _, stdout, stderr = client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, stderr.read().decode()


def connect_host(
    host: str,
    alias: str,
    user: str,
    port: int,
    key_path: Path,
    ssh_config_path: Path | None = None,
) -> None:
    pub_key_path = Path(str(key_path) + ".pub")

    DotError.require_condition(
        pub_key_path.exists(),
        f"Public key not found: {pub_key_path}",
    )

    password = typer.prompt(f"{user}@{host}'s password", hide_input=True)

    with spinner(f"Connecting to {host}", context_level="INFO"):
        with spinner("Establishing SSH connection", context_level="DEBUG"):
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(hostname=host, port=port, username=user, password=password)
            except paramiko.AuthenticationException:
                raise DotError(f"Authentication failed for {user}@{host}")
            except Exception as e:
                raise DotError(f"Could not connect to {host}: {e}")
            logger.debug(f"Connected to {host}", status=Status.CONFIRM)

        with spinner("Verifying public key exists", context_level="DEBUG"):
            pub_key = pub_key_path.read_text().strip()
            logger.debug(f"Using public key: {pub_key_path}", status=Status.CONFIRM)

        with spinner("Adding public key to remote authorized_keys", context_level="DEBUG"):
            exit_code, _ = _run_remote(client, f"grep -qF '{pub_key}' ~/.ssh/authorized_keys 2>/dev/null")
            if exit_code == 0:
                logger.debug("Public key already present in authorized_keys", status=Status.CONFIRM)
            else:
                exit_code, stderr = _run_remote(
                    client,
                    f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
                    f"echo '{pub_key}' >> ~/.ssh/authorized_keys && "
                    f"chmod 600 ~/.ssh/authorized_keys",
                )
                DotError.require_condition(
                    exit_code == 0,
                    f"Failed to add key to authorized_keys:\n{stderr}",
                )
                logger.debug("Public key added to authorized_keys", status=Status.CONFIRM)

        client.close()

        with spinner(f"Adding '{alias}' to ~/.ssh/config", context_level="DEBUG"):
            _add_ssh_config_entry(
                alias=alias,
                host=host,
                user=user,
                port=port,
                key_path=key_path,
                ssh_config_path=ssh_config_path,
            )


def _add_ssh_config_entry(
    alias: str,
    host: str,
    user: str,
    port: int,
    key_path: Path,
    ssh_config_path: Path | None = None,
) -> None:
    config_path = ssh_config_path or _ssh_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.touch(exist_ok=True)

    existing = config_path.read_text()

    if f"Host {alias}" in existing:
        logger.debug(f"Entry for '{alias}' already exists in ssh config", status=Status.CONFIRM)
        return

    entry = (
        f"\nHost {alias}\n"
        f"    HostName {host}\n"
        f"    User {user}\n"
        f"    Port {port}\n"
        f"    IdentityFile {key_path}\n"
    )

    with config_path.open("a") as f:
        f.write(entry)

    logger.debug(f"Added '{alias}' to {config_path}", status=Status.CONFIRM)


def generate_keypair(key_path: Path | None = None) -> None:
    resolved_key_path = key_path or _default_key_path()

    with spinner("Generating SSH keypair", context_level="INFO"):
        DotError.require_condition(
            not resolved_key_path.exists(),
            f"Key already exists at {resolved_key_path} — delete it first if you want to regenerate",
        )
        resolved_key_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", str(resolved_key_path), "-N", ""],
            capture_output=True,
            text=True,
        )
        DotError.require_condition(
            result.returncode == 0,
            f"ssh-keygen failed:\n{result.stderr}",
        )
        logger.debug(f"Keypair generated at {resolved_key_path}", status=Status.CONFIRM)
        logger.debug(f"Public key: {resolved_key_path}.pub", status=Status.CONFIRM)
