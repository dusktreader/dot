import contextlib
import os
import secrets
import socket
import subprocess
import time
from collections.abc import Iterator
from typing import cast
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from loguru import logger

from dot_tools.constants import Status
from dot_tools.exceptions import DotError
from dot_tools.settings import DbEntry, Settings
from dot_tools.settings_manager import dot_settings_manager
from dot_tools.spinner import spinner

SOCAT_IMAGE = "alpine/socat"
FORWARD_TIMEOUT = 30


def _load() -> tuple:
    sm = dot_settings_manager()
    return sm, dict(cast(Settings, sm.settings_instance).dbs)


def _save(sm, dbs: dict[str, DbEntry]):
    sm.update(dbs=dbs)
    sm.save()


def validate_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("postgres", "postgresql") or not parts.hostname:
        raise DotError("URL must look like postgresql://USER:PASS@HOST:PORT/DBNAME")
    return url


def build_url(user: str, password: str, host: str, port: int, dbname: str) -> str:
    userinfo = quote(user, safe="")
    if password:
        userinfo += ":" + quote(password, safe="")
    return f"postgresql://{userinfo}@{host}:{port}/{quote(dbname, safe='')}"


def list_dbs() -> dict[str, DbEntry]:
    return _load()[1]


def get_db(alias: str) -> DbEntry:
    dbs = list_dbs()
    if alias not in dbs:
        raise DotError(f"No database with alias {alias!r}. Use `dt db configure {alias}` first")
    return dbs[alias]


def add_db(alias: str, url: str, namespace: str | None, profile: str | None = None):
    sm, dbs = _load()
    if alias in dbs:
        raise DotError(f"Alias {alias!r} already exists. Use `dt db update {alias}` to change it")
    dbs[alias] = DbEntry(url=validate_url(url), namespace=namespace, profile=profile)  # type: ignore[arg-type]
    _save(sm, dbs)


def update_db(alias: str, url: str | None, namespace: str | None, profile: str | None = None):
    sm, dbs = _load()
    if alias not in dbs:
        raise DotError(f"No database with alias {alias!r}")
    entry = dbs[alias]
    if url is not None:
        entry = entry.model_copy(update={"url": validate_url(url)})
    if namespace is not None:
        entry = entry.model_copy(update={"namespace": namespace})
    if profile is not None:
        entry = entry.model_copy(update={"profile": profile})
    dbs[alias] = entry
    _save(sm, dbs)


def remove_db(alias: str):
    sm, dbs = _load()
    if alias not in dbs:
        raise DotError(f"No database with alias {alias!r}")
    del dbs[alias]
    _save(sm, dbs)


def mask_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.password is None:
        return url
    host = parts.netloc.rsplit("@", 1)[1]
    user = parts.username or ""
    return urlunsplit(parts._replace(netloc=f"{user}:***@{host}"))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _kubectl(namespace: str | None) -> list[str]:
    return ["kubectl", *(["-n", namespace] if namespace else [])]


def _wait_for_port(port: int, proc: subprocess.Popen):
    deadline = time.monotonic() + FORWARD_TIMEOUT
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise DotError("kubectl port-forward exited unexpectedly")
        with contextlib.suppress(OSError):
            socket.create_connection(("127.0.0.1", port), timeout=1).close()
            return
        time.sleep(0.2)
    raise DotError("Timed out waiting for port-forward")


@contextlib.contextmanager
def forwarded_url(url: str, namespace: str | None, profile: str | None = None) -> Iterator[str]:
    """Create a temporary socat pod, forward a local port to it, and yield a url using the local port."""
    parts = urlsplit(url)
    remote_port = parts.port or 5432
    pod = f"pgfwd-{secrets.token_hex(3)}"
    kube = _kubectl(namespace)
    env = {**os.environ, "AWS_PROFILE": profile} if profile else None
    forwarder: subprocess.Popen | None = None
    pod_requested = False
    try:
        with spinner(f"Connecting to {parts.hostname} via {pod}", context_level="DEBUG"):
            logger.debug(f"Creating pod {pod} in {namespace or 'current namespace'}", status=Status.CHECK)
            pod_requested = True
            run = subprocess.run(
                [
                    *kube, "run", pod, f"--image={SOCAT_IMAGE}", "--restart=Never", "--",
                    "tcp-listen:5432,fork,reuseaddr", f"tcp-connect:{parts.hostname}:{remote_port}",
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            if run.returncode:
                raise DotError(f"Failed to create pod: {run.stderr.strip()}")
            logger.debug(f"Pod {pod} created", status=Status.CONFIRM)

            logger.debug("Waiting for pod to become ready", status=Status.CHECK)
            wait = subprocess.run(
                [*kube, "wait", "--for=condition=Ready", f"pod/{pod}", f"--timeout={FORWARD_TIMEOUT * 2}s"],
                capture_output=True,
                text=True,
                env=env,
            )
            if wait.returncode:
                raise DotError(f"Pod never became ready: {wait.stderr.strip()}")
            logger.debug("Pod is ready", status=Status.CONFIRM)

            local_port = _free_port()
            logger.debug(f"Starting port-forward on localhost:{local_port}", status=Status.CHECK)
            forwarder = subprocess.Popen(
                [*kube, "port-forward", f"pod/{pod}", f"{local_port}:5432"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            _wait_for_port(local_port, forwarder)
            logger.debug(f"Port-forward is accepting connections on localhost:{local_port}", status=Status.CONFIRM)

        userinfo = ""
        if parts.username is not None:
            userinfo = quote(unquote(parts.username), safe="")
            if parts.password is not None:
                userinfo += ":" + quote(unquote(parts.password), safe="")
            userinfo += "@"
        yield urlunsplit(parts._replace(netloc=f"{userinfo}localhost:{local_port}"))
    finally:
        with spinner("Cleaning up", context_level="DEBUG"):
            if forwarder is not None:
                logger.debug("Stopping port-forward", status=Status.CHECK)
                forwarder.terminate()
                try:
                    forwarder.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    forwarder.kill()
                logger.debug("Port-forward stopped", status=Status.CONFIRM)
            if pod_requested:
                logger.debug(f"Deleting pod {pod}", status=Status.CHECK)
                subprocess.run(
                    [*kube, "delete", "pod", pod, "--now", "--ignore-not-found", "--wait=false"],
                    capture_output=True,
                    env=env,
                )
                logger.debug(f"Pod {pod} deleted", status=Status.CONFIRM)


def login(alias: str, namespace: str | None, profile: str | None = None) -> int:
    entry = get_db(alias)
    ns = namespace or entry.namespace
    with forwarded_url(entry.url.get_secret_value(), ns, profile or entry.profile) as local_url:
        try:
            return subprocess.run(["pgcli", local_url]).returncode
        except FileNotFoundError as err:
            raise DotError("pgcli is not installed") from err
        except KeyboardInterrupt:
            return 130
