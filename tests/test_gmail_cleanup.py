"""Tests for Gmail credential retrieval."""

import importlib.util
from pathlib import Path
from subprocess import CompletedProcess


def load_gmail_cleanup_module():
    """Load the Gmail tool module from its tracked tool path."""
    tool_path = Path(__file__).parents[1] / ".config/opencode/tools/gmail_cleanup.py"
    spec = importlib.util.spec_from_file_location("gmail_cleanup", tool_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_gmail_creds_fetches_both_dt_credentials(monkeypatch):
    """Verify Gmail OAuth credentials are read through dt creds."""
    gmail_cleanup = load_gmail_cleanup_module()
    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        value = "gmail-client-id" if command[-1] == "gmail_client_id" else "gmail-client-secret"
        return CompletedProcess(command, 0, stdout=f"{value}\n", stderr="")

    monkeypatch.setattr(gmail_cleanup.subprocess, "run", fake_run)

    assert gmail_cleanup.load_gmail_creds() == ("gmail-client-id", "gmail-client-secret")
    assert commands == [
        ["dt", "creds", "fetch", "gmail_client_id"],
        ["dt", "creds", "fetch", "gmail_client_secret"],
    ]
