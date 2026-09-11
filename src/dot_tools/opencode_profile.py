"""Manage the personal OpenCode router and process lifecycle."""

import json
import os
import shlex
import shutil
import signal
import socket
import subprocess
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

TIERS = frozenset(("light", "standard", "premium"))

PERSONAL_PROVIDER_ENV_VARS = frozenset(
    {
        "OPENCODE_ZEN_API_KEY",
        "OPENCODE_ZEN_TOKEN",
        "OPENCODE_ROUTER_KEY",
        "OPENCODE_PREMIUM_APPROVED",
        "GITHUB_COPILOT_TOKEN",
        "GITHUB_COPILOT_API_KEY",
        "GITHUB_COPILOT_ACCESS_TOKEN",
        "GITHUB_COPILOT_OAUTH_TOKEN",
        "GITHUB_TOKEN",
        "GH_TOKEN",
    }
)


class LifecycleHooks(TypedDict, total=False):
    """Type lifecycle seams used by tests and local integrations."""

    environment: dict[str, str]
    repository_root: Path
    health_probe: Callable[[], bool]
    port_probe: Callable[[], bool]
    process_alive: Callable[[int], bool]
    process_command: Callable[[int], str | None]
    popen: Callable[..., subprocess.Popen[bytes]]
    execvpe: Callable[[str, list[str], dict[str, str]], Any]
    kill: Callable[[int, int], None]
    sleep: Callable[[float], None]
    command_path: Callable[[str], str | None]


class OpenCodeProfileError(RuntimeError):
    """Report a profile lifecycle failure without exposing secrets."""


@dataclass(frozen=True)
class ProfileSpec:
    """Describe the filesystem and routing boundary for one OpenCode profile."""

    name: str
    profile_tag: str
    router_name: str
    port: int
    repository_env: str
    profile_config_name: str
    requires_work_account: bool = False


PERSONAL_PROFILE = ProfileSpec(
    name="personal",
    profile_tag="profile:personal",
    router_name="personal",
    port=4010,
    repository_env="DOT_HOME",
    profile_config_name="personal",
)


def validate_tier(tier: str) -> str:
    """Validate and return a supported routing tier."""
    if tier not in TIERS:
        raise ValueError(f"Invalid routing tier {tier!r}. Use light, standard, or premium.")
    return tier


