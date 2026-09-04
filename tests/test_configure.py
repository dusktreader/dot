import json
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from dot_tools.configure import (
    parse_octal,
    FileSpecs,
    ScriptSpecs,
    SettingSpecs,
    ToolSpecs,
    ServiceSpecs,
    InstallManifest,
    DotInstaller,
    resolve_tool_order,
)
from dot_tools.exceptions import DotError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_MANIFEST = {
    "link_paths": [],
    "copy_paths": [],
    "dotfile_paths": [],
    "mkdir_paths": [],
    "tools": [],
    "services": [],
}


class FakeBinaryStream:
    def __init__(self, *chunks: bytes):
        self.chunks = list(chunks) + [b""]
        self.read_sizes: list[int] = []

    def read(self, size: int) -> bytes:
        self.read_sizes.append(size)
        return self.chunks.pop(0)


def make_dot_root(tmp_path: Path, manifest: dict | None = None) -> Path:
    """Create a minimal dot root with a valid etc/install.yaml."""
    root = tmp_path / "dot_root"
    etc = root / "etc"
    etc.mkdir(parents=True)
    (etc / "install.yaml").write_text(yaml.dump(manifest or MINIMAL_MANIFEST))
    return root


def make_installer(tmp_path: Path, manifest: dict | None = None, force: bool = False) -> DotInstaller:
    root = make_dot_root(tmp_path, manifest)
    home = tmp_path / "home"
    home.mkdir()
    with patch("dot_tools.configure.spinner"):
        return DotInstaller(root=root, override_home=home, force=force)


# ---------------------------------------------------------------------------
# parse_octal
# ---------------------------------------------------------------------------

class TestParseOctal:

    def test_parse_octal__converts_octal_string(self):
        assert parse_octal("0o600") == 0o600
        assert parse_octal("0o755") == 0o755
        assert parse_octal("0o644") == 0o644

    def test_parse_octal__works_without_prefix(self):
        assert parse_octal("600") == 0o600

    def test_parse_octal__raises_on_invalid_value(self):
        with pytest.raises(ValueError):
            parse_octal("not_octal")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TestFileSpecs:

    def test_file_specs__parses_path_and_perms(self):
        spec = FileSpecs(path=Path(".ssh/config"), perms="0o600")
        assert spec.path == Path(".ssh/config")
        assert spec.perms == 0o600

    def test_file_specs__rejects_invalid_perms(self):
        with pytest.raises(Exception):
            FileSpecs(path=Path(".ssh/config"), perms="bad")


class TestScriptSpecs:

    def test_script_specs__all_optional(self):
        spec = ScriptSpecs()
        assert spec.generic is None
        assert spec.linux is None
        assert spec.darwin is None

    def test_script_specs__stores_scripts(self):
        spec = ScriptSpecs(generic="echo hi", linux="apt install foo", darwin="brew install foo")
        assert spec.generic == "echo hi"
        assert spec.linux == "apt install foo"
        assert spec.darwin == "brew install foo"


class TestToolSpecs:

    def test_tool_specs__stores_fields(self):
        spec = ToolSpecs(name="ripgrep", check="rg --version", scripts=ScriptSpecs(generic="cargo install rg"))
        assert spec.name == "ripgrep"
        assert spec.check == "rg --version"
        assert spec.scripts.generic == "cargo install rg"

    def test_tool_specs__depends_on_defaults_to_empty_list(self):
        spec = ToolSpecs(name="ripgrep", check="rg --version", scripts=ScriptSpecs(generic="cargo install rg"))
        assert spec.depends_on == []

    def test_tool_specs__depends_on_loads_from_dict(self):
        spec = ToolSpecs(
            name="usql",
            check="usql --version",
            scripts=ScriptSpecs(generic="go install github.com/xo/usql@latest"),
            depends_on=["asdf-go"]
        )
        assert spec.depends_on == ["asdf-go"]

    def test_tool_specs__depends_on_loads_multiple_dependencies(self):
        spec = ToolSpecs(
            name="foo",
            check="foo --version",
            scripts=ScriptSpecs(generic="install-foo"),
            depends_on=["bar", "baz"]
        )
        assert spec.depends_on == ["bar", "baz"]


