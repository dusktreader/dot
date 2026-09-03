#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# ///

from pathlib import Path
import subprocess
import sys


def main() -> int:
    """Delegate wrapper arguments to the repository CLI."""
    entry_cwd = Path.cwd()
    script_path = Path(__file__).resolve()
    repo = next((parent for parent in [script_path.parent, *script_path.parents] if (parent / "pyproject.toml").exists()), None)
    if repo is None:
        print("Could not locate repository", file=sys.stderr)
        return 2
    args = sys.argv[1:]
    command = args[0] if args and args[0] in {"format", "check"} else "--help"
    operands = [str((entry_cwd / Path(arg)).absolute()) if not Path(arg).is_absolute() else arg for arg in args[1:]]
    child_args = ["uv", "run", "--project", str(repo), "dt", "markdown", command, *operands]
    if command == "--help":
        child_args = ["uv", "run", "--project", str(repo), "dt", "markdown", "--help"]
    return subprocess.run(child_args, cwd=entry_cwd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