class OpenCodeLifecycle:
    """Start, inspect, stop, and replace the current process with OpenCode."""

    def __init__(
        self,
        profile: ProfileSpec = PERSONAL_PROFILE,
        *,
        environment: dict[str, str] | None = None,
        repository_root: Path | None = None,
        health_probe: Callable[[], bool] | None = None,
        port_probe: Callable[[], bool] | None = None,
        process_alive: Callable[[int], bool] | None = None,
        process_command: Callable[[int], str | None] | None = None,
        popen: Callable[..., subprocess.Popen[bytes]] | None = None,
        execvpe: Callable[[str, list[str], dict[str, str]], object] | None = None,
        kill: Callable[[int, int], None] | None = None,
        sleep: Callable[[float], None] | None = None,
        command_path: Callable[[str], str | None] | None = None,
    ) -> None:
        self.profile = profile
        self.base_environment = dict(environment if environment is not None else os.environ)
        self.home = Path(self.base_environment.get("HOME", str(Path.home()))).expanduser()
        self.repository_root = (repository_root or self._default_repository_root()).expanduser().resolve()
        self._health_probe = health_probe
        self._port_probe = port_probe
        self._process_alive = process_alive
        self._process_command = process_command
        self._popen = popen or subprocess.Popen
        self._execvpe = execvpe or os.execvpe
        self._kill = kill or os.kill
        self._sleep = sleep or time.sleep
        self._command_path = command_path or shutil.which

    @property
    def state_root(self) -> Path:
        """Return the profile-owned state directory."""
        return self.home / ".local" / "state" / self.profile.router_name

    @property
    def router_config(self) -> Path:
        """Return the profile-owned LiteLLM configuration."""
        return self.repository_root / ".config" / "litellm" / f"{self.profile.name}.yaml"

    @property
    def open_code_config(self) -> Path:
        """Return the profile-owned OpenCode overlay."""
        return self.repository_root / ".config" / "opencode" / "profiles" / f"{self.profile.profile_config_name}.json"

    @property
    def pid_file(self) -> Path:
        """Return the profile-owned router PID file."""
        return self.state_root / "router.pid"

    @property
    def log_file(self) -> Path:
        """Return the profile-owned router log file."""
        return self.state_root / "router.log"

    @property
    def key_file(self) -> Path:
        """Return the profile-owned router key file."""
        return self.state_root / "router.key"

    @property
    def endpoint(self) -> str:
        """Return the loopback OpenAI-compatible endpoint."""
        return f"http://127.0.0.1:{self.profile.port}/v1"

    def _default_repository_root(self) -> Path:
        configured_root = self.base_environment.get(self.profile.repository_env)
        if configured_root:
            return Path(configured_root)
        if self.profile.requires_work_account:
            return self.home / "src" / "mhe" / "work-dot"
        return Path(__file__).resolve().parents[2]

    def _config_content(self, tier: str) -> str:
        model = f"{self.profile.router_name}/{tier}"
        agents = {
            agent: {"model": model}
            for agent in (
                "principal",
                "plan",
                "title",
                "summary",
                "compaction",
                "architect-planner",
                "architect-reviewer",
                "engineer-executor",
                "engineer-investigator",
                "engineer-planner",
                "engineer-reviewer",
                "engineer-task-planner",
            )
        }
        agents["principal"]["variant"] = "xhigh"
        return json.dumps(
            {"default_agent": "principal", "model": model, "small_model": model, "agent": agents},
            separators=(",", ":"),
        )

    def environment_for(self, tier: str = "light", *, explicit_cli_premium: bool = False) -> dict[str, str]:
        """Build the isolated OpenCode and router environment for one invocation."""
        validate_tier(tier)
        state_root = self.state_root
        environment = dict(self.base_environment)
        if self.profile.requires_work_account:
            for variable in PERSONAL_PROVIDER_ENV_VARS:
                environment.pop(variable, None)
        environment.update(
            {
                "OPENCODE_ROUTING_PROFILE": self.profile.profile_tag,
                "OPENCODE_PROFILE_NAME": self.profile.name,
                "OPENCODE_ROUTING_TIER": tier,
                "OPENCODE_ROUTER_ENDPOINT": self.endpoint,
                "OPENCODE_CONFIG": str(self.open_code_config),
                "OPENCODE_CONFIG_CONTENT": self._config_content(tier),
                "OPENCODE_CONFIG_DIR": str(self.home / ".config" / "opencode"),
                "XDG_CONFIG_HOME": str(state_root / "xdg-config"),
                "XDG_DATA_HOME": str(state_root / "xdg-data"),
                "XDG_STATE_HOME": str(state_root / "xdg-state"),
                "XDG_CACHE_HOME": str(state_root / "xdg-cache"),
                "GITHUB_COPILOT_TOKEN_DIR": str(state_root / "copilot"),
                "GITHUB_COPILOT_API_KEY_FILE": "api-key.json",
                "GITHUB_COPILOT_ACCESS_TOKEN_FILE": "access-token",
            }
        )
        no_proxy = environment.get("NO_PROXY", "")
        loopback = "127.0.0.1,localhost"
        environment["NO_PROXY"] = f"{loopback},{no_proxy}" if no_proxy else loopback
        environment["no_proxy"] = environment["NO_PROXY"]
        environment.pop("OPENCODE_CLI_PREMIUM_AUTHORIZED", None)
        if explicit_cli_premium and tier == "premium":
            environment["OPENCODE_CLI_PREMIUM_AUTHORIZED"] = "1"
        return environment

    def _ensure_state(self) -> None:
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.state_root.chmod(0o700)
        for name in ("copilot", "xdg-config", "xdg-data", "xdg-state", "xdg-cache"):
            path = self.state_root / name
            path.mkdir(exist_ok=True)
            if name == "copilot":
                path.chmod(0o700)

    def _router_key(self) -> str:
        self._ensure_state()
        if self.key_file.is_symlink():
            raise OpenCodeProfileError(f"Router key path is a symlink: {self.key_file}")
        if not self.key_file.exists() or not self.key_file.read_text().strip():
            try:
                descriptor = os.open(self.key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                pass
            else:
                with os.fdopen(descriptor, "w") as key_file:
                    key_file.write(os.urandom(32).hex())
        self.key_file.chmod(0o600)
        if not self.key_file.read_text().strip():
            self.key_file.write_text(os.urandom(32).hex())
        key = self.key_file.read_text().strip()
        if not key:
            raise OpenCodeProfileError(f"Router key is empty: {self.key_file}")
        return key

    def _health_url(self) -> str:
        return f"http://127.0.0.1:{self.profile.port}/health/liveliness"

    def router_healthy(self) -> bool:
        """Return whether the profile router answers its local health endpoint."""
        if self._health_probe is not None:
            return self._health_probe()
        try:
            with build_opener(ProxyHandler({})).open(self._health_url(), timeout=1) as response:
                return 200 <= response.status < 400
        except (OSError, URLError):
            return False

    def router_port_is_open(self) -> bool:
        """Return whether any local process has claimed the profile port."""
        if self._port_probe is not None:
            return self._port_probe()
        try:
            with socket.create_connection(("127.0.0.1", self.profile.port), timeout=1):
                return True
        except OSError:
            return False

    def process_is_alive(self, pid: int) -> bool:
        """Return whether a process ID currently exists."""
        if self._process_alive is not None:
            return self._process_alive(pid)
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def process_command(self, pid: int) -> str | None:
        """Return the complete command recorded by the operating system."""
        if self._process_command is not None:
            return self._process_command(pid)
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def _read_pid(self) -> int | None:
        try:
            pid = int(self.pid_file.read_text().strip())
        except (FileNotFoundError, ValueError):
            return None
        return pid if pid > 0 else None

    def router_pid_is_ours(self) -> bool:
        """Return whether the recorded PID is alive and owns this exact router command."""
        pid = self._read_pid()
        if pid is None or not self.process_is_alive(pid):
            return False
        command = self.process_command(pid)
        if not command:
            return False
        try:
            tokens = shlex.split(command)
        except ValueError:
            return False
        expected = [
            "--config",
            str(self.router_config),
            "--host",
            "127.0.0.1",
            "--port",
            str(self.profile.port),
        ]
        if not tokens:
            return False
        executable = Path(tokens[0])
        if tokens[0] != "litellm" and (not executable.is_absolute() or executable.name != "litellm"):
            return False
        return tokens == [tokens[0], *expected]

    def _router_command(self) -> list[str]:
        command = self._command_path("litellm")
        if command is None:
            raise OpenCodeProfileError('litellm is required. Install it with: uv tool install "litellm[proxy]"')
        return [
            command,
            "--config",
            str(self.router_config),
            "--host",
            "127.0.0.1",
            "--port",
            str(self.profile.port),
        ]

    def _cleanup_failed_start(self, pid: int, *, terminate: bool) -> None:
        if terminate:
            try:
                self._kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        if self._read_pid() == pid:
            self.pid_file.unlink(missing_ok=True)
        self.log_file.unlink(missing_ok=True)

    def _wait_for_router(self, pid: int, label: str, *, cleanup_on_failure: bool = False) -> None:
        for _ in range(30):
            if self.router_healthy():
                return
            if not self.process_is_alive(pid):
                if cleanup_on_failure:
                    self._cleanup_failed_start(pid, terminate=False)
                    raise OpenCodeProfileError(f"{label} LiteLLM router exited during startup; state was cleaned up.")
                raise OpenCodeProfileError(f"{label} LiteLLM router exited. See {self.log_file}.")
            self._sleep(1)
        if cleanup_on_failure:
            self._cleanup_failed_start(pid, terminate=True)
            raise OpenCodeProfileError(f"{label} LiteLLM router did not become healthy during startup; state was cleaned up.")
        raise OpenCodeProfileError(f"{label} LiteLLM router did not become healthy. See {self.log_file}.")

    def start_router(self, environment: dict[str, str]) -> None:
        """Reuse or start the profile router after verifying ownership."""
        label = self.profile.name.capitalize()
        if self.router_healthy():
            if self.router_pid_is_ours():
                return
            raise OpenCodeProfileError(
                f"{label} router port {self.profile.port} is occupied by an unrelated process; refusing to adopt it."
            )
        if self.router_pid_is_ours():
            pid = self._read_pid()
            assert pid is not None
            self._wait_for_router(pid, label)
            return
        if self.router_port_is_open():
            raise OpenCodeProfileError(
                f"{label} router port {self.profile.port} is occupied by an unrelated process; refusing to start LiteLLM."
            )
        command = self._router_command()
        self._ensure_state()
        with self.log_file.open("ab") as log_file:
            process = self._popen(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                env=environment,
            )
        self.pid_file.write_text(f"{process.pid}\n")
        self._wait_for_router(process.pid, label, cleanup_on_failure=True)

    def validate_work_account(self) -> None:
        """Require an owner-controlled work Copilot directory and account marker."""
        copilot = self.state_root / "copilot"
        marker = copilot / "account"
        try:
            owner_matches = copilot.stat().st_uid == os.getuid()
        except OSError:
            owner_matches = False
        if not copilot.is_dir() or copilot.is_symlink() or not owner_matches:
            raise OpenCodeProfileError(
                f"Work Copilot state is not configured. Create {copilot} as a work-owned token directory."
            )
        try:
            marker_owner_matches = marker.stat().st_uid == os.getuid()
            marker_value = marker.read_text().strip()
        except OSError:
            marker_owner_matches = False
            marker_value = ""
        if marker.is_symlink() or not marker.is_file() or not marker_owner_matches or marker_value != "TuckerBeck_mcgraw":
            raise OpenCodeProfileError(
                f"Work Copilot account marker is missing or mismatched. Set {marker} to TuckerBeck_mcgraw after work authentication."
            )

    def launch(self, arguments: Sequence[str], tier: str = "light", *, explicit_cli_premium: bool = False) -> None:
        """Start the profile router and replace this process with OpenCode."""
        validate_tier(tier)
        self._ensure_state()
        if self.profile.requires_work_account:
            self.validate_work_account()
        environment = self.environment_for(tier, explicit_cli_premium=explicit_cli_premium)
        environment["OPENCODE_ROUTER_KEY"] = self._router_key()
        self.start_router(environment)
        argv = ["opencode", *arguments]
        self._execvpe("opencode", argv, environment)

    def status(self) -> None:
        """Print profile lifecycle details without printing secrets."""
        print(
            f"profile: {self.profile.name}\n"
            f"endpoint: {self.endpoint}\n"
            f"config: {self.open_code_config}\n"
            f"state: {self.state_root}"
        )
        if self.router_healthy() and self.router_pid_is_ours():
            print("router: healthy")
        elif self.router_healthy():
            print("router: healthy but ownership is unverified")
        else:
            print("router: stopped or unhealthy")

    def stop(self) -> None:
        """Stop only a live router whose command belongs to this profile."""
        pid = self._read_pid()
        if pid is not None and self.router_pid_is_ours():
            try:
                self._kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        self.pid_file.unlink(missing_ok=True)


def personal_lifecycle(**kwargs: Any) -> OpenCodeLifecycle:
    """Construct the personal OpenCode lifecycle."""
    return OpenCodeLifecycle(PERSONAL_PROFILE, **kwargs)
