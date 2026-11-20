from typer.testing import CliRunner

from dot_tools.cli.main import cli

URL = "postgresql://u:p%40ss@db.example.com:5432/app"


def test_db_lifecycle(runner: CliRunner):
    assert "No databases" in runner.invoke(cli, ["db", "list"]).output
    r = runner.invoke(cli, ["db", "configure", "dev", URL, "--namespace", "ns", "-p", "prof"])
    assert r.exit_code == 0, r.output
    out = runner.invoke(cli, ["db", "list"]).output
    assert "dev" in out and "prof" in out and "p%40ss" not in out
    assert runner.invoke(cli, ["db", "configure", "dev", URL]).exit_code != 0
    assert runner.invoke(cli, ["db", "update", "dev", URL + "x"]).exit_code == 0
    assert runner.invoke(cli, ["db", "remove", "dev"]).exit_code == 0
    assert "No databases" in runner.invoke(cli, ["db", "list"]).output


def test_bad_url(runner: CliRunner):
    assert runner.invoke(cli, ["db", "configure", "x", "http://nope"]).exit_code != 0


def test_configure_prompts_for_components(runner: CliRunner):
    r = runner.invoke(cli, ["db", "configure", "dev"], input="db.example.com\n\napp\nme\np@ss\n")
    assert r.exit_code == 0, r.output
    from dot_tools import db_tools

    assert db_tools.get_db("dev").url.get_secret_value() == "postgresql://me:p%40ss@db.example.com:5432/app"


def test_update_prompts_prepopulated(runner: CliRunner):
    from dot_tools import db_tools

    runner.invoke(cli, ["db", "configure", "dev", URL])
    # accept all defaults except the database name
    r = runner.invoke(cli, ["db", "update", "dev"], input="\n\nother\n\n\n")
    assert r.exit_code == 0, r.output
    assert db_tools.get_db("dev").url.get_secret_value() == "postgresql://u:p%40ss@db.example.com:5432/other"


def test_login_creates_and_cleans_up_pod(runner: CliRunner, monkeypatch):
    import subprocess
    from dot_tools import db_tools

    calls: list[list[str]] = []

    class FakeProc:
        def poll(self): return None
        def terminate(self): calls.append(["terminate"])
        def wait(self, timeout=None): return 0

    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: calls.append(cmd) or subprocess.CompletedProcess(cmd, 0, "", ""))
    monkeypatch.setattr(subprocess, "Popen", lambda cmd, **kw: calls.append(cmd) or FakeProc())
    monkeypatch.setattr(db_tools, "_wait_for_port", lambda port, proc: None)

    runner.invoke(cli, ["db", "configure", "dev", URL, "-n", "ns"])
    r = runner.invoke(cli, ["db", "login", "dev"])
    assert r.exit_code == 0, r.output
    verbs = [c[3] if c[0] == "kubectl" else c[0] for c in calls]
    assert verbs == ["run", "wait", "port-forward", "pgcli", "terminate", "delete"]
