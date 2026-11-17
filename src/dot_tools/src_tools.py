import shutil
import subprocess
from pathlib import Path
from typing import cast

import typer

from dot_tools.exceptions import DotError
from dot_tools.settings import Settings, SrcMode
from dot_tools.settings_manager import dot_settings_manager
from dot_tools.worktree_tools import _matches_search, _normalize_search_text, navigate_to


def src_settings():
    return cast(Settings, dot_settings_manager().settings_instance).src


def default_mode() -> SrcMode:
    return src_settings().default_mode


def mode_root(mode: SrcMode) -> Path:
    return Path(getattr(src_settings(), f"{mode.value}_root")).expanduser()


def matching_folders(query: str, root: Path) -> list[Path]:
    normalized_query = _normalize_search_text(query)
    if not normalized_query:
        raise DotError("Search text must contain at least one letter or number")
    if not root.is_dir():
        raise DotError(f"Source root does not exist: {root}")
    folders = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    return [p for p in folders if _matches_search(normalized_query, p.name)]


def choose_folder(folders: list[Path]) -> Path:
    if len(folders) == 1:
        return folders[0]

    fzf = shutil.which("fzf")
    if fzf:
        result = subprocess.run(
            [fzf],
            input="\n".join(f.name for f in folders) + "\n",
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise typer.Exit(code=1)
        selected = result.stdout.strip()
        for folder in folders:
            if folder.name == selected:
                return folder
        raise DotError("The folder picker returned an unknown selection")

    typer.echo("Select a folder:")
    for index, folder in enumerate(folders, 1):
        typer.echo(f"{index}. {folder.name}")
    while True:
        selection = typer.prompt("Selection", type=int)
        if 1 <= selection <= len(folders):
            return folders[selection - 1]
        typer.echo(f"Enter a number between 1 and {len(folders)}")


def jump_to_folder(mode: SrcMode, query: str) -> None:
    root = mode_root(mode)
    matches = matching_folders(query, root)
    if not matches:
        raise DotError(f"No folder in {root} matches {query!r}")
    navigate_to(choose_folder(matches))


def go_to_root(mode: SrcMode) -> None:
    root = mode_root(mode)
    if not root.is_dir():
        raise DotError(f"Source root does not exist: {root}")
    navigate_to(root)


def list_folders(mode: SrcMode) -> list[Path]:
    root = mode_root(mode)
    if not root.is_dir():
        raise DotError(f"Source root does not exist: {root}")
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))


def current_branch(folder: Path) -> str:
    """Return the checked out branch of a folder, or an empty string if it is not a git repo."""
    if not (folder / ".git").exists():
        return ""
    result = subprocess.run(
        ["git", "-C", str(folder), "branch", "--show-current"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return ""
    return result.stdout.strip() or "(detached)"
