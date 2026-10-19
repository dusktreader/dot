import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import git
import typer
from auto_name_enum import AutoNameEnum, auto
from inflection import parameterize

from dot_tools.exceptions import DotError
from dot_tools.git_tools import _run_git


class WorktreeError(DotError):
    pass

class BranchType(AutoNameEnum):
    feat = auto()
    fix = auto()
    docs = auto()
    style = auto()
    refactor = auto()
    perf = auto()
    test = auto()
    build = auto()
    ci = auto()
    chore = auto()
    revert = auto()


@dataclass(frozen=True)
class Worktree:
    path: Path
    branch: str


def project_root(path: Path | None = None) -> Path:
    with WorktreeError.handle_errors(
        "Current directory is not inside a Git repository",
        handle_exc_class=(git.InvalidGitRepositoryError, git.NoSuchPathError),
    ):
        repo = git.Repo(path or Path.cwd(), search_parent_directories=True)

    repo_root = Path(
        WorktreeError.enforce_defined(repo.working_tree_dir, "Git repository has no working tree")
    ).resolve()
    common_dir = Path(repo.git.rev_parse("--git-common-dir"))
    if not common_dir.is_absolute():
        common_dir = repo_root / common_dir
    return common_dir.resolve().parent


def parameterize_summary(summary: str) -> str:
    return parameterize(summary.lower())[:80].rstrip("-")


def build_branch_name(branch_type: BranchType, summary: str, ticket: str | None = None) -> str:
    slug = parameterize_summary(summary)
    DotError.require_condition(slug, "Summary must contain at least one letter or number")

    if ticket:
        ticket = ticket.strip()
        DotError.require_condition(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", ticket),
            "Ticket must contain only letters, numbers, dots, underscores, and hyphens"
        )
        slug = f"{ticket}--{slug}"

    return f"{branch_type.value}/{slug}"


def list_worktrees(root: Path) -> list[Worktree]:
    worktree_root = (root / ".worktrees").resolve()
    output = _run_git(root, "worktree", "list", "--porcelain")
    entries: list[Worktree] = []
    path: Path | None = None
    branch: str | None = None

    def append_entry() -> None:
        if path is not None and branch is not None:
            resolved_path = path.resolve()
            if resolved_path.is_relative_to(worktree_root):
                entries.append(Worktree(resolved_path, branch))

    for line in (*output.splitlines(), ""):
        if line.startswith("worktree "):
            append_entry()
            path = Path(line.removeprefix("worktree "))
            branch = None
        elif line.startswith("branch refs/heads/"):
            branch = line.removeprefix("branch refs/heads/")
        elif not line:
            append_entry()
            path = None
            branch = None

    return entries


def create_worktree(branch: str) -> Worktree:
    root = project_root()
    path = root / ".worktrees" / branch
    path.parent.mkdir(parents=True, exist_ok=True)
    _run_git(root, "worktree", "add", "-b", branch, str(path))
    return Worktree(path.resolve(), branch)


def matching_worktrees(query: str, worktrees: list[Worktree]) -> list[Worktree]:
    normalized_query = re.sub(r"[^a-z0-9]", "", query.casefold())
    if not normalized_query:
        raise DotError("Search text must contain at least one letter or number")

    def matches(worktree: Worktree) -> bool:
        candidate = re.sub(r"[^a-z0-9]", "", worktree.branch.casefold())
        return normalized_query in candidate or _is_subsequence(normalized_query, candidate)

    return [worktree for worktree in worktrees if matches(worktree)]


def _is_subsequence(query: str, candidate: str) -> bool:
    position = 0
    for char in candidate:
        if char == query[position]:
            position += 1
            if position == len(query):
                return True
    return False


def choose_worktree(worktrees: list[Worktree]) -> Worktree:
    if len(worktrees) == 1:
        return worktrees[0]

    fzf = shutil.which("fzf")
    if fzf:
        result = subprocess.run(
            [fzf],
            input="\n".join(worktree.branch for worktree in worktrees) + "\n",
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise typer.Exit(code=1)
        selected_branch = result.stdout.strip()
        for worktree in worktrees:
            if worktree.branch == selected_branch:
                return worktree
        raise DotError("The worktree picker returned an unknown selection")

    typer.echo("Select a worktree:")
    for index, worktree in enumerate(worktrees, 1):
        typer.echo(f"{index}. {worktree.branch}")
    while True:
        selection = typer.prompt("Selection", type=int)
        if 1 <= selection <= len(worktrees):
            return worktrees[selection - 1]
        typer.echo(f"Enter a number between 1 and {len(worktrees)}")


def find_worktree(query: str, root: Path | None = None) -> Worktree:
    matches = matching_worktrees(query, list_worktrees(root or project_root()))
    if not matches:
        raise DotError(f"No worktree matches {query!r}")
    return choose_worktree(matches)


def remove_worktree(worktree: Worktree, *, delete_branch: bool = False) -> None:
    root = project_root()
    _run_git(root, "worktree", "remove", str(worktree.path))
    if delete_branch:
        _run_git(root, "branch", "-d", worktree.branch)


def navigate_to(path: Path) -> None:
    destination = path.resolve()
    navigation_file = os.environ.get("DT_NAVIGATION_FILE")
    if navigation_file:
        Path(navigation_file).write_text(f"{destination}\n")
    typer.echo(f"Directory: {destination}")
