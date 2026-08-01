#!/usr/bin/env python3
"""Create a repository-local agent branch and worktree."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def branch_exists(repository: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repository), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
    )
    return result.returncode == 0


def worktree_paths(repository: Path) -> set[Path]:
    output = run_git(repository, "worktree", "list", "--porcelain")
    return {
        Path(line.removeprefix("worktree ")).resolve()
        for line in output.splitlines()
        if line.startswith("worktree ")
    }


def next_branch(repository: Path, candidate: str) -> str:
    if not branch_exists(repository, candidate):
        return candidate

    suffix = 2
    while branch_exists(repository, f"{candidate}-{suffix:02d}"):
        suffix += 1
    return f"{candidate}-{suffix:02d}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--parent-worktree", type=Path, required=True)
    parser.add_argument("--parent-branch", required=True)
    parser.add_argument("--parent-base", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--type", dest="branch_type", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--slug", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = args.repository.resolve()
    parent_worktree = args.parent_worktree.resolve()

    if not (repository / ".git").exists() and not (repository / ".git").is_file():
        raise SystemExit(f"Not a Git worktree: {repository}")
    if parent_worktree != repository:
        raise SystemExit("The parent worktree must be the repository root passed to --repository.")

    recorded_root = Path(run_git(parent_worktree, "rev-parse", "--show-toplevel")).resolve()
    if recorded_root != repository:
        raise SystemExit(f"Repository root mismatch: git reports {recorded_root}")

    local_worktrees = repository / ".worktrees"
    local_worktrees.mkdir(exist_ok=True)
    if not local_worktrees.is_dir():
        raise SystemExit(f"Worktree path is not a directory: {local_worktrees}")

    if args.parent_branch in {"main", "master"}:
        requested_branch = f"{args.branch_type}/{args.task_id}--{args.slug}"
        audit_branch = False
    else:
        requested_branch = f"{args.parent_branch}--agents-{args.workflow}"
        audit_branch = True

    agent_branch = next_branch(repository, requested_branch)
    agent_path = (local_worktrees / agent_branch).resolve()
    if agent_path in worktree_paths(repository) or agent_path.exists():
        raise SystemExit(f"Agent worktree path already exists: {agent_path}")

    run_git(repository, "branch", agent_branch, args.parent_base)
    try:
        run_git(repository, "worktree", "add", str(agent_path), agent_branch)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "-C", str(repository), "branch", "-D", agent_branch], check=False)
        raise

    print(
        json.dumps(
            {
                "repository": str(repository),
                "parent_worktree": str(parent_worktree),
                "parent_branch": args.parent_branch,
                "parent_base": args.parent_base,
                "workflow": args.workflow,
                "agent_branch": agent_branch,
                "agent_worktree": str(agent_path),
                "audit_branch": audit_branch,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