class TestServiceSpecs:

    def test_service_specs__stores_fields(self):
        spec = ServiceSpecs(name="my-svc", label="com.example.my-svc", executable="my-svc")
        assert spec.name == "my-svc"
        assert spec.args == []
        assert spec.config_template is None

    def test_service_specs__stores_args_and_template(self):
        spec = ServiceSpecs(
            name="my-svc",
            label="com.example.my-svc",
            executable="my-svc",
            args=["--port", "8080"],
            config_template=Path(".config/my-svc/config.yaml"),
        )
        assert spec.args == ["--port", "8080"]
        assert spec.config_template == Path(".config/my-svc/config.yaml")

    def test_service_specs__stores_platform(self):
        spec = ServiceSpecs(name="my-svc", label="com.example.my-svc", executable="my-svc", platform="Darwin")
        assert spec.platform == "Darwin"
        assert spec.keep_alive is True

    def test_setting_specs__stores_platform(self):
        spec = SettingSpecs(
            name="linux-setting",
            check="check-setting",
            scripts=ScriptSpecs(linux="apply-setting"),
            platform="Linux",
        )
        assert spec.platform == "Linux"


class TestDotInstallerInstallServices:

    def test_install_services__skips_service_for_other_platform(self, tmp_path: Path):
        manifest = {
            **MINIMAL_MANIFEST,
            "services": [
                {
                    "name": "mac-only",
                    "label": "com.example.mac-only",
                    "executable": "mac-only",
                    "platform": "Darwin",
                }
            ],
        }
        installer = make_installer(tmp_path, manifest)

        with (
            patch("dot_tools.configure.platform.system", return_value="Linux"),
            patch("dot_tools.configure.shutil.which") as which,
            patch("dot_tools.configure.subprocess.run") as run,
            patch("dot_tools.configure.spinner"),
        ):
            installer._install_services()

        assert not (installer.home / "Library" / "LaunchAgents").exists()
        which.assert_not_called()
        run.assert_not_called()

    def test_install_services__installs_non_keep_alive_darwin_service(self, tmp_path: Path):
        manifest = {
            **MINIMAL_MANIFEST,
            "services": [
                {
                    "name": "one-shot",
                    "label": "com.example.one-shot",
                    "executable": "one-shot",
                    "platform": "Darwin",
                    "keep_alive": False,
                }
            ],
        }
        installer = make_installer(tmp_path, manifest)
        launchctl_result = MagicMock(returncode=0, stderr=b"")

        with (
            patch("dot_tools.configure.platform.system", return_value="Darwin"),
            patch("dot_tools.configure.shutil.which", return_value="/usr/local/bin/one-shot"),
            patch("dot_tools.configure.subprocess.run", return_value=launchctl_result) as run,
            patch("dot_tools.configure.spinner"),
        ):
            installer._install_services()

        plist_path = installer.home / "Library" / "LaunchAgents" / "com.example.one-shot.plist"
        plist_content = plist_path.read_text()
        assert plist_path.exists()
        assert "<key>KeepAlive</key>" not in plist_content
        assert ["launchctl", "load", "-w", str(plist_path)] in [call.args[0] for call in run.call_args_list]


class TestInstallManifest:

    def test_install_manifest__all_fields_default_to_empty(self):
        manifest = InstallManifest()
        assert manifest.link_paths == []
        assert manifest.copy_paths == []
        assert manifest.dotfile_paths == []
        assert manifest.mkdir_paths == []
        assert manifest.tools == []
        assert manifest.services == []

    def test_install_manifest__loads_from_yaml(self):
        data = {
            "link_paths": [".gitconfig", ".zshrc"],
            "mkdir_paths": [".vim/backup"],
            "copy_paths": [{"path": ".ssh/config", "perms": "0o600"}],
            "dotfile_paths": [".dotrc"],
            "tools": [],
            "services": [],
        }
        manifest = InstallManifest(**data)
        assert Path(".gitconfig") in manifest.link_paths
        assert manifest.mkdir_paths == [Path(".vim/backup")]
        assert isinstance(manifest.copy_paths[0], FileSpecs)
        assert manifest.copy_paths[0].perms == 0o600

    def test_install_manifest__loads_real_manifest_with_dependencies(self, tmp_path: Path):
        # Test loading the real etc/install.yaml file
        import os
        dot_root = Path(os.getcwd())
        manifest_path = dot_root / "etc" / "install.yaml"
        
        if manifest_path.exists():
            manifest_data = yaml.safe_load(manifest_path.read_text())
            manifest = InstallManifest(**manifest_data)
            
            # Verify we have the three tools with expected dependencies
            tools_by_name = {tool.name: tool for tool in manifest.tools}
            
            assert "asdf" in tools_by_name
            assert "asdf-go" in tools_by_name
            assert "usql" in tools_by_name
            
            # Verify the dependency chain
            assert tools_by_name["asdf"].depends_on == []
            assert tools_by_name["asdf-go"].depends_on == ["asdf"]
            assert tools_by_name["usql"].depends_on == ["asdf-go"]
            
            # Verify the chain can be resolved
            resolved = resolve_tool_order(manifest.tools)
            resolved_names = [t.name for t in resolved]
            
            # asdf must come before asdf-go, asdf-go must come before usql
            asdf_idx = resolved_names.index("asdf")
            asdf_go_idx = resolved_names.index("asdf-go")
            usql_idx = resolved_names.index("usql")
            
            assert asdf_idx < asdf_go_idx
            assert asdf_go_idx < usql_idx


