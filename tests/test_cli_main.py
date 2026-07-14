import json
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from dot_tools.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestMain:

    def test_main__prints_help_when_no_subcommand(self, runner: CliRunner):
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "dot-tools" in result.output

    def test_main__prints_version_with_flag(self, runner: CliRunner):
        with patch("dot_tools.cli.main.get_version", return_value="9.9.9"):
            result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "9.9.9" in result.output


class TestKv:

    def test_kv__produces_json_from_key_value_pairs(self, runner: CliRunner):
        result = runner.invoke(cli, ["kv", "foo->bar", "baz->qux"])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert data == {"foo": "bar", "baz": "qux"}

    def test_kv__wraps_output_in_quotes_when_flag_set(self, runner: CliRunner):
        result = runner.invoke(cli, ["kv", "k->v", "--include-quotes"])
        assert result.exit_code == 0
        output = result.output.strip()
        assert output.startswith("'")
        assert output.endswith("'")
        inner = json.loads(output[1:-1])
        assert inner == {"k": "v"}

    def test_kv__respects_custom_separator(self, runner: CliRunner):
        result = runner.invoke(cli, ["kv", "k:v", "--sep", ":"])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert data == {"k": "v"}


class TestLineLength:

    def test_line_length__prints_detected_length(self, runner: CliRunner):
        with patch("dot_tools.cli.main.get_config_line_length", return_value=120):
            result = runner.invoke(cli, ["line-length"])
        assert result.exit_code == 0
        assert "120" in result.output


class TestUrlencode:

    def test_urlencode__encodes_provided_text(self, runner: CliRunner):
        with patch("dot_tools.cli.main.pyperclip.copy"):
            result = runner.invoke(cli, ["urlencode", "hello world"])
        assert result.exit_code == 0
        assert "hello%20world" in result.output

    def test_urlencode__reads_from_stdin_when_no_argument(self, runner: CliRunner):
        with patch("dot_tools.cli.main.pyperclip.copy"):
            result = runner.invoke(cli, ["urlencode"], input="hello world\n")
        assert result.exit_code == 0
        assert "hello%20world" in result.output

    def test_urlencode__copies_result_to_clipboard(self, runner: CliRunner):
        with patch("dot_tools.cli.main.pyperclip.copy") as mock_copy:
            runner.invoke(cli, ["urlencode", "hello world"])
        mock_copy.assert_called_once_with("hello%20world")


class TestConfigure:

    def test_configure__invokes_installer(self, runner: CliRunner, tmp_path):
        mock_installer = MagicMock()
        with patch("dot_tools.cli.main.DotInstaller", return_value=mock_installer):
            runner.invoke(cli, ["configure", "--root", str(tmp_path), "--override-home", str(tmp_path)])
        mock_installer.install_dot.assert_called_once()

    def test_configure_wdt_absent_silent(self, runner: CliRunner, tmp_path):
        """dt configure exits zero and silently continues when wdt is not on PATH."""
        mock_installer = MagicMock()
        with patch("dot_tools.cli.main.DotInstaller", return_value=mock_installer), \
             patch("dot_tools.cli.main.shutil.which", return_value=None):
            result = runner.invoke(cli, ["configure", "--root", str(tmp_path), "--override-home", str(tmp_path)])
        assert result.exit_code == 0
        mock_installer.install_dot.assert_called_once()

    def test_configure_wdt_present_success(self, runner: CliRunner, tmp_path):
        """dt configure succeeds when wdt is found on PATH and exits zero."""
        mock_installer = MagicMock()
        mock_run = MagicMock()
        mock_run.return_value = MagicMock(returncode=0)
        with patch("dot_tools.cli.main.DotInstaller", return_value=mock_installer), \
             patch("dot_tools.cli.main.shutil.which", return_value="/usr/local/bin/wdt"), \
             patch("dot_tools.cli.main.subprocess.run", side_effect=mock_run):
            result = runner.invoke(cli, ["configure", "--root", str(tmp_path), "--override-home", str(tmp_path)])
        assert result.exit_code == 0
        mock_installer.install_dot.assert_called_once()
        mock_run.assert_called_once()

    def test_configure_wdt_present_failure(self, runner: CliRunner, tmp_path):
        """dt configure exits nonzero when wdt subprocess fails."""
        mock_installer = MagicMock()
        mock_run = MagicMock()
        mock_run.return_value = MagicMock(returncode=1)
        with patch("dot_tools.cli.main.DotInstaller", return_value=mock_installer), \
             patch("dot_tools.cli.main.shutil.which", return_value="/usr/local/bin/wdt"), \
             patch("dot_tools.cli.main.subprocess.run", side_effect=mock_run):
            result = runner.invoke(cli, ["configure", "--root", str(tmp_path), "--override-home", str(tmp_path)])
        assert result.exit_code == 1

    def test_configure_wdt_receives_override_home(self, runner: CliRunner, tmp_path):
        """dt configure forwards --override-home to wdt subprocess."""
        mock_installer = MagicMock()
        mock_run = MagicMock()
        mock_run.return_value = MagicMock(returncode=0)
        home_path = str(tmp_path / "work_home")
        with patch("dot_tools.cli.main.DotInstaller", return_value=mock_installer), \
             patch("dot_tools.cli.main.shutil.which", return_value="/usr/local/bin/wdt"), \
             patch("dot_tools.cli.main.subprocess.run", side_effect=mock_run):
            runner.invoke(cli, [
                "configure",
                "--root", str(tmp_path),
                "--override-home", home_path,
            ])
            # Verify subprocess was called with --override-home argument
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert "--override-home" in call_args
            assert home_path in call_args

    def test_configure_wdt_receives_force_flag(self, runner: CliRunner, tmp_path):
        """dt configure forwards --force to wdt subprocess."""
        mock_installer = MagicMock()
        mock_run = MagicMock()
        mock_run.return_value = MagicMock(returncode=0)
        with patch("dot_tools.cli.main.DotInstaller", return_value=mock_installer), \
             patch("dot_tools.cli.main.shutil.which", return_value="/usr/local/bin/wdt"), \
             patch("dot_tools.cli.main.subprocess.run", side_effect=mock_run):
            runner.invoke(cli, [
                "configure",
                "--root", str(tmp_path),
                "--force",
            ])
            # Verify subprocess was called with --force argument
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert "--force" in call_args
