from pathlib import Path
from unittest.mock import MagicMock, patch, call
import subprocess

import paramiko
import pytest
from typer.testing import CliRunner

from dot_tools.cli.ssh import cli
from dot_tools.exceptions import DotError
from dot_tools.ssh_tools import (
    _add_ssh_config_entry,
    _default_key_path,
    connect_host,
    generate_keypair,
)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def ssh_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".ssh"
    d.mkdir()
    return d


@pytest.fixture
def key_path(ssh_dir: Path) -> Path:
    key = ssh_dir / "test.ed25519"
    key.write_text("private-key-data")
    pub = Path(str(key) + ".pub")
    pub.write_text("ssh-ed25519 AAAAB3Nza test@host")
    return key


class TestDefaultKeyPath:

    def test_default_key_path__uses_login_username(self):
        with patch("dot_tools.ssh_tools.os.getlogin", return_value="someuser"):
            result = _default_key_path()
        assert result.name == "someuser.ed25519"
        assert result.parent == Path.home() / ".ssh"


class TestAddSshConfigEntry:

    def test_add_entry__writes_correct_block(self, tmp_path: Path, key_path: Path):
        config = tmp_path / "config"
        _add_ssh_config_entry("myhost", "192.168.1.1", "bob", 22, key_path, ssh_config_path=config)
        entry = (tmp_path / "config.d" / "myhost").read_text()
        assert "Host myhost" in entry
        assert "HostName 192.168.1.1" in entry
        assert "User bob" in entry
        assert "Port 22" in entry
        assert str(key_path) in entry

    def test_add_entry__skips_if_alias_already_present(self, tmp_path: Path, key_path: Path):
        config = tmp_path / "config"
        entry_path = tmp_path / "config.d" / "myhost"
        entry_path.parent.mkdir(parents=True, exist_ok=True)
        entry_path.write_text("Host myhost\n    HostName 1.2.3.4\n")
        _add_ssh_config_entry("myhost", "192.168.1.1", "bob", 22, key_path, ssh_config_path=config)
        assert entry_path.read_text().count("Host myhost") == 1

    def test_add_entry__creates_config_d_if_missing(self, tmp_path: Path, key_path: Path):
        config = tmp_path / "subdir" / "config"
        _add_ssh_config_entry("newhost", "10.0.0.1", "alice", 2222, key_path, ssh_config_path=config)
        entry = (tmp_path / "subdir" / "config.d" / "newhost").read_text()
        assert "Host newhost" in entry

    def test_add_entry__uses_custom_port(self, tmp_path: Path, key_path: Path):
        config = tmp_path / "config"
        _add_ssh_config_entry("myhost", "10.0.0.1", "alice", 2222, key_path, ssh_config_path=config)
        entry = (tmp_path / "config.d" / "myhost").read_text()
        assert "Port 2222" in entry


class TestGenerateKeypair:

    def test_generate_keypair__calls_ssh_keygen(self, tmp_path: Path):
        key = tmp_path / "test.ed25519"
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("dot_tools.ssh_tools.subprocess.run", return_value=mock_result) as mock_run:
            generate_keypair(key_path=key)
        mock_run.assert_called_once_with(
            ["ssh-keygen", "-t", "ed25519", "-f", str(key), "-N", ""],
            capture_output=True,
            text=True,
        )

    def test_generate_keypair__fails_if_key_already_exists(self, key_path: Path):
        with pytest.raises(DotError, match="Key already exists"):
            generate_keypair(key_path=key_path)

    def test_generate_keypair__raises_on_ssh_keygen_failure(self, tmp_path: Path):
        key = tmp_path / "test.ed25519"
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "some error"
        with patch("dot_tools.ssh_tools.subprocess.run", return_value=mock_result):
            with pytest.raises(DotError, match="ssh-keygen failed"):
                generate_keypair(key_path=key)