# ---------------------------------------------------------------------------
# resolve_tool_order
# ---------------------------------------------------------------------------

class TestResolveToolOrder:

    def test_resolve_tool_order__empty_list_returns_empty(self):
        result = resolve_tool_order([])
        assert result == []

    def test_resolve_tool_order__no_dependencies_returns_valid_order(self):
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a")),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b")),
            ToolSpecs(name="c", check="check-c", scripts=ScriptSpecs(generic="install-c")),
        ]
        result = resolve_tool_order(tools)
        assert len(result) == 3
        assert {t.name for t in result} == {"a", "b", "c"}

    def test_resolve_tool_order__simple_chain_abc(self):
        # B depends on A, C depends on B
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a")),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b"), depends_on=["a"]),
            ToolSpecs(name="c", check="check-c", scripts=ScriptSpecs(generic="install-c"), depends_on=["b"]),
        ]
        result = resolve_tool_order(tools)
        names = [t.name for t in result]
        assert names == ["a", "b", "c"]

    def test_resolve_tool_order__chain_with_different_input_order(self):
        # C depends on B, B depends on A, but input order is C, B, A
        tools = [
            ToolSpecs(name="c", check="check-c", scripts=ScriptSpecs(generic="install-c"), depends_on=["b"]),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b"), depends_on=["a"]),
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a")),
        ]
        result = resolve_tool_order(tools)
        names = [t.name for t in result]
        # A must come before B, B must come before C
        assert names.index("a") < names.index("b")
        assert names.index("b") < names.index("c")

    def test_resolve_tool_order__diamond_dependency(self):
        # D depends on B and C, B depends on A, C depends on A
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a")),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b"), depends_on=["a"]),
            ToolSpecs(name="c", check="check-c", scripts=ScriptSpecs(generic="install-c"), depends_on=["a"]),
            ToolSpecs(name="d", check="check-d", scripts=ScriptSpecs(generic="install-d"), depends_on=["b", "c"]),
        ]
        result = resolve_tool_order(tools)
        names = [t.name for t in result]
        # A must come first
        assert names.index("a") < names.index("b")
        assert names.index("a") < names.index("c")
        # B and C must come before D
        assert names.index("b") < names.index("d")
        assert names.index("c") < names.index("d")

    def test_resolve_tool_order__unknown_dependency_raises_error(self):
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a")),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b"), depends_on=["unknown"]),
        ]
        with pytest.raises(DotError) as exc_info:
            resolve_tool_order(tools)
        assert "unknown" in str(exc_info.value)
        assert "b" in str(exc_info.value)

    def test_resolve_tool_order__cycle_abc_raises_error(self):
        # A depends on B, B depends on C, C depends on A
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a"), depends_on=["b"]),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b"), depends_on=["c"]),
            ToolSpecs(name="c", check="check-c", scripts=ScriptSpecs(generic="install-c"), depends_on=["a"]),
        ]
        with pytest.raises(DotError) as exc_info:
            resolve_tool_order(tools)
        msg = str(exc_info.value)
        assert "Cycle detected" in msg
        assert "a" in msg
        assert "b" in msg
        assert "c" in msg

    def test_resolve_tool_order__self_dependency_raises_error(self):
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a"), depends_on=["a"]),
        ]
        with pytest.raises(DotError) as exc_info:
            resolve_tool_order(tools)
        assert "depends on itself" in str(exc_info.value)

    def test_resolve_tool_order__preserves_objects(self):
        # Ensure the returned list contains the actual ToolSpecs objects, not copies
        tools = [
            ToolSpecs(name="a", check="check-a", scripts=ScriptSpecs(generic="install-a")),
            ToolSpecs(name="b", check="check-b", scripts=ScriptSpecs(generic="install-b"), depends_on=["a"]),
        ]
        result = resolve_tool_order(tools)
        assert result[0] is tools[0]
        assert result[1] is tools[1]


# ---------------------------------------------------------------------------
# DotInstaller.__init__
# ---------------------------------------------------------------------------

