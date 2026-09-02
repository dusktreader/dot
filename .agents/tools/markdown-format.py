#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys


def main() -> int:
    """Delegate wrapper arguments to the repository CLI."""
    entry_cwd = Path.cwd()
    repo = next((parent for parent in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents] if (parent / "pyproject.toml").exists()), None)
    if repo is None:
        print("Could not locate repository", file=sys.stderr)
        return 3
    args = sys.argv[1:]
    command = args[0] if args else "--help"
    operands = [str((entry_cwd / Path(arg)).resolve()) if not Path(arg).is_absolute() else arg for arg in args[1:]]
    return subprocess.run(["uv", "run", "--project", str(repo), "dt", "markdown", command, *operands], cwd=entry_cwd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