class TestConnectHost:

    def test_connect_host__fails_if_pubkey_missing(self, tmp_path: Path):
        key = tmp_path / "missing.ed25519"
        with pytest.raises(DotError, match="Public key not found"):
            connect_host("host", "alias", "user", 22, key)

    def test_connect_host__adds_key_to_authorized_keys(self, tmp_path: Path, key_path: Path):
        config = tmp_path / "config"
        mock_client = MagicMock(spec=paramiko.SSHClient)

        # First call: grep check returns 1 (key not present)
        # Second call: write command returns 0 (success)
        mock_stdout_check = MagicMock()
        mock_stdout_check.channel.recv_exit_status.return_value = 1
        mock_stderr_check = MagicMock()
        mock_stderr_check.read.return_value = b""

        mock_stdout_write = MagicMock()
        mock_stdout_write.channel.recv_exit_status.return_value = 0
        mock_stderr_write = MagicMock()
        mock_stderr_write.read.return_value = b""

        mock_client.exec_command.side_effect = [
            (None, mock_stdout_check, mock_stderr_check),
            (None, mock_stdout_write, mock_stderr_write),
        ]

        with patch("dot_tools.ssh_tools.paramiko.SSHClient", return_value=mock_client):
            with patch("dot_tools.ssh_tools.typer.prompt", return_value="password"):
                connect_host("192.168.1.1", "myalias", "bob", 22, key_path, ssh_config_path=config)

        mock_client.connect.assert_called_once_with(
            hostname="192.168.1.1", port=22, username="bob", password="password"
        )
        assert "Host myalias" in (tmp_path / "config.d" / "myalias").read_text()

    def test_connect_host__skips_write_if_key_already_present(self, tmp_path: Path, key_path: Path):
        config = tmp_path / "config"
        mock_client = MagicMock(spec=paramiko.SSHClient)

        mock_stdout = MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

        with patch("dot_tools.ssh_tools.paramiko.SSHClient", return_value=mock_client):
            with patch("dot_tools.ssh_tools.typer.prompt", return_value="password"):
                connect_host("192.168.1.1", "myalias", "bob", 22, key_path, ssh_config_path=config)

        # exec_command should only be called once (the grep check, not the write)
        assert mock_client.exec_command.call_count == 1

    def test_connect_host__raises_on_auth_failure(self, tmp_path: Path, key_path: Path):
        mock_client = MagicMock(spec=paramiko.SSHClient)
        mock_client.connect.side_effect = paramiko.AuthenticationException()

        with patch("dot_tools.ssh_tools.paramiko.SSHClient", return_value=mock_client):
            with patch("dot_tools.ssh_tools.typer.prompt", return_value="wrongpass"):
                with pytest.raises(DotError, match="Authentication failed"):
                    connect_host("192.168.1.1", "myalias", "bob", 22, key_path)

    def test_connect_host__raises_on_connection_error(self, tmp_path: Path, key_path: Path):
        mock_client = MagicMock(spec=paramiko.SSHClient)
        mock_client.connect.side_effect = Exception("Connection refused")

        with patch("dot_tools.ssh_tools.paramiko.SSHClient", return_value=mock_client):
            with patch("dot_tools.ssh_tools.typer.prompt", return_value="pass"):
                with pytest.raises(DotError, match="Could not connect"):
                    connect_host("192.168.1.1", "myalias", "bob", 22, key_path)


class TestCliSshKeygen:

    def test_keygen__invokes_generate_keypair(self, runner: CliRunner):
        with patch("dot_tools.cli.ssh.generate_keypair") as mock_gen:
            result = runner.invoke(cli, ["keygen"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()

    def test_keygen__fails_if_key_exists(self, runner: CliRunner, key_path: Path):
        with patch("dot_tools.ssh_tools._default_key_path", return_value=key_path):
            result = runner.invoke(cli, ["keygen"])
        assert result.exit_code != 0


class TestCliSshConnect:

    def test_connect__prints_help_with_no_args(self, runner: CliRunner):
        result = runner.invoke(cli, ["connect"])
        assert "Usage" in result.output

    def test_connect__invokes_connect_host(self, runner: CliRunner, key_path: Path):
        with patch("dot_tools.cli.ssh.connect_host") as mock_connect:
            result = runner.invoke(cli, ["connect", "192.168.1.1", "myalias", "--key", str(key_path)])
        assert result.exit_code == 0
        mock_connect.assert_called_once()