class TestDotInstallerInit:

    def test_init__sets_root_and_home(self, tmp_path: Path):
        root = make_dot_root(tmp_path)
        home = tmp_path / "home"
        home.mkdir()

        installer = DotInstaller(root=root, override_home=home)

        assert installer.root == root
        assert installer.home == home

    def test_init__uses_home_dir_when_no_override(self, tmp_path: Path):
        root = make_dot_root(tmp_path)

        with patch("dot_tools.configure.Path.home", return_value=tmp_path / "default_home"):
            (tmp_path / "default_home").mkdir()
            installer = DotInstaller(root=root)

        assert installer.home == tmp_path / "default_home"

    def test_init__sets_zshrc_as_startup_on_darwin(self, tmp_path: Path):
        root = make_dot_root(tmp_path)
        home = tmp_path / "home"
        home.mkdir()

        with patch("dot_tools.configure.platform.system", return_value="Darwin"):
            installer = DotInstaller(root=root, override_home=home)

        assert installer.startup_config == home / ".zshrc"

    def test_init__sets_bashrc_as_startup_on_linux(self, tmp_path: Path):
        root = make_dot_root(tmp_path)
        home = tmp_path / "home"
        home.mkdir()

        with patch("dot_tools.configure.platform.system", return_value="Linux"):
            installer = DotInstaller(root=root, override_home=home)

        assert installer.startup_config == home / ".bashrc"

    def test_init__loads_install_manifest(self, tmp_path: Path):
        manifest = {**MINIMAL_MANIFEST, "link_paths": [".gitconfig"]}
        root = make_dot_root(tmp_path, manifest)
        home = tmp_path / "home"
        home.mkdir()

        installer = DotInstaller(root=root, override_home=home)

        assert Path(".gitconfig") in installer.install_manifest.link_paths


# ---------------------------------------------------------------------------
# DotInstaller._scrub_extra_dotfiles_block / _add_extra_dotfiles_block
# ---------------------------------------------------------------------------

