"""Tests for credentials commands."""

import tempfile
import pytest
from typer.testing import CliRunner

from dot_tools.cli.main import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_home():
    """Create a temporary home directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_creds_bare_invocation_shows_help(runner, temp_home, monkeypatch):
    """Test that bare dt creds invocation shows help and exits zero."""
    monkeypatch.setenv("HOME", temp_home)
    result = runner.invoke(cli, ["creds"])
    assert result.exit_code == 0
    assert "Manage personal credentials" in result.stdout
    assert "fetch" in result.stdout
    assert "set" in result.stdout


def test_creds_help_matches_bare_invocation(runner, temp_home, monkeypatch):
    """Test that 'dt creds --help' output matches bare 'dt creds' output."""
    monkeypatch.setenv("HOME", temp_home)
    result_bare = runner.invoke(cli, ["creds"])
    result_help = runner.invoke(cli, ["creds", "--help"])
    assert result_bare.stdout == result_help.stdout


def test_creds_fetch_missing_key(runner, temp_home, monkeypatch):
    """Test that fetching a missing key exits non-zero."""
    monkeypatch.setenv("HOME", temp_home)
    result = runner.invoke(cli, ["creds", "fetch", "nonexistent_key"])
    assert result.exit_code == 1
    assert "error" in result.stdout or "error" in result.stderr


def test_creds_fetch_empty_value(runner, temp_home, monkeypatch):
    """Test that fetching an empty value exits non-zero."""
    monkeypatch.setenv("HOME", temp_home)
    # First, jira_api_key should be empty by default
    result = runner.invoke(cli, ["creds", "fetch", "jira_api_key"])
    assert result.exit_code == 1
    assert "empty or not configured" in result.stdout or "empty or not configured" in result.stderr


def test_creds_fetch_placeholder_value(runner, temp_home, monkeypatch):
    """Test that fetching a placeholder value exits non-zero."""
    monkeypatch.setenv("HOME", temp_home)
    # Set a placeholder value first
    result = runner.invoke(cli, ["creds", "set", "jira_api_key", "PLACEHOLDER_JIRA_API_KEY"])
    assert result.exit_code == 0
    
    # Now try to fetch it
    result = runner.invoke(cli, ["creds", "fetch", "jira_api_key"])
    assert result.exit_code == 1
    assert "empty or not configured" in result.stdout or "empty or not configured" in result.stderr


def test_creds_fetch_valid_value(runner, temp_home, monkeypatch):
    """Test that fetching a valid value succeeds and prints to stdout."""
    monkeypatch.setenv("HOME", temp_home)
    # Set a valid value
    result = runner.invoke(cli, ["creds", "set", "jira_api_key", "my_secret_value"])
    assert result.exit_code == 0
    
    # Now fetch it
    result = runner.invoke(cli, ["creds", "fetch", "jira_api_key"])
    assert result.exit_code == 0
    assert "my_secret_value" in result.stdout


def test_creds_set_valid_key(runner, temp_home, monkeypatch):
    """Test that setting a valid key succeeds."""
    monkeypatch.setenv("HOME", temp_home)
    result = runner.invoke(cli, ["creds", "set", "gmail_client_id", "test_token"])
    assert result.exit_code == 0
    assert "credential 'gmail_client_id' updated" in result.stdout
    assert "test_token" not in result.stdout  # Value should not be echoed


def test_creds_set_invalid_key(runner, temp_home, monkeypatch):
    """Test that setting an invalid key exits non-zero."""
    monkeypatch.setenv("HOME", temp_home)
    result = runner.invoke(cli, ["creds", "set", "invalid_key", "value"])
    assert result.exit_code == 1
    assert "unknown credential key" in result.stdout or "unknown credential key" in result.stderr


def test_creds_set_persists_to_disk(runner, temp_home, monkeypatch):
    """Test that set values are persisted and retrievable in new instance."""
    monkeypatch.setenv("HOME", temp_home)
    # Set a value
    result = runner.invoke(cli, ["creds", "set", "gmail_client_secret", "my_gmail_client_secret"])
    assert result.exit_code == 0
    
    # Create a new CLI runner to simulate a new session
    new_runner = CliRunner()
    monkeypatch.setenv("HOME", temp_home)
    result = new_runner.invoke(cli, ["creds", "fetch", "gmail_client_secret"])
    assert result.exit_code == 0
    assert "my_gmail_client_secret" in result.stdout


def test_creds_fetch_help_includes_warning(runner, temp_home, monkeypatch):
    """Test that creds fetch help includes security warning."""
    monkeypatch.setenv("HOME", temp_home)
    result = runner.invoke(cli, ["creds", "fetch", "--help"])
    assert result.exit_code == 0
    assert "WARNING" in result.stdout or "warning" in result.stdout or "secret" in result.stdout


def test_creds_set_help_includes_warning(runner, temp_home, monkeypatch):
    """Test that creds set help includes non-echo warning."""
    monkeypatch.setenv("HOME", temp_home)
    result = runner.invoke(cli, ["creds", "set", "--help"])
    assert result.exit_code == 0
    assert "WARNING" in result.stdout or "warning" in result.stdout or "echo" in result.stdout


def test_creds_set_preserves_unrelated_keys(runner, temp_home, monkeypatch):
    """Test that setting one credential preserves other credentials."""
    monkeypatch.setenv("HOME", temp_home)
    
    # Set first credential
    result1 = runner.invoke(cli, ["creds", "set", "gmail_client_id", "client_id_value"])
    assert result1.exit_code == 0
    
    # Set second credential
    result2 = runner.invoke(cli, ["creds", "set", "jira_api_key", "jira_key_value"])
    assert result2.exit_code == 0
    
    # Verify first credential still exists
    result3 = runner.invoke(cli, ["creds", "fetch", "gmail_client_id"])
    assert result3.exit_code == 0
    assert result3.stdout.strip() == "client_id_value"
    
    # Verify second credential exists
    result4 = runner.invoke(cli, ["creds", "fetch", "jira_api_key"])
    assert result4.exit_code == 0
    assert result4.stdout.strip() == "jira_key_value"
