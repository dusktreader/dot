import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

from dot_tools.cli.main import cli
from dot_tools.opencode_profile import OpenCodeLifecycle, OpenCodeProfileError, PERSONAL_PROFILE
from tools.validate_opencode_profiles import validate


ROOT = Path(__file__).parents[1]


def lifecycle(tmp_path: Path, **kwargs: Any) -> OpenCodeLifecycle:
    environment = {"HOME": str(tmp_path / "home"), "DOT_HOME": str(ROOT), "PATH": "/usr/bin:/bin"}
    environment.update(kwargs.pop("environment", {}))
    return OpenCodeLifecycle(
        PERSONAL_PROFILE,
        environment=environment,
        repository_root=ROOT,
        **kwargs,
    )


def test_personal_profile_has_aliases_and_only_personal_zen_fallback() -> None:
    router = yaml.safe_load((ROOT / ".config/litellm/personal.yaml").read_text())
    names = [item["model_name"] for item in router["model_list"]]
    assert {"light", "standard", "premium", "personal-light-zen"}.issubset(names)
    assert router["router_settings"]["fallbacks"] == [{"light": ["personal-light-zen"]}]
    assert "os.environ/OPENCODE_ZEN_API_KEY" in (ROOT / ".config/litellm/personal.yaml").read_text()


def test_personal_overlay_uses_responses_transport_for_gpt_5_6() -> None:
    overlay = json.loads((ROOT / ".config/opencode/profiles/personal.json").read_text())
    assert overlay["provider"]["personal"]["npm"] == "@ai-sdk/openai"


def test_personal_premium_route_uses_github_copilot_provider() -> None:
    router = yaml.safe_load((ROOT / ".config/litellm/personal.yaml").read_text())
    premium = next(item for item in router["model_list"] if item["model_name"] == "premium")
    assert premium["litellm_params"]["model"] == "github_copilot/gpt-5.6-sol"
    assert "api_key" not in premium["litellm_params"]


def test_personal_copilot_routes_use_models_supported_by_installed_litellm() -> None:
    router = yaml.safe_load((ROOT / ".config/litellm/personal.yaml").read_text())
    models = {
        item["model_name"]: item["litellm_params"]["model"]
        for item in router["model_list"]
        if item["model_name"] in {"light", "standard", "premium"}
    }
    assert models == {
        "light": "github_copilot/gpt-5.6-luna",
        "standard": "github_copilot/gpt-5.6-sol",
        "premium": "github_copilot/gpt-5.6-sol",
    }


def test_personal_profile_validation_is_offline_and_clean() -> None:
    assert validate(ROOT, None) == []


def test_personal_overlay_defaults_to_light_and_keeps_standard_alias() -> None:
    overlay = json.loads((ROOT / ".config/opencode/profiles/personal.json").read_text())
    assert overlay["model"] == "personal/light"
    assert overlay["provider"]["personal"]["models"]["standard"]["name"] == "Standard"


@pytest.mark.parametrize("tier", ["light", "standard", "premium"])
def test_environment_selects_each_tier_without_provider_contact(tmp_path: Path, tier: str) -> None:
    environment = lifecycle(tmp_path).environment_for(tier, explicit_cli_premium=tier == "premium")
    assert environment["OPENCODE_ROUTING_PROFILE"] == "profile:personal"
    assert environment["OPENCODE_ROUTING_TIER"] == tier
    config = json.loads(environment["OPENCODE_CONFIG_CONTENT"])
    assert config["default_agent"] == "principal"
    assert config["model"] == f"personal/{tier}"
    assert config["agent"]["principal"]["variant"] == "xhigh"
    assert environment.get("OPENCODE_CLI_PREMIUM_AUTHORIZED") == ("1" if tier == "premium" else None)


def test_environment_preserves_home_and_isolates_runtime_state(tmp_path: Path) -> None:
    original_home = str(tmp_path / "home")
    environment = lifecycle(tmp_path).environment_for()
    assert environment["HOME"] == original_home
    assert environment["LITELLM_LOCAL_MODEL_COST_MAP"] == "True"
    assert environment["XDG_DATA_HOME"].endswith("personal/xdg-data")
    assert environment["GITHUB_COPILOT_TOKEN_DIR"].endswith("personal/copilot")


