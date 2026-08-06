"""Persistent state for the OpenCode staleness guard."""

import json
import os
from pathlib import Path


def state_path() -> Path:
    """Return the user-local path used to persist file read timestamps."""
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "dot-tools" / "staleness-guard.json"


def _load() -> dict[str, float]:
    try:
        value = json.loads(state_path().read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _save(timestamps: dict[str, float]) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(timestamps, sort_keys=True) + "\n")
    temporary_path.replace(path)


def record_read(file_path: Path) -> None:
    """Record the current mtime of an existing file after OpenCode reads it."""
    try:
        mtime = file_path.stat().st_mtime_ns
    except FileNotFoundError:
        return
    timestamps = _load()
    timestamps[str(file_path.resolve())] = mtime
    _save(timestamps)


def check_before_edit(file_path: Path) -> str | None:
    """Return an error if a file changed since it was recorded, otherwise ``None``."""
    path = str(file_path.resolve())
    timestamps = _load()
    read_mtime = timestamps.get(path)
    if read_mtime is None:
        return None

    try:
        current_mtime = file_path.stat().st_mtime_ns
    except FileNotFoundError:
        return None

    if current_mtime <= read_mtime:
        return None

    del timestamps[path]
    _save(timestamps)
    return (
        f"File has been modified since it was last read: {file_path}\n"
        f"Read mtime: {read_mtime}\n"
        f"Modified mtime: {current_mtime}\n"
        "Re-read the file before editing."
    )
