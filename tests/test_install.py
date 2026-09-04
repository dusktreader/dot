import importlib.util
import os
import stat
import subprocess
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest
import yaml


SCRIPT = Path(__file__).parents[1] / "tools" / "configure-sudoers.py"


def load_configurator() -> ModuleType:
    """Load the standalone configurator as an isolated test module."""
    spec = importlib.util.spec_from_file_location("configure_sudoers_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def sudoers_tree(tmp_path: Path):
    """Create a sudoers fixture and patch the configurator's absolute paths."""
    etc = tmp_path / "etc"
    include_dir = etc / "sudoers.d"
    etc.mkdir()
    (etc / "sudoers").write_text("Defaults env_reset\n")
    module = load_configurator()
    real_chown = module.os.chown

    def fixture_chown(path, uid, gid):
        """Attempt ownership changes and suppress only the root-only operation unavailable to this user."""
        try:
            return real_chown(path, uid, gid)
        except PermissionError:
            return None

    with patch.object(module, "SUDOERS_PATH", etc / "sudoers"), patch.object(
        module, "INCLUDE_DIR", include_dir
    ), patch.object(module, "MANAGED_PATH", include_dir / "90-dotfiles"), patch.object(
        module.platform, "system", return_value="Linux"
    ), patch.object(module.os, "geteuid", return_value=os.getuid()), patch.object(
        module, "ROOT_UID", os.getuid()
    ), patch.object(module.pwd, "getpwuid", return_value=type("Passwd", (), {"pw_name": "ada.lovelace"})()
    ), patch.object(module.os, "chown", side_effect=fixture_chown
    ):
        with patch.object(module.subprocess, "run", side_effect=RecordingRunner()):
            yield module, etc / "sudoers", include_dir


class RecordingRunner:
    """Record command arguments and return configured validation results."""

    def __init__(self, returncodes=None):
        self.calls = []
        self.returncodes = iter(returncodes or [])

    def __call__(self, args, **kwargs):
        if args[0] not in {"visudo", "sudo"}:
            raise AssertionError(f"unexpected subprocess: {args}")
        if args[0] == "visudo" and "-f" in args:
            candidate = Path(args[args.index("-f") + 1])
            assert candidate.exists(), candidate
            assert candidate.read_bytes()
        self.calls.append((args, kwargs))
        result = type("Result", (), {})()
        result.returncode = next(self.returncodes, 0)
        result.stderr = b"validation failed"
        result.stdout = b""
        return result


def test_sudoers_contract_has_uv_shebang_and_dependencies():
    content = SCRIPT.read_text()
    assert content.startswith("#!/usr/bin/env -S uv run --script\n")
    assert "# /// script" in content
    assert '# dependencies = ["py-buzz>=8.0", "rich>=14.0"]' in content


def test_sudoers_errors_use_rich_red_error_prefix(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.object(module.console, "print") as print_error:
        assert module.fail("bad configuration") == 1

    prefix, message = print_error.call_args.args
    assert isinstance(prefix, module.Text)
    assert prefix.plain == "Error"
    assert prefix.style == "red"
    assert isinstance(message, module.Text)
    assert message.plain == ": configure-sudoers: bad configuration"


def test_sudoers_configuration_error_uses_buzz(sudoers_tree):
    module, _, _ = sudoers_tree
    assert issubclass(module.ConfigurationError, module.Buzz)

    with pytest.raises(module.ConfigurationError, match="Checked expressions failed"):
        module.require_safe_path(module.SUDOERS_PATH, stat.S_IFDIR, "sudoers file")

    with pytest.raises(module.ConfigurationError, match="does not exist"):
        module.require_safe_path(module.SUDOERS_PATH.with_name("missing"), stat.S_IFREG, "sudoers file")

    assert module.require_safe_path(module.SUDOERS_PATH.with_name("missing"), stat.S_IFREG, "optional file", allow_missing=True) is None


def test_sudoers_standalone_invocation_is_executable_without_configuring():
    result = subprocess.run([str(SCRIPT), "--help"], check=False, capture_output=True, text=True)
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert SCRIPT.stat().st_mode & stat.S_IXUSR


def test_sudoers_check_does_not_modify_fixture(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    original = sudoers.read_bytes()

    assert module.main(["--check"]) != 0
    assert sudoers.read_bytes() == original
    assert not include_dir.exists()


def test_sudoers_check_succeeds_for_active_configuration(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    sudoers.write_text("Defaults env_reset\n#includedir /etc/sudoers.d\n")
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_text("ada.lovelace ALL=(ALL) NOPASSWD: ALL\n")
    os.chmod(managed, 0o440)
    with patch.object(module.subprocess, "run", side_effect=RecordingRunner()):
        assert module.main(["--check"]) == 0


def test_sudoers_linux_creates_include_and_exact_managed_rule(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    runner = RecordingRunner()

    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) == 0

    assert sudoers.read_text() == "Defaults env_reset\n#includedir /etc/sudoers.d\n"
    assert (include_dir / "90-dotfiles").read_text() == "ada.lovelace ALL=(ALL) NOPASSWD: ALL\n"
    assert (include_dir / "90-dotfiles").stat().st_mode & 0o777 == 0o440
    assert all(call[0][0] != "sudo" for call in runner.calls)
    assert [call[0][:3] for call in runner.calls] == [
        ["visudo", "-c"],
        ["visudo", "-c", "-f"],
        ["visudo", "-c", "-f"],
        ["visudo", "-c"],
    ]


def test_sudoers_darwin_accepts_private_etc_include_and_keeps_unrelated_dropins(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    sudoers.write_text("Defaults env_reset\n#includedir /etc/sudoers.d # macOS\n")
    include_dir.mkdir()
    unrelated = include_dir / "10-other"
    unrelated.write_bytes(b"other bytes\r\n")
    with patch.object(module.platform, "system", return_value="Darwin"), patch.object(
        module.subprocess, "run", side_effect=RecordingRunner()
    ):
        assert module.main([]) == 0
    assert sudoers.read_text() == "Defaults env_reset\n#includedir /etc/sudoers.d\n"
    assert unrelated.read_bytes() == b"other bytes\r\n"


def test_sudoers_darwin_creates_include_for_at_includedir(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    sudoers.write_bytes(b"Defaults env_reset\n@includedir /etc/sudoers.d\n")
    with patch.object(module.platform, "system", return_value="Darwin"):
        assert module.main([]) == 0
    assert include_dir.is_dir()
    assert sudoers.read_bytes() == b"Defaults env_reset\n#includedir /etc/sudoers.d\n"
    assert (include_dir / "90-dotfiles").read_bytes() == b"ada.lovelace ALL=(ALL) NOPASSWD: ALL\n"


def test_sudoers_darwin_private_alias_requires_same_resolved_directory(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.object(module.platform, "system", return_value="Darwin"), patch.object(
        module, "INCLUDE_DIR", Path("/private/etc/sudoers.d")
    ):
        assert module.is_active_target_include(b"#includedir /private/etc/sudoers.d # macOS\n")


def test_sudoers_linux_does_not_accept_distinct_private_alias(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.object(module.platform, "system", return_value="Linux"):
        assert not module.is_active_target_include(b"#includedir /private/etc/sudoers.d\n")


def test_sudoers_include_parser_deduplicates_target_and_preserves_unrelated_lines(sudoers_tree):
    module, sudoers, _ = sudoers_tree
    sudoers.write_text(
        "# ordinary #includedir /etc/sudoers.d\n"
        "@includedir /etc/sudoers.d # owned\n"
        "#includedir /private/etc/sudoers.d\n"
        "@includedir /other\n"
        "unrelated\n"
    )
    runner = RecordingRunner()
    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) == 0
    assert sudoers.read_text() == (
        "# ordinary #includedir /etc/sudoers.d\n"
        "#includedir /etc/sudoers.d\n"
        "#includedir /private/etc/sudoers.d\n"
        "@includedir /other\n"
        "unrelated\n"
    )


def test_sudoers_duplicate_active_targets_preserve_every_unrelated_byte(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    sudoers.write_bytes(b"# keep\r\n#includedir /etc/sudoers.d # first\n@includedir /etc/sudoers.d\n# end")
    assert module.main([]) == 0
    assert sudoers.read_bytes() == b"# keep\r\n#includedir /etc/sudoers.d\n# end"
    assert (include_dir / "90-dotfiles").exists()


def test_sudoers_invalid_existing_config_is_rejected_before_writing(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    original = sudoers.read_bytes()
    runner = RecordingRunner([1])
    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) != 0
    assert sudoers.read_bytes() == original
    assert not include_dir.exists()


def test_sudoers_candidate_validation_failure_restores_files(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_text("previous\n")
    os.chmod(managed, 0o440)
    original_main = sudoers.read_bytes()
    runner = RecordingRunner([0, 1])
    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) != 0
    assert sudoers.read_bytes() == original_main
    assert managed.read_text() == "previous\n"


def test_sudoers_final_validation_failure_restores_files(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_text("previous\n")
    os.chmod(managed, 0o440)
    runner = RecordingRunner([0, 0, 0, 1])
    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) != 0
    assert sudoers.read_text() == "Defaults env_reset\n"
    assert managed.read_text() == "previous\n"


def test_sudoers_idempotent_rerun_preserves_inode_and_mtime(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    with patch.object(module.subprocess, "run", side_effect=RecordingRunner()):
        assert module.main([]) == 0
    managed = include_dir / "90-dotfiles"
    paths = [(path, path.stat().st_ino, path.stat().st_mtime_ns) for path in (sudoers, managed)]
    with patch.object(module.subprocess, "run", side_effect=RecordingRunner()):
        assert module.main([]) == 0
    assert [(path.stat().st_ino, path.stat().st_mtime_ns) for path, _, _ in paths] == [
        (inode, mtime) for _, inode, mtime in paths
    ]


def test_sudoers_noninteractive_reexecutes_with_original_arguments(sudoers_tree):
    module, _, _ = sudoers_tree
    result = type("Result", (), {"returncode": 0})()
    with patch.object(module.os, "geteuid", return_value=module.ROOT_UID + 1), patch.object(
        module.subprocess, "run", return_value=result
    ) as run:
        assert module.main(["--check"]) == 0
    assert run.call_args.args[0][:2] == ["sudo", "-n"]
    assert run.call_args.args[0][-1] == "--check"


def test_sudoers_unsafe_paths_are_rejected(sudoers_tree):
    module, _, include_dir = sudoers_tree
    include_dir.symlink_to(Path("/tmp"))
    assert module.main([]) != 0


def test_sudoers_unsafe_managed_drop_in_symlink_is_rejected(sudoers_tree):
    module, _, include_dir = sudoers_tree
    include_dir.mkdir()
    (include_dir / "90-dotfiles").symlink_to(Path("/tmp"))
    assert module.main([]) != 0


def test_sudoers_sudo_failure_is_noninteractive_and_clear(sudoers_tree, capsys):
    module, _, _ = sudoers_tree
    result = type("Result", (), {"returncode": 1})()
    with patch.object(module.os, "geteuid", return_value=module.ROOT_UID + 1), patch.object(
        module.subprocess, "run", return_value=result
    ) as run:
        assert module.main([]) != 0
    assert run.call_args.args[0][:2] == ["sudo", "-n"]
    assert "authentication failed" in capsys.readouterr().err


def test_failed_final_validation_restores_managed_file(sudoers_tree):
    module, _, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_text("old rule\n")
    os.chmod(managed, 0o440)
    runner = RecordingRunner([0, 0, 1])
    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) != 0
    assert managed.read_text() == "old rule\n"


def test_sudoers_unsupported_platform_is_clear(sudoers_tree, capsys):
    module, _, _ = sudoers_tree
    with patch.object(module.platform, "system", return_value="FreeBSD"):
        assert module.main([]) != 0
    assert "Unsupported operating system" in capsys.readouterr().err


def test_sudoers_nonroot_unsupported_platform_does_not_attempt_sudo(sudoers_tree, capsys):
    module, _, _ = sudoers_tree
    with patch.object(module.platform, "system", return_value="FreeBSD"), patch.object(
        module.os, "geteuid", return_value=module.ROOT_UID + 1
    ) as geteuid, patch.object(module.subprocess, "run") as run:
        assert module.main([]) != 0
    geteuid.assert_not_called()
    run.assert_not_called()
    assert "Unsupported operating system" in capsys.readouterr().err


def test_sudoers_missing_visudo_is_clear(sudoers_tree, capsys):
    module, _, _ = sudoers_tree
    with patch.object(module.subprocess, "run", side_effect=FileNotFoundError):
        assert module.main([]) != 0
    assert "visudo" in capsys.readouterr().err


def test_sudoers_visudo_oserror_is_clear(sudoers_tree, capsys):
    module, _, _ = sudoers_tree
    with patch.object(module.subprocess, "run", side_effect=PermissionError("blocked")):
        assert module.main([]) != 0
    assert "could not run visudo" in capsys.readouterr().err


def test_sudoers_missing_sudo_is_clear(sudoers_tree, capsys):
    module, _, _ = sudoers_tree
    with patch.object(module.os, "geteuid", return_value=module.ROOT_UID + 1), patch.object(
        module.subprocess, "run", side_effect=FileNotFoundError
    ):
        assert module.main([]) != 0
    assert "sudo is unavailable" in capsys.readouterr().err


@pytest.mark.parametrize("include", ["@includedir /etc/sudoers.d", "#includedir /etc/sudoers.d # active"])
def test_sudoers_check_accepts_active_include_forms(sudoers_tree, include):
    module, sudoers, include_dir = sudoers_tree
    sudoers.write_text(f"Defaults env_reset\n{include}\n")
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_text("ada.lovelace ALL=(ALL) NOPASSWD: ALL\n")
    os.chmod(managed, 0o440)
    assert module.main(["--check"]) == 0


def test_sudoers_identity_uses_sudo_uid_not_user(sudoers_tree):
    module, _, _ = sudoers_tree
    passwd = type("Passwd", (), {"pw_name": "original.user"})()
    with patch.dict(module.os.environ, {"SUDO_UID": "1234", "SUDO_USER": "wrong", "USER": "wrong"}), patch.object(
        module.pwd, "getpwuid", return_value=passwd
    ) as getpwuid:
        assert module.desired_rule() == b"original.user ALL=(ALL) NOPASSWD: ALL\n"
    getpwuid.assert_called_once_with(1234)


def test_sudoers_identity_falls_back_to_sudo_user(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.dict(module.os.environ, {"SUDO_UID": "", "SUDO_USER": "grace", "USER": "wrong"}), patch.object(
        module.pwd, "getpwnam", return_value=type("Passwd", (), {"pw_name": "grace.hopper"})()
    ) as getpwnam:
        assert module.desired_rule() == b"grace.hopper ALL=(ALL) NOPASSWD: ALL\n"
    getpwnam.assert_called_once_with("grace")


def test_sudoers_identity_falls_back_to_current_uid(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.dict(module.os.environ, {}, clear=True), patch.object(
        module.pwd, "getpwuid", return_value=type("Passwd", (), {"pw_name": "current.user"})()
    ) as getpwuid:
        assert module.desired_rule() == b"current.user ALL=(ALL) NOPASSWD: ALL\n"
    getpwuid.assert_called_once_with(os.getuid())


def test_sudoers_complete_candidate_contains_staged_rule(sudoers_tree):
    module, _, _ = sudoers_tree
    inspected: list[tuple[str, bytes]] = []

    class CandidateRunner(RecordingRunner):
        def __call__(self, args, **kwargs):
            if "-f" in args:
                candidate = Path(args[-1])
                inspected.append((str(candidate), candidate.read_bytes()))
            return super().__call__(args, **kwargs)

    with patch.object(module.subprocess, "run", side_effect=CandidateRunner()):
        assert module.main([]) == 0
    assert len(inspected) == 2
    assert any(content.startswith(b"ada.lovelace ALL=(ALL) NOPASSWD: ALL\n") for _, content in inspected)
    assert any(b".sudoers-candidate-" in content for _, content in inspected)


def test_sudoers_final_failure_restores_managed_metadata_and_cleans_candidates(sudoers_tree):
    module, _, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_bytes(b"old rule\n")
    os.chmod(managed, 0o640)
    original_stat = managed.stat()
    with patch.object(module.subprocess, "run", side_effect=RecordingRunner([0, 0, 0, 1])):
        assert module.main([]) != 0
    restored = managed.stat()
    assert managed.read_bytes() == b"old rule\n"
    assert stat.S_IMODE(restored.st_mode) == stat.S_IMODE(original_stat.st_mode)
    assert restored.st_uid == original_stat.st_uid
    assert restored.st_gid == original_stat.st_gid
    assert list(include_dir.glob(".90-dotfiles.*")) == []
    assert list(include_dir.parent.glob(".sudoers-candidate-*")) == []


def test_sudoers_candidate_filesystem_failure_is_clear_and_clean(sudoers_tree, capsys):
    module, _, include_dir = sudoers_tree
    include_dir.mkdir()
    with patch.object(module.tempfile, "mkstemp", side_effect=PermissionError("denied")):
        assert module.main([]) != 0
    assert "temporary file" in capsys.readouterr().err
    assert list(include_dir.glob(".90-dotfiles.*")) == []


def test_sudoers_candidate_write_failure_is_clear_and_clean(sudoers_tree, capsys):
    module, _, include_dir = sudoers_tree
    include_dir.mkdir()
    with patch.object(module, "write_file", side_effect=PermissionError("denied")):
        assert module.main([]) != 0
    error = capsys.readouterr().err
    assert "candidate" in error
    assert list(include_dir.glob(".90-dotfiles.*")) == []
    assert list(include_dir.parent.glob(".sudoers-candidate-*")) == []


def test_sudoers_write_temp_cleanup_failure_preserves_original_error(sudoers_tree, tmp_path):
    module, _, _ = sudoers_tree
    candidate = tmp_path / "candidate"
    descriptor = os.open(candidate, os.O_CREAT | os.O_WRONLY, 0o600)
    with patch.object(module.tempfile, "mkstemp", return_value=(descriptor, str(candidate))), patch.object(
        module.os, "chmod", side_effect=PermissionError("metadata blocked")
    ), patch.object(module.Path, "unlink", side_effect=PermissionError("cleanup blocked")):
        with pytest.raises(module.ConfigurationError, match="metadata blocked"):
            module.write_temp(tmp_path, b"candidate\n", 0o440)
    candidate.unlink()


def test_sudoers_created_include_is_removed_after_transaction_failure(sudoers_tree):
    module, _, include_dir = sudoers_tree
    runner = RecordingRunner([0, 1])
    with patch.object(module.subprocess, "run", side_effect=runner):
        assert module.main([]) != 0
    assert not include_dir.exists()


def test_sudoers_read_failure_is_clear(sudoers_tree, capsys):
    module, sudoers, _ = sudoers_tree
    module.INCLUDE_DIR.mkdir()
    with patch.object(module.Path, "read_bytes", side_effect=PermissionError("blocked")):
        assert module.main(["--check"]) != 0
    assert "could not read sudoers file" in capsys.readouterr().err


def test_sudoers_preserves_existing_include_directory_mode(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir(mode=0o700)
    before = include_dir.stat().st_mode
    with patch.object(module.subprocess, "run", side_effect=RecordingRunner()):
        assert module.main([]) == 0
    assert stat.S_IMODE(include_dir.stat().st_mode) == stat.S_IMODE(before)
    assert sudoers.read_bytes().endswith(b"#includedir /etc/sudoers.d\n")


def test_sudoers_rejects_unsafe_main_file_and_managed_mode(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    target = sudoers.with_name("real-sudoers")
    target.write_bytes(sudoers.read_bytes())
    sudoers.unlink()
    sudoers.symlink_to(target)
    assert module.main([]) != 0

    sudoers.unlink()
    sudoers.write_bytes(b"Defaults env_reset\n")
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_bytes(b"old\n")
    os.chmod(managed, 0o660)
    assert module.main([]) != 0


def test_sudoers_rejects_real_unsafe_modes_for_main_include_and_managed(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    os.chmod(sudoers, 0o664)
    assert module.main([]) != 0

    os.chmod(sudoers, 0o600)
    include_dir.mkdir()
    os.chmod(include_dir, 0o777)
    assert module.main([]) != 0

    os.chmod(include_dir, 0o755)
    managed = include_dir / "90-dotfiles"
    managed.write_bytes(b"old\n")
    os.chmod(managed, 0o660)
    assert module.main([]) != 0


def test_sudoers_rejects_actual_nonroot_owned_fixture_via_root_uid_seam(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.object(module, "ROOT_UID", os.getuid() + 1):
        with patch.object(module.os, "geteuid", return_value=module.ROOT_UID):
            assert module.main([]) != 0


def test_sudoers_rejects_non_root_fixture_owner(sudoers_tree):
    module, _, _ = sudoers_tree
    with patch.object(module, "require_safe_path", side_effect=module.ConfigurationError("must be root-owned")):
        assert module.main([]) != 0


def test_sudoers_success_replaces_changed_files_atomically(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    original_inode = sudoers.stat().st_ino
    with patch.object(module.subprocess, "run", side_effect=RecordingRunner()):
        assert module.main([]) == 0
    assert sudoers.stat().st_ino != original_inode


def test_sudoers_manifest_contains_passwordless_sudo_setting():
    manifest = yaml.safe_load((SCRIPT.parents[1] / "etc" / "install.yaml").read_text())
    settings = [setting for setting in manifest["settings"] if setting["name"] == "passwordless sudo"]
    assert len(settings) == 1
    assert settings[0]["check"] == '"$DOT_ROOT/tools/configure-sudoers.py" --check'
    assert settings[0]["scripts"]["generic"] == '"$DOT_ROOT/tools/configure-sudoers.py"'


def test_capslock_manifest_contains_linux_setting_and_darwin_service():
    manifest = yaml.safe_load((SCRIPT.parents[1] / "etc" / "install.yaml").read_text())
    settings = [setting for setting in manifest["settings"] if setting["name"] == "capslock-to-escape"]
    assert len(settings) == 1

    capslock = settings[0]
    assert capslock["platform"] == "Linux"
    assert capslock["check"] == "grep -q 'caps:escape' /etc/default/keyboard"
    assert capslock["scripts"]["linux"].startswith("sudo sed -i")
    assert capslock["scripts"].get("darwin") is None

    services = [service for service in manifest["services"] if service["name"] == "capslock-to-escape"]
    assert services == [
        {
            "name": "capslock-to-escape",
            "label": "com.dusktreader.capslock-to-escape",
            "executable": "/usr/bin/hidutil",
            "args": [
                "property",
                "--set",
                '{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x700000039,"HIDKeyboardModifierMappingDst":0x700000029}]}',
            ],
            "platform": "Darwin",
            "keep_alive": False,
        }
    ]


def test_sudoers_install_script_has_no_username_derived_write():
    install = (SCRIPT.parents[1] / "install.sh").read_text()
    assert "sudo tee /etc/sudoers.d/$USER" not in install
    assert "Making passwordless sudo" not in install


@pytest.mark.parametrize("target", ["main", "include", "managed"])
def test_sudoers_rejects_nonregular_required_paths(sudoers_tree, target):
    module, sudoers, include_dir = sudoers_tree
    if target == "main":
        sudoers.unlink()
        os.mkfifo(sudoers)
    else:
        include_dir.mkdir()
        if target == "include":
            include_dir.rmdir()
            os.mkfifo(include_dir)
        else:
            os.mkfifo(include_dir / "90-dotfiles")
    assert module.main([]) != 0


def test_sudoers_replacement_failure_cleans_candidates_and_preserves_files(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_bytes(b"old\n")
    os.chmod(managed, 0o440)
    original_main = sudoers.read_bytes()
    real_replace = module.os.replace

    def fail_main(source, destination):
        if destination == sudoers:
            raise OSError("main replacement blocked")
        return real_replace(source, destination)

    with patch.object(module.os, "replace", side_effect=fail_main), patch.object(
        module.subprocess, "run", side_effect=RecordingRunner()
    ):
        assert module.main([]) != 0
    assert sudoers.read_bytes() == original_main
    assert managed.read_bytes() == b"old\n"
    assert list(sudoers.parent.glob(".sudoers-*")) == []
    assert list(include_dir.glob(".90-dotfiles.*")) == []


def test_sudoers_managed_replacement_failure_restores_main_and_cleans_candidates(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_bytes(b"old\n")
    os.chmod(managed, 0o440)
    original_main = sudoers.read_bytes()
    real_replace = module.os.replace
    calls = []

    def fail_managed(source, destination):
        calls.append((Path(source), Path(destination)))
        if destination == module.MANAGED_PATH and len(calls) == 2:
            raise OSError("managed replacement blocked")
        return real_replace(source, destination)

    with patch.object(module.os, "replace", side_effect=fail_managed), patch.object(
        module.subprocess, "run", side_effect=RecordingRunner()
    ):
        assert module.main([]) != 0
    assert sudoers.read_bytes() == original_main
    assert managed.read_bytes() == b"old\n"
    assert list(sudoers.parent.glob(".sudoers-*")) == []
    assert list(include_dir.glob(".90-dotfiles.*")) == []


def test_sudoers_restoration_failure_reports_primary_error_and_cleans_candidates(sudoers_tree, capsys):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir()
    managed = include_dir / "90-dotfiles"
    managed.write_bytes(b"old\n")
    os.chmod(managed, 0o440)
    real_replace = module.os.replace
    calls = []

    def fail_restore(source, destination):
        calls.append((Path(source), Path(destination)))
        if destination == sudoers and len(calls) == 3:
            raise OSError("main restoration blocked")
        return real_replace(source, destination)

    with patch.object(module.os, "replace", side_effect=fail_restore), patch.object(
        module.subprocess, "run", side_effect=RecordingRunner([0, 0, 0, 1])
    ):
        assert module.main([]) != 0
    error = capsys.readouterr().err
    assert "configuration failed" in error
    assert "validation failed" in error
    assert "main sudoers" in error
    assert list(sudoers.parent.glob(".sudoers-*")) == []
    assert list(include_dir.glob(".90-dotfiles.*")) == []


def test_sudoers_atomic_replacement_arguments_and_main_metadata(sudoers_tree):
    module, sudoers, include_dir = sudoers_tree
    include_dir.mkdir()
    before = sudoers.stat()
    calls = []
    real_replace = module.os.replace

    def record_replace(source, destination):
        calls.append((Path(source), Path(destination)))
        return real_replace(source, destination)

    with patch.object(module.os, "replace", side_effect=record_replace), patch.object(
        module.subprocess, "run", side_effect=RecordingRunner()
    ):
        assert module.main([]) == 0
    assert calls[0][0].parent == sudoers.parent
    assert calls[0][1] == sudoers
    assert calls[1][0].parent == include_dir
    assert calls[1][1] == include_dir / "90-dotfiles"
    after = sudoers.stat()
    assert sudoers.read_bytes() == b"Defaults env_reset\n#includedir /etc/sudoers.d\n"
    assert stat.S_IMODE(after.st_mode) == stat.S_IMODE(before.st_mode)
    assert after.st_uid == before.st_uid
    assert after.st_gid == before.st_gid


@pytest.mark.parametrize("operation", ["chown", "chmod", "revalidate"])
def test_sudoers_include_creation_failure_removes_directory(sudoers_tree, operation):
    module, _, include_dir = sudoers_tree
    if operation == "chown":
        failure = patch.object(module.os, "chown", side_effect=PermissionError("chown blocked"))
    elif operation == "chmod":
        failure = patch.object(module.os, "chmod", side_effect=PermissionError("chmod blocked"))
    else:
        failure = patch.object(
            module, "require_safe_path", side_effect=[None, module.ConfigurationError("revalidation blocked")]
        )
    with failure, pytest.raises(module.ConfigurationError):
        module.ensure_include_dir()
    assert not include_dir.exists()


def test_sudoers_post_creation_failure_removes_empty_include_directory(sudoers_tree):
    module, _, include_dir = sudoers_tree
    with patch.object(module, "desired_rule", side_effect=module.ConfigurationError("identity blocked")):
        assert module.main([]) != 0
    assert not include_dir.exists()


def test_sudoers_cleanup_failure_is_reported_without_masking_primary_error(sudoers_tree, capsys):
    module, _, include_dir = sudoers_tree
    include_dir.mkdir()
    with patch.object(module, "write_file", side_effect=PermissionError("candidate blocked")), patch.object(
        module, "remove_tree_best_effort", return_value="candidate directory: cleanup blocked"
    ):
        assert module.main([]) != 0
    error = capsys.readouterr().err
    assert "candidate" in error
    assert "could not clean up" in error