@pytest.mark.parametrize(
    "executable",
    ["litellm", "/usr/local/bin/litellm", "/usr/local/bin/python /usr/local/bin/litellm"],
)
def test_router_ownership_accepts_litellm_command_shapes(tmp_path: Path, executable: str) -> None:
    command = f"{executable} --config {ROOT / '.config/litellm/personal.yaml'} --host 127.0.0.1 --port 4010"
    profile = lifecycle(
        tmp_path,
        process_alive=lambda _: True,
        process_command=lambda _: command,
    )
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    assert profile.router_pid_is_ours()


@pytest.mark.parametrize("executable", ["./litellm", "wrapper/litellm"])
def test_router_ownership_rejects_relative_litellm_path(tmp_path: Path, executable: str) -> None:
    command = f"{executable} --config {ROOT / '.config/litellm/personal.yaml'} --host 127.0.0.1 --port 4010"
    profile = lifecycle(tmp_path, process_alive=lambda _: True, process_command=lambda _: command)
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    assert not profile.router_pid_is_ours()


def test_router_ownership_rejects_wrapper_with_later_litellm_token(tmp_path: Path) -> None:
    command = f"python wrapper litellm --config {ROOT / '.config/litellm/personal.yaml'} --host 127.0.0.1 --port 4010"
    profile = lifecycle(tmp_path, process_alive=lambda _: True, process_command=lambda _: command)
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    assert not profile.router_pid_is_ours()


