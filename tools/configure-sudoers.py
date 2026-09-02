#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["py-buzz>=8.0", "rich>=14.0"]
# ///
"""Install and validate the dotfiles passwordless-sudo configuration."""

import argparse
import os
import platform
import pwd
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

from buzz import Buzz
from rich.console import Console
from rich.text import Text


SUDOERS_PATH = Path("/etc/sudoers")
INCLUDE_DIR = Path("/etc/sudoers.d")
MANAGED_PATH = INCLUDE_DIR / "90-dotfiles"
ROOT_UID = 0
CANONICAL_INCLUDE = "#includedir /etc/sudoers.d"
INCLUDE_DIRECTIVE = re.compile(r"^\s*(?:#includedir|@includedir)\s+(\S+)(?:\s+#.*)?\s*$")
console = Console(stderr=True)


class ConfigurationError(Buzz):
    """Report a configuration precondition, validation, or transaction failure."""


def fail(message: str) -> int:
    """Print a clear configuration error and return a command failure status."""
    console.print(Text("Error", style="red"), Text(f": configure-sudoers: {message}"))
    return 1


def run_command(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Run a bounded noninteractive validation command."""
    try:
        return subprocess.run(arguments, check=False, capture_output=True, timeout=30)
    except FileNotFoundError as error:
        raise ConfigurationError(f"required command is unavailable: {arguments[0]}") from error
    except OSError as error:
        raise ConfigurationError(f"could not run {' '.join(arguments)}: {error}") from error
    except subprocess.TimeoutExpired as error:
        raise ConfigurationError(f"command timed out: {' '.join(arguments)}") from error


def validate_with_visudo(path: Path | None = None) -> None:
    """Validate the live or candidate sudoers configuration without editing it."""
    arguments = ["visudo", "-c"] if path is None else ["visudo", "-c", "-f", str(path)]
    result = run_command(arguments)
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()
        raise ConfigurationError(f"visudo rejected {path or SUDOERS_PATH}: {detail or 'invalid configuration'}")


def require_safe_path(
    path: Path, expected_type: int, description: str, *, allow_missing: bool = False
) -> os.stat_result | None:
    """Require an existing non-symlink root-owned path with no group or other write permission."""
    try:
        details = path.lstat()
    except FileNotFoundError:
        if allow_missing:
            return None
        raise ConfigurationError(f"required {description} does not exist ({path})")
    except OSError as error:
        raise ConfigurationError(f"could not inspect {description} ({path}): {error}") from error
    is_symlink = stat.S_ISLNK(details.st_mode)
    with ConfigurationError.check_expressions(f"unsafe {description} ({path})") as check:
        check(not is_symlink, "symlinks are not allowed")
        if not is_symlink:
            if expected_type == stat.S_IFREG:
                check(stat.S_ISREG(details.st_mode), "expected a regular file")
            elif expected_type == stat.S_IFDIR:
                check(stat.S_ISDIR(details.st_mode), "expected a directory")
            check(details.st_uid == ROOT_UID, "it must be root-owned")
            check(not details.st_mode & 0o022, "it must not be group- or world-writable")
    return details


def ensure_include_dir() -> None:
    """Create the include directory or verify its existing safe metadata."""
    details = require_safe_path(INCLUDE_DIR, stat.S_IFDIR, "sudoers include directory", allow_missing=True)
    if details is None:
        created = False
        try:
            INCLUDE_DIR.mkdir(mode=0o755)
            created = True
            os.chown(INCLUDE_DIR, ROOT_UID, -1)
            os.chmod(INCLUDE_DIR, 0o755)
            details = require_safe_path(INCLUDE_DIR, stat.S_IFDIR, "sudoers include directory")
        except (ConfigurationError, OSError) as error:
            cleanup_error = remove_empty_directory(INCLUDE_DIR) if created else None
            message = f"could not create sudoers include directory: {error}"
            if cleanup_error is not None:
                message += f"; could not remove newly created include directory: {cleanup_error}"
            raise ConfigurationError(message) from error
        assert details is not None


def invoking_username() -> str:
    """Resolve the original invoking account from sudo metadata or the current UID."""
    sudo_uid = os.environ.get("SUDO_UID")
    sudo_user = os.environ.get("SUDO_USER")
    try:
        if sudo_uid:
            return pwd.getpwuid(int(sudo_uid)).pw_name
        if sudo_user:
            return pwd.getpwnam(sudo_user).pw_name
        return pwd.getpwuid(os.getuid()).pw_name
    except (KeyError, ValueError, OverflowError, OSError) as error:
        raise ConfigurationError("could not resolve the invoking account") from error


def desired_rule() -> bytes:
    """Return the exact managed rule for the invoking account."""
    return f"{invoking_username()} ALL=(ALL) NOPASSWD: ALL\n".encode()


def rewrite_includes(content: bytes) -> bytes:
    """Collapse owned active includes and retain all unrelated sudoers bytes."""
    lines = content.splitlines(keepends=True)
    result: list[bytes] = []
    found = False
    for line in lines:
        if is_active_target_include(line):
            if not found:
                result.append((CANONICAL_INCLUDE + "\n").encode())
                found = True
            continue
        result.append(line)
    if not found:
        if result and not result[-1].endswith((b"\n", b"\r")):
            result.append(b"\n")
        result.append((CANONICAL_INCLUDE + "\n").encode())
    return b"".join(result)


def is_active_target_include(line: bytes) -> bool:
    """Return whether a line actively includes the configured sudoers directory."""
    match = INCLUDE_DIRECTIVE.match(line.decode(errors="surrogateescape").rstrip("\r\n"))
    if match is None:
        return False
    target = Path(match.group(1))
    if target == Path("/etc/sudoers.d"):
        return True
    if platform.system() != "Darwin" or target != Path("/private/etc/sudoers.d"):
        return False
    try:
        return target.resolve() == INCLUDE_DIR.resolve()
    except (OSError, shutil.Error) as error:
        raise ConfigurationError(f"could not resolve sudoers include directory: {error}") from error


def write_temp(directory: Path, content: bytes, mode: int, uid: int = ROOT_UID, gid: int = -1) -> Path:
    """Write validated candidate bytes to a same-directory temporary file."""
    try:
        descriptor, name = tempfile.mkstemp(prefix=".90-dotfiles.", dir=directory)
    except OSError as error:
        raise ConfigurationError(f"could not create temporary file in {directory}: {error}") from error
    path = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.chmod(path, mode)
        os.chown(path, uid, gid)
    except OSError as error:
        cleanup_error = remove_best_effort(path)
        message = f"could not write temporary file in {directory}: {error}"
        if cleanup_error is not None:
            message += f"; could not clean up: {cleanup_error}"
        raise ConfigurationError(message) from error
    return path


def write_file(path: Path, content: bytes, mode: int) -> None:
    """Write a candidate file and apply its mode, converting OS failures to configuration errors."""
    try:
        path.write_bytes(content)
        os.chmod(path, mode)
    except OSError as error:
        raise ConfigurationError(f"could not write candidate file {path}: {error}") from error


def remove_best_effort(path: Path) -> str | None:
    """Remove a temporary path and return a description when cleanup fails."""
    try:
        path.unlink(missing_ok=True)
    except OSError as error:
        return f"{path}: {error}"
    return None


def remove_tree_best_effort(path: Path) -> str | None:
    """Remove a temporary directory and return a description when cleanup fails."""
    try:
        shutil.rmtree(path)
    except OSError as error:
        return f"{path}: {error}"
    return None


def cleanup_candidates(candidates: tuple[Path | None, ...], candidate_dir: Path | None) -> list[str]:
    """Remove candidate files and their directory, returning paths that could not be removed."""
    failures = [failure for candidate in candidates if candidate is not None
                for failure in [remove_best_effort(candidate)] if failure is not None]
    if candidate_dir is not None:
        failure = remove_tree_best_effort(candidate_dir)
        if failure is not None:
            failures.append(failure)
    return failures


def remove_empty_directory(path: Path) -> str | None:
    """Remove a newly created empty directory and return a description when it remains."""
    try:
        path.rmdir()
    except OSError as error:
        return f"{path}: {error}"
    return None


def install(
    sudoers_path: Path,
    managed_path: Path,
    rule: bytes,
) -> None:
    """Validate and atomically install the managed sudoers files, restoring failures."""
    root_metadata = require_safe_path(sudoers_path, stat.S_IFREG, "sudoers file")
    assert root_metadata is not None
    managed_metadata = require_safe_path(managed_path, stat.S_IFREG, "managed sudoers drop-in", allow_missing=True)
    candidate_dir: Path | None = None
    main_candidate: Path | None = None
    complete_candidate: Path | None = None
    managed_candidate: Path | None = None
    try:
        try:
            old_main = sudoers_path.read_bytes()
            old_managed = managed_path.read_bytes() if managed_metadata is not None else None
            old_managed_metadata = managed_metadata
        except OSError as error:
            raise ConfigurationError(f"could not read sudoers configuration: {error}") from error
        main_content = rewrite_includes(old_main)
        managed_needs_replacement = (
            old_managed != rule
            or old_managed_metadata is None
            or stat.S_IMODE(old_managed_metadata.st_mode) != 0o440
        )
        main_needs_replacement = main_content != old_main
        if not main_needs_replacement and not managed_needs_replacement:
            return

        try:
            candidate_dir = Path(tempfile.mkdtemp(prefix=".sudoers-candidate-", dir=INCLUDE_DIR.parent))
            os.chmod(candidate_dir, 0o755)
            for entry in INCLUDE_DIR.iterdir():
                if entry.name == MANAGED_PATH.name:
                    continue
                details = entry.lstat()
                if not stat.S_ISREG(details.st_mode):
                    raise ConfigurationError(f"unsafe unrelated sudoers drop-in: {entry}")
                shutil.copyfile(entry, candidate_dir / entry.name)
                os.chmod(candidate_dir / entry.name, stat.S_IMODE(details.st_mode))
            candidate_managed = candidate_dir / MANAGED_PATH.name
            write_file(candidate_managed, rule, 0o440)
        except OSError as error:
            raise ConfigurationError(f"could not prepare sudoers candidate directory: {error}") from error
        candidate_main_content = main_content.replace(
            CANONICAL_INCLUDE.encode(), f"#includedir {candidate_dir}\n".encode()
        )
        complete_candidate = write_temp(
            SUDOERS_PATH.parent,
            candidate_main_content,
            stat.S_IMODE(root_metadata.st_mode),
            root_metadata.st_uid,
            root_metadata.st_gid,
        )
        main_candidate = write_temp(
            SUDOERS_PATH.parent,
            main_content,
            stat.S_IMODE(root_metadata.st_mode),
            root_metadata.st_uid,
            root_metadata.st_gid,
        )
        managed_candidate = write_temp(INCLUDE_DIR, rule, 0o440)
    except ConfigurationError as error:
        cleanup_failures = cleanup_candidates((main_candidate, complete_candidate, managed_candidate), candidate_dir)
        if cleanup_failures:
            raise ConfigurationError(f"{error}; could not clean up: {'; '.join(cleanup_failures)}") from error
        raise
    except (OSError, shutil.Error) as error:
        cleanup_failures = cleanup_candidates((main_candidate, complete_candidate, managed_candidate), candidate_dir)
        message = f"could not prepare sudoers candidates: {error}"
        if cleanup_failures:
            message += f"; could not clean up: {'; '.join(cleanup_failures)}"
        raise ConfigurationError(message) from error
    replaced_main = False
    replaced_managed = False
    try:
        validate_with_visudo(managed_candidate)
        validate_with_visudo(complete_candidate)
        if main_needs_replacement:
            os.replace(main_candidate, sudoers_path)
            replaced_main = True
        else:
            main_candidate.unlink()
        if managed_needs_replacement:
            os.replace(managed_candidate, managed_path)
            replaced_managed = True
        else:
            managed_candidate.unlink()
        validate_with_visudo()
    except BaseException as error:
        restoration_errors: list[str] = []
        if replaced_main:
            try:
                restore_main = write_temp(
                    SUDOERS_PATH.parent,
                    old_main,
                    stat.S_IMODE(root_metadata.st_mode),
                    root_metadata.st_uid,
                    root_metadata.st_gid,
                )
                try:
                    os.replace(restore_main, sudoers_path)
                except OSError as replace_error:
                    cleanup_error = remove_best_effort(restore_main)
                    if cleanup_error is not None:
                        raise OSError(f"{replace_error}; could not clean up: {cleanup_error}") from replace_error
                    raise
            except (ConfigurationError, OSError) as restore_error:
                restoration_errors.append(f"main sudoers: {restore_error}")
        if replaced_managed:
            try:
                if old_managed is None:
                    managed_path.unlink(missing_ok=True)
                else:
                    assert old_managed_metadata is not None
                    restore_managed = write_temp(
                        INCLUDE_DIR,
                        old_managed,
                        stat.S_IMODE(old_managed_metadata.st_mode),
                        old_managed_metadata.st_uid,
                        old_managed_metadata.st_gid,
                    )
                    try:
                        os.replace(restore_managed, managed_path)
                    except OSError as replace_error:
                        cleanup_error = remove_best_effort(restore_managed)
                        if cleanup_error is not None:
                            raise OSError(f"{replace_error}; could not clean up: {cleanup_error}") from replace_error
                        raise
            except (ConfigurationError, OSError) as restore_error:
                restoration_errors.append(f"managed sudoers: {restore_error}")
        cleanup_failures = cleanup_candidates((main_candidate, complete_candidate, managed_candidate), candidate_dir)
        if restoration_errors:
            cleanup_detail = f"; cleanup failed: {'; '.join(cleanup_failures)}" if cleanup_failures else ""
            raise ConfigurationError(
                f"configuration failed: {error}; restoration failed: {'; '.join(restoration_errors)}{cleanup_detail}"
            ) from error
        if cleanup_failures:
            raise ConfigurationError(f"configuration failed: {error}; cleanup failed: {'; '.join(cleanup_failures)}") from error
        if isinstance(error, ConfigurationError):
            raise
        raise ConfigurationError(f"configuration failed: {error}") from error
    else:
        cleanup_failures = cleanup_candidates((main_candidate, complete_candidate, managed_candidate), candidate_dir)
        if cleanup_failures:
            raise ConfigurationError(f"could not clean up sudoers candidates: {'; '.join(cleanup_failures)}")


def configure_existing_paths(
    check_only: bool,
    sudoers_path: Path,
    managed_path: Path,
) -> None:
    """Resolve, inspect, and install the configuration while the include directory cleanup scope is active."""
    managed_metadata = require_safe_path(managed_path, stat.S_IFREG, "managed sudoers drop-in", allow_missing=True)
    rule = desired_rule()
    try:
        original_main = sudoers_path.read_bytes()
    except OSError as error:
        raise ConfigurationError(f"could not read sudoers file ({sudoers_path}): {error}") from error
    active = sum(is_active_target_include(line) for line in original_main.splitlines(keepends=True)) == 1
    try:
        managed_content = managed_path.read_bytes() if managed_metadata is not None else None
    except OSError as error:
        raise ConfigurationError(f"could not read managed sudoers drop-in ({managed_path}): {error}") from error
    managed_active = managed_metadata is not None and managed_content == rule and stat.S_IMODE(managed_metadata.st_mode) == 0o440
    if check_only:
        if not active or not managed_active:
            raise ConfigurationError("desired sudoers configuration is not active")
        return
    install(sudoers_path, managed_path, rule)


def configure(check_only: bool) -> None:
    """Check or apply the safe sudoers configuration."""
    if platform.system() not in {"Darwin", "Linux"}:
        raise ConfigurationError(f"Unsupported operating system: {platform.system()}")
    require_safe_path(SUDOERS_PATH, stat.S_IFREG, "sudoers file")
    validate_with_visudo()
    include_exists = require_safe_path(INCLUDE_DIR, stat.S_IFDIR, "sudoers include directory", allow_missing=True) is not None
    include_created = not include_exists and not check_only
    if check_only and not include_exists:
        raise ConfigurationError(f"sudoers include directory does not exist: {INCLUDE_DIR}")
    if include_created:
        ensure_include_dir()
    try:
        configure_existing_paths(check_only, SUDOERS_PATH, MANAGED_PATH)
    except BaseException as error:
        if include_created:
            cleanup_error = remove_empty_directory(INCLUDE_DIR)
            if cleanup_error is not None:
                raise ConfigurationError(f"{error}; could not remove newly created include directory: {cleanup_error}") from error
        raise


def main(argv: list[str] | None = None) -> int:
    """Parse command-line options, escalate when necessary, and configure sudoers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the active configuration without modifying files")
    arguments = parser.parse_args(argv)
    if platform.system() not in {"Darwin", "Linux"}:
        return fail(f"Unsupported operating system: {platform.system()}")
    if os.geteuid() != ROOT_UID:
        command = ["sudo", "-n", sys.executable, str(Path(__file__).resolve())]
        if arguments.check:
            command.append("--check")
        try:
            result = subprocess.run(command, check=False, timeout=30)
        except FileNotFoundError:
            return fail("sudo is unavailable")
        except subprocess.TimeoutExpired:
            return fail("sudo authentication timed out")
        except OSError as error:
            return fail(f"could not run sudo: {error}")
        if result.returncode:
            return fail("noninteractive sudo authentication failed")
        return 0
    try:
        configure(arguments.check)
    except ConfigurationError as error:
        return fail(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