class TestDotInstallerDotfilesBlock:

    def test_scrub_extra_dotfiles_block__removes_block_from_startup_config(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        installer.startup_config = tmp_path / ".zshrc"
        installer.startup_config.write_text(textwrap.dedent("""\
            export FOO=bar
            # EXTRA DOTFILES START
            source /some/dotfile
            # EXTRA DOTFILES END
            export BAZ=qux
        """))

        installer._scrub_extra_dotfiles_block()

        content = installer.startup_config.read_text()
        assert "EXTRA DOTFILES START" not in content
        assert "source /some/dotfile" not in content
        assert "export FOO=bar" in content
        assert "export BAZ=qux" in content

    def test_scrub_extra_dotfiles_block__is_no_op_when_block_absent(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        installer.startup_config = tmp_path / ".zshrc"
        original = "export FOO=bar\nexport BAZ=qux\n"
        installer.startup_config.write_text(original)

        installer._scrub_extra_dotfiles_block()

        assert installer.startup_config.read_text() == original

    def test_add_extra_dotfiles_block__appends_block_to_startup_config(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        installer.startup_config = tmp_path / ".zshrc"
        installer.startup_config.write_text("export FOO=bar\n")

        installer._add_extra_dotfiles_block()

        content = installer.startup_config.read_text()
        assert "EXTRA DOTFILES START" in content
        assert "EXTRA DOTFILES END" in content
        assert str(installer.home / ".extra_dotfiles") in content
        assert str(installer.root) in content


# ---------------------------------------------------------------------------
# DotInstaller._update_dotfiles
# ---------------------------------------------------------------------------

class TestDotInstallerUpdateDotfiles:

     def test_update_dotfiles__creates_extra_dotfiles_file_if_missing(self, tmp_path: Path):
         manifest = {**MINIMAL_MANIFEST, "dotfile_paths": [".dotrc"]}
         installer = make_installer(tmp_path, manifest)
         (installer.root / ".dotrc").touch()

         with patch("dot_tools.configure.spinner"):
             installer._update_dotfiles()

         assert (installer.home / ".extra_dotfiles").exists()

     def test_update_dotfiles__adds_source_entry_for_each_dotfile(self, tmp_path: Path):
         manifest = {**MINIMAL_MANIFEST, "dotfile_paths": [".dotrc", ".dot_colors"]}
         installer = make_installer(tmp_path, manifest)

         with patch("dot_tools.configure.spinner"):
             installer._update_dotfiles()

         content = (installer.home / ".extra_dotfiles").read_text()
         assert f"source {installer.root / '.dotrc'}" in content
         assert f"source {installer.root / '.dot_colors'}" in content

     def test_update_dotfiles__does_not_duplicate_existing_entries(self, tmp_path: Path):
         manifest = {**MINIMAL_MANIFEST, "dotfile_paths": [".dotrc"]}
         installer = make_installer(tmp_path, manifest)
         entry = f"source {installer.root / '.dotrc'}"
         (installer.home / ".extra_dotfiles").write_text(f"{entry}\n")

         with patch("dot_tools.configure.spinner"):
             installer._update_dotfiles()

         content = (installer.home / ".extra_dotfiles").read_text()
         assert content.count(entry) == 1

     def test_update_dotfiles__expands_tilde_paths_against_home(self, tmp_path: Path):
         manifest = {**MINIMAL_MANIFEST, "dotfile_paths": ["~/.dotrc_local"]}
         installer = make_installer(tmp_path, manifest)

         with patch("dot_tools.configure.spinner"):
             installer._update_dotfiles()

         content = (installer.home / ".extra_dotfiles").read_text()
         assert f"source {installer.home / '.dotrc_local'}" in content


# ---------------------------------------------------------------------------
# DotInstaller._create_dotrc_local
# ---------------------------------------------------------------------------
class TestDotInstallerCreateDotrcLocal:

    def test_create_dotrc_local__creates_file_when_absent(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        dotrc_local_path = installer.home / ".dotrc_local"

        assert not dotrc_local_path.exists()

        with patch("dot_tools.configure.spinner"):
            installer._create_dotrc_local()

        assert dotrc_local_path.exists()
        content = dotrc_local_path.read_text()
        assert "# ~/.dotrc_local" in content
        assert "machine-local" in content

    def test_create_dotrc_local__skips_when_file_exists(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        dotrc_local_path = installer.home / ".dotrc_local"
        original_content = "# Original content that should not change"
        dotrc_local_path.write_text(original_content)

        with patch("dot_tools.configure.spinner"):
            installer._create_dotrc_local()

        assert dotrc_local_path.read_text() == original_content


# ---------------------------------------------------------------------------
# DotInstaller._git_committed_content
# ---------------------------------------------------------------------------

class TestDotInstallerGitCommittedContent:

    def test_git_committed_content__returns_content_when_tracked(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        target = installer.root / "somefile.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("hello")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"hello"

        with patch("dot_tools.configure.subprocess.run", return_value=mock_result) as mock_run:
            content = installer._git_committed_content(target)

        assert content == b"hello"
        args = mock_run.call_args[0][0]
        assert "HEAD:somefile.txt" in args

    def test_git_committed_content__returns_none_when_untracked(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        target = installer.root / "untracked.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("hi")

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("dot_tools.configure.subprocess.run", return_value=mock_result):
            content = installer._git_committed_content(target)

        assert content is None


# ---------------------------------------------------------------------------
# DotInstaller._make_dirs
# ---------------------------------------------------------------------------

class TestDotInstallerMakeDirs:

    def test_make_dirs__creates_directories_from_manifest(self, tmp_path: Path):
        manifest = {**MINIMAL_MANIFEST, "mkdir_paths": [".vim/backup", ".vim/swap"]}
        installer = make_installer(tmp_path, manifest)

        with patch("dot_tools.configure.spinner"):
            installer._make_dirs()

        assert (installer.home / ".vim/backup").is_dir()
        assert (installer.home / ".vim/swap").is_dir()

    def test_make_dirs__is_idempotent(self, tmp_path: Path):
        manifest = {**MINIMAL_MANIFEST, "mkdir_paths": [".vim/backup"]}
        installer = make_installer(tmp_path, manifest)

        with patch("dot_tools.configure.spinner"):
            installer._make_dirs()
            installer._make_dirs()  # second call should not raise

        assert (installer.home / ".vim/backup").is_dir()


# ---------------------------------------------------------------------------
# DotInstaller._ensure_startup_config / _startup
# ---------------------------------------------------------------------------

class TestDotInstallerStartup:

    def test_ensure_startup_config__creates_startup_config_if_missing(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        installer.startup_config = tmp_path / ".zshrc"
        # file does not exist yet

        with patch("dot_tools.configure.spinner"):
            installer._ensure_startup_config()

        assert installer.startup_config.exists()

    def test_ensure_startup_config__preserves_existing_content(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        installer.startup_config = tmp_path / ".zshrc"
        original_content = "export FOO=bar\n"
        installer.startup_config.write_text(original_content)

        with patch("dot_tools.configure.spinner"):
            installer._ensure_startup_config()

        assert installer.startup_config.read_text() == original_content

    def test_startup__scrubs_and_readds_block_when_config_exists(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        installer.startup_config = tmp_path / ".zshrc"
        installer.startup_config.write_text(textwrap.dedent("""\
            export FOO=bar
            # EXTRA DOTFILES START
            source /old/path
            # EXTRA DOTFILES END
        """))

        with patch("dot_tools.configure.spinner"):
            installer._startup()

        content = installer.startup_config.read_text()
        assert "source /old/path" not in content
        assert "EXTRA DOTFILES START" in content
        assert "export FOO=bar" in content

    def test_install_dot__integrates_startup_before_tools_and_settings(self, tmp_path: Path):
        installer = make_installer(tmp_path)
        call_order: list[str] = []

        def record_startup_creation():
            call_order.append("ensure")
            DotInstaller._ensure_startup_config(installer)

        def record_dotfile_update():
            call_order.append("update")
            DotInstaller._update_dotfiles(installer)

        def record_scrub():
            call_order.append("scrub")
            DotInstaller._scrub_extra_dotfiles_block(installer)

        def record_add():
            call_order.append("add")
            DotInstaller._add_extra_dotfiles_block(installer)

        def record_tools():
            assert installer.startup_config.exists()
            assert (installer.home / ".extra_dotfiles").exists()
            assert "EXTRA DOTFILES START" in installer.startup_config.read_text()
            assert "EXTRA DOTFILES END" in installer.startup_config.read_text()
            call_order.append("tools")

        with (
            patch.object(installer, "_ensure_startup_config", side_effect=record_startup_creation),
            patch.object(installer, "_update_dotfiles", side_effect=record_dotfile_update),
            patch.object(installer, "_scrub_extra_dotfiles_block", side_effect=record_scrub),
            patch.object(installer, "_add_extra_dotfiles_block", side_effect=record_add),
            patch.object(installer, "_install_tools", side_effect=record_tools),
            patch.object(installer, "_apply_settings", side_effect=lambda: call_order.append("settings")),
            patch.object(installer, "_make_dirs"),
            patch.object(installer, "_make_links"),
            patch.object(installer, "_copy_files"),
            patch.object(installer, "_setup_ssh_config"),
            patch.object(installer, "_create_dotrc_local"),
            patch.object(installer, "_github_cli_login"),
            patch.object(installer, "_add_ssh_keys"),
            patch.object(installer, "_install_services"),
            patch.object(installer, "_create_local_agents_file"),
            patch("dot_tools.configure.generate_keypair"),
            patch("dot_tools.configure.terminal_message"),
            patch("dot_tools.configure.spinner"),
            patch("dot_tools.configure.os.getlogin", return_value="test-user"),
        ):
            installer.install_dot()

        assert call_order.index("ensure") < call_order.index("tools")
        assert call_order.index("update") < call_order.index("tools")
        assert call_order.index("scrub") < call_order.index("tools")
        assert call_order.index("add") < call_order.index("tools")
        assert call_order.index("ensure") < call_order.index("settings")
        assert call_order.index("update") < call_order.index("settings")
        assert call_order.index("scrub") < call_order.index("settings")
        assert call_order.index("add") < call_order.index("settings")
        assert call_order == ["ensure", "update", "scrub", "add", "tools", "settings"]


# ---------------------------------------------------------------------------
# DotInstaller._apply_settings
# ---------------------------------------------------------------------------

class TestDotInstallerApplySettings:

    def test_apply_settings__skips_setting_for_other_platform(self, tmp_path: Path):
        manifest = {
            **MINIMAL_MANIFEST,
            "settings": [
                {
                    "name": "linux-only",
                    "check": "check-setting",
                    "scripts": {"linux": "apply-setting"},
                    "platform": "Linux",
                }
            ],
        }
        installer = make_installer(tmp_path, manifest)

        with (
            patch("dot_tools.configure.platform.system", return_value="Darwin"),
            patch("dot_tools.configure.subprocess.run") as run,
            patch("dot_tools.configure.spinner"),
        ):
            installer._apply_settings()

        run.assert_not_called()

    def test_apply_settings__uses_override_home_for_setting_check(self, tmp_path: Path):
        manifest = {
            **MINIMAL_MANIFEST,
            "settings": [
                {
                    "name": "opencode-setting",
                    "check": "test -d $HOME/.config/opencode",
                    "scripts": {"generic": "touch \"$HOME/.config/opencode/ready\""},
                }
            ],
        }
        installer = make_installer(tmp_path, manifest)

        with patch("dot_tools.configure.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            installer._apply_settings()

        command = mock_run.call_args.args[0]
        environment = mock_run.call_args.kwargs["env"]
        assert command == "test -d $HOME/.config/opencode"
        assert environment["HOME"] == str(installer.home)

    @pytest.mark.parametrize(
        ("method_name", "manifest_key", "name", "script"),
        [
            ("_apply_settings", "settings", "prompt-setting", "setting-script"),
            ("_install_tools", "tools", "prompt-tool", "tool-script"),
        ],
    )
    def test_install_script__streams_partial_combined_output_to_terminal_and_log(
        self, tmp_path: Path, method_name: str, manifest_key: str, name: str, script: str, capsys
    ):
        manifest = {
            **MINIMAL_MANIFEST,
            manifest_key: [{"name": name, "check": f"check-{name}", "scripts": {"generic": script}}],
        }
        installer = make_installer(tmp_path, manifest)
        stream = FakeBinaryStream(b"prompt> ", b"progress\n", b"stderr text")
        process = MagicMock(stdout=stream)
        process.returncode = 0

        with (
            patch("dot_tools.configure.subprocess.run", return_value=MagicMock(returncode=1)),
            patch("dot_tools.configure.subprocess.Popen", return_value=process) as popen,
            patch("dot_tools.configure.select.select", side_effect=lambda streams, *_: (streams, [], [])),
            patch("dot_tools.configure.pause_live"),
            patch("dot_tools.configure.logger.debug") as log_debug,
        ):
            getattr(installer, method_name)()

        assert capsys.readouterr().out == "prompt> progress\nstderr text"
        assert any("prompt> " in call.args[0] for call in log_debug.call_args_list)
        assert any("stderr text" in call.args[0] for call in log_debug.call_args_list)
        assert popen.call_args.kwargs["stderr"] == subprocess.STDOUT
        assert popen.call_args.kwargs["bufsize"] == 0
        assert "text" not in popen.call_args.kwargs
        assert stream.read_sizes[:2] == [4096, 4096]

    @pytest.mark.parametrize(
        ("method_name", "manifest_key", "name", "script"),
        [
            ("_apply_settings", "settings", "failing-setting", "setting-script"),
            ("_install_tools", "tools", "failing-tool", "tool-script"),
        ],
    )
    def test_install_script__failure_includes_last_20_output_lines(
        self, tmp_path: Path, method_name: str, manifest_key: str, name: str, script: str
    ):
        manifest = {
            **MINIMAL_MANIFEST,
            manifest_key: [{"name": name, "check": f"check-{name}", "scripts": {"generic": script}}],
        }
        installer = make_installer(tmp_path, manifest)
        stream = FakeBinaryStream("\n".join(f"line-{index}" for index in range(25)).encode())
        process = MagicMock(stdout=stream)
        process.returncode = 7

        with (
            patch("dot_tools.configure.subprocess.run", return_value=MagicMock(returncode=1)),
            patch("dot_tools.configure.subprocess.Popen", return_value=process),
            patch("dot_tools.configure.select.select", side_effect=lambda streams, *_: (streams, [], [])),
            patch("dot_tools.configure.pause_live"),
        ):
            with pytest.raises(DotError) as exc_info:
                getattr(installer, method_name)()

        message = str(exc_info.value)
        assert "line-5" in message
        assert "line-24" in message
        assert "line-4" not in message
        assert name in message


# ---------------------------------------------------------------------------
# DotInstaller._install_tools
# ---------------------------------------------------------------------------

class TestDotInstallerInstallTools:

    def test_install_manifest__installs_opencode_npm_dependencies(self):
        root = Path(__file__).parents[1]
        manifest = yaml.safe_load((root / "etc/install.yaml").read_text())
        package = json.loads((root / ".config/opencode/package.json").read_text())

        assert ".config/opencode/package.json" in manifest["link_paths"]
        opencode_deps = next(tool for tool in manifest["tools"] if tool["name"] == "opencode-npm-deps")
        assert opencode_deps["check"] == 'test -d "$DOT_ROOT/.config/opencode/node_modules/@opencode-ai/plugin"'
        assert opencode_deps["scripts"]["generic"] == (
            '. "$HOME/.nvm/nvm.sh"\n'
            'npm install --prefix "$DOT_ROOT/.config/opencode"\n'
        )
        assert opencode_deps["depends_on"] == ["node"]
        assert "bun" not in {tool["name"] for tool in manifest["tools"]}
        assert package["dependencies"]["@opencode-ai/plugin"] == "1.18.14"

    def test_install_tools__uses_override_home_for_opencode_npm_check(self, tmp_path: Path):
        manifest = {
            **MINIMAL_MANIFEST,
            "tools": [
                {
                    "name": "opencode-npm-deps",
                    "check": "test -d \"$DOT_ROOT/.config/opencode/node_modules/@opencode-ai/plugin\"",
                    "scripts": {"generic": "npm install --prefix \"$DOT_ROOT/.config/opencode\""},
                }
            ],
        }
        installer = make_installer(tmp_path / "home with spaces", manifest)

        with patch("dot_tools.configure.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            installer._install_tools()

        assert mock_run.call_args.args[0] == 'test -d "$DOT_ROOT/.config/opencode/node_modules/@opencode-ai/plugin"'
        assert mock_run.call_args.kwargs["env"]["HOME"] == str(installer.home)
        assert mock_run.call_args.kwargs["env"]["DOT_ROOT"] == str(installer.root)

    def test_install_tools__uses_override_home_for_opencode_npm_install(self, tmp_path: Path):
        manifest = {
            **MINIMAL_MANIFEST,
            "tools": [
                {
                    "name": "opencode-npm-deps",
                    "check": "test -d \"$DOT_ROOT/.config/opencode/node_modules/@opencode-ai/plugin\"",
                    "scripts": {"generic": "npm install --prefix \"$DOT_ROOT/.config/opencode\""},
                }
            ],
        }
        installer = make_installer(tmp_path / "home with spaces", manifest)
        process = MagicMock(returncode=0, stdout=FakeBinaryStream())

        with (
            patch("dot_tools.configure.subprocess.run", return_value=MagicMock(returncode=1)),
            patch("dot_tools.configure.subprocess.Popen", return_value=process) as mock_popen,
            patch("dot_tools.configure.select.select", side_effect=lambda streams, *_: (streams, [], [])),
            patch("dot_tools.configure.pause_live"),
        ):
            installer._install_tools()

        assert mock_popen.call_args.args[0] == 'npm install --prefix "$DOT_ROOT/.config/opencode"'
        assert mock_popen.call_args.kwargs["env"]["HOME"] == str(installer.home)
        assert mock_popen.call_args.kwargs["env"]["DOT_ROOT"] == str(installer.root)

    def test_install_tools__calls_resolve_tool_order(self, tmp_path: Path):
        # Verify that _install_tools calls resolve_tool_order
        manifest = {
            **MINIMAL_MANIFEST,
            "tools": [
                {
                    "name": "a",
                    "check": "check-a",
                    "scripts": {"generic": "install-a"},
                    "depends_on": [],
                },
                {
                    "name": "b",
                    "check": "check-b",
                    "scripts": {"generic": "install-b"},
                    "depends_on": ["a"],
                },
            ],
        }
        installer = make_installer(tmp_path, manifest)

        with patch("dot_tools.configure.resolve_tool_order") as mock_resolve:
            mock_resolve.return_value = installer.install_manifest.tools
            with patch("dot_tools.configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                with patch("dot_tools.configure.subprocess.Popen") as mock_popen:
                    mock_proc = MagicMock()
                    mock_proc.stdout = None
                    mock_proc.stderr = None
                    mock_popen.return_value = mock_proc

                    installer._install_tools()

        # Verify resolve_tool_order was called with the manifest tools
        mock_resolve.assert_called_once_with(installer.install_manifest.tools)

    def test_install_tools__respects_resolved_order(self, tmp_path: Path):
        # Tools declared in reverse dependency order (C→B→A in YAML, but A must install first).
        # _install_tools() must install them in resolved order: A, B, C.
        manifest = {
            **MINIMAL_MANIFEST,
            "tools": [
                {
                    "name": "c",
                    "check": "check-c",
                    "scripts": {"generic": "install-c"},
                    "depends_on": ["b"],
                },
                {
                    "name": "b",
                    "check": "check-b",
                    "scripts": {"generic": "install-b"},
                    "depends_on": ["a"],
                },
                {
                    "name": "a",
                    "check": "check-a",
                    "scripts": {"generic": "install-a"},
                    "depends_on": [],
                },
            ],
        }
        installer = make_installer(tmp_path, manifest)

        checked_order: list[str] = []

        def fake_run(cmd, **kwargs):
            result = MagicMock()
            # Return 0 (already installed) so the install script is never reached.
            # We only care about the order of check-command invocations.
            result.returncode = 0
            if isinstance(cmd, str):
                checked_order.append(cmd)
            return result

        with patch("dot_tools.configure.subprocess.run", side_effect=fake_run):
            installer._install_tools()

        # Extract tool names from check commands in the order they were invoked
        install_order = [cmd.replace("check-", "") for cmd in checked_order if cmd.startswith("check-")]
        assert install_order == ["a", "b", "c"]