def test_invalid_tier_is_rejected_before_router_start(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid routing tier"):
        lifecycle(tmp_path).environment_for("opus")


def test_launch_uses_execvpe_and_passes_arguments(tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def execvpe(program: str, arguments: list[str], environment: dict[str, str]) -> None:
        captured.update(program=program, arguments=arguments, environment=environment)

    profile = lifecycle(
        tmp_path,
        health_probe=lambda: True,
        process_alive=lambda _: True,
        process_command=lambda _: f"litellm --config {ROOT / '.config/litellm/personal.yaml'} --host 127.0.0.1 --port 4010",
        execvpe=execvpe,
    )
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    profile.launch(["--session", "abc"], "standard")

    assert captured["program"] == "opencode"
    assert captured["arguments"] == ["opencode", "--session", "abc"]
    assert captured["environment"]["OPENCODE_ROUTING_TIER"] == "standard"  # type: ignore[index]


def test_launch_starts_router_with_list_subprocess_and_generates_private_key(tmp_path: Path) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def popen(command: list[str], **kwargs: object) -> SimpleNamespace:
        calls.append((command, kwargs))
        return SimpleNamespace(pid=123)

    profile = lifecycle(
        tmp_path,
        health_probe=lambda: len(calls) > 0,
        port_probe=lambda: False,
        process_alive=lambda _: True,
        popen=popen,
        execvpe=lambda *_: None,
        command_path=lambda _: "/usr/local/bin/litellm",
    )
    profile.launch([], "light")

    assert calls[0][0] == [
        "/usr/local/bin/litellm",
        "--config",
        str(ROOT / ".config/litellm/personal.yaml"),
        "--host",
        "127.0.0.1",
        "--port",
        "4010",
    ]
    assert profile.key_file.stat().st_mode & 0o777 == 0o600
    assert profile.key_file.read_text()
    assert calls[0][1]["env"]["HOME"] == str(tmp_path / "home")  # type: ignore[index]


@pytest.mark.parametrize("process_alive", [lambda _: True, lambda _: False])
def test_failed_new_router_start_cleans_only_new_state(tmp_path: Path, process_alive: Any) -> None:
    killed: list[int] = []

    def popen(command: list[str], **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(pid=123)

    profile = lifecycle(
        tmp_path,
        health_probe=lambda: False,
        port_probe=lambda: False,
        process_alive=process_alive,
        popen=popen,
        kill=lambda pid, _: killed.append(pid),
        sleep=lambda _: None,
        command_path=lambda _: "/usr/local/bin/litellm",
    )
    profile._ensure_state()
    profile.log_file.write_text("startup output")

    with pytest.raises(OpenCodeProfileError, match="startup"):
        profile.start_router(profile.environment_for())

    assert not profile.pid_file.exists()
    assert not profile.log_file.exists()
    assert killed == ([] if not process_alive(123) else [123])


def test_healthy_unrelated_port_fails_closed(tmp_path: Path) -> None:
    profile = lifecycle(tmp_path, health_probe=lambda: True, process_alive=lambda _: True, process_command=lambda _: "python unrelated")
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    with pytest.raises(OpenCodeProfileError, match="refusing to adopt"):
        profile.start_router(profile.environment_for())


def test_unhealthy_unrelated_port_fails_closed(tmp_path: Path) -> None:
    profile = lifecycle(tmp_path, health_probe=lambda: False, port_probe=lambda: True)
    with pytest.raises(OpenCodeProfileError, match="refusing to start LiteLLM"):
        profile.start_router(profile.environment_for())


def test_matching_pid_is_reused_and_unrelated_pid_is_not_stopped(tmp_path: Path) -> None:
    killed: list[int] = []
    command = f"litellm --config {ROOT / '.config/litellm/personal.yaml'} --host 127.0.0.1 --port 4010"
    profile = lifecycle(
        tmp_path,
        health_probe=lambda: True,
        process_alive=lambda _: True,
        process_command=lambda _: command,
        kill=lambda pid, _: killed.append(pid),
    )
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    profile.start_router(profile.environment_for())
    profile.stop()
    assert killed == [42]

    profile.pid_file.write_text("42\n")
    profile._process_command = lambda _: "python unrelated"
    profile.stop()
    assert killed == [42]


def test_waiting_for_preexisting_matching_router_does_not_clean_it_up(tmp_path: Path) -> None:
    killed: list[int] = []
    command = f"litellm --config {ROOT / '.config/litellm/personal.yaml'} --host 127.0.0.1 --port 4010"
    profile = lifecycle(
        tmp_path,
        health_probe=lambda: False,
        process_alive=lambda _: True,
        process_command=lambda _: command,
        kill=lambda pid, _: killed.append(pid),
        sleep=lambda _: None,
    )
    profile.state_root.mkdir(parents=True)
    profile.pid_file.write_text("42\n")
    profile.log_file.write_text("existing router log")

    with pytest.raises(OpenCodeProfileError, match="did not become healthy"):
        profile.start_router(profile.environment_for())

    assert killed == []
    assert profile.pid_file.read_text() == "42\n"
    assert profile.log_file.read_text() == "existing router log"


def test_status_does_not_print_router_key(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    profile = lifecycle(tmp_path, health_probe=lambda: False)
    profile.status()
    output = capsys.readouterr().out
    assert "profile: personal" in output
    assert "4010" in output
    assert "router.key" not in output


def test_cli_launch_parses_only_its_tier_and_forwards_extra_args(tmp_path: Path) -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.personal_lifecycle") as factory:
        result = runner.invoke(cli, ["opencode", "launch", "--tier", "standard", "--session", "abc"])
    assert result.exit_code == 0
    factory.return_value.launch.assert_called_once_with(["--session", "abc"], "standard", explicit_cli_premium=False)


def test_cli_premium_does_not_require_approval_marker(tmp_path: Path) -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.personal_lifecycle") as factory:
        result = runner.invoke(cli, ["opencode", "launch", "--tier", "premium"])
    assert result.exit_code == 0
    factory.return_value.launch.assert_called_once_with([], "premium", explicit_cli_premium=True)


def test_cli_rejects_invalid_tier() -> None:
    result = CliRunner().invoke(cli, ["opencode", "launch", "--tier", "opus"])
    assert result.exit_code == 2
    assert "Invalid routing tier" in result.output


def test_cli_status_and_stop_delegate_to_personal_lifecycle() -> None:
    runner = CliRunner()
    with patch("dot_tools.cli.opencode.personal_lifecycle") as factory:
        assert runner.invoke(cli, ["opencode", "status"]).exit_code == 0
        assert runner.invoke(cli, ["opencode", "stop"]).exit_code == 0
    factory.return_value.status.assert_called_once_with()
    factory.return_value.stop.assert_called_once_with()


def test_existing_opencode_commands_remain_registered() -> None:
    output = CliRunner().invoke(cli, ["opencode", "--help"]).output
    assert all(command in output for command in ("launch", "status", "stop", "costs", "trends", "staleness-guard"))


def test_alias_and_manifest_migration() -> None:
    manifest = yaml.safe_load((ROOT / "etc/install.yaml").read_text())
    assert "bin/opencode-tab" not in manifest["link_paths"]
    assert "alias doc='dt opencode launch'" in (ROOT / ".dotrc").read_text()
    assert not (ROOT / "bin/opencode-tab").exists()
