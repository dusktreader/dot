# Task plan: Add workstation-specific `~/.dotrc_local` support


## Goal

Create `~/.dotrc_local` as a machine-local shell file that is automatically sourced at login.
The change has two parts: (1) add `~/.dotrc_local` to the `dotfile_paths` list in
`etc/install.yaml` so `_update_dotfiles` writes a `source` entry for it into `~/.extra_dotfiles`,
and (2) add a `_create_dotrc_local` step to `DotInstaller.install_dot()` that creates the file
with a minimal comment header if it does not already exist. The file is intentionally not tracked
in the repo — it is the user's per-machine escape hatch for aliases, env vars, and secrets that
do not belong in shared dotfiles.

Out of scope: migrating any existing per-machine content, adding content to the stub beyond a
comment header, or changing how any other dotfile is sourced.


## Project commands

### Run tests

Command:

```shell
uv run pytest
```

Expected output:

All tests pass with zero failures or errors.

### Run linter

Command:

```shell
uv run ruff check src tests
```

Expected output:

No linting errors reported.

### Run type checker

Command:

```shell
uv run ty check
```

Expected output:

No type errors reported.


## Project standards

- Line length: 120 characters (`[tool.ruff] line-length = 120` in `pyproject.toml`)
- New methods follow the same `with spinner(..., context_level="DEBUG"):` pattern used by other
  `DotInstaller` steps such as `_create_local_agents_file`.
- Test classes live in `tests/test_configure.py`; each scenario is a separate test method named
  `test_<method>__<scenario>`.


## Steps

1. Write a failing test `TestDotInstallerCreateDotrcLocal.test_create_dotrc_local__creates_file_when_absent` that calls `installer._create_dotrc_local()` on an installer whose home has no `.dotrc_local` and asserts the file exists afterward.
2. Run `uv run pytest tests/test_configure.py` and confirm the new test fails (method does not exist yet).
3. Add `_create_dotrc_local(self)` to `DotInstaller` in `src/dot_tools/configure.py`. The method should:
   - Return early (log debug, skip) if `self.home / ".dotrc_local"` already exists.
   - Otherwise create `~/.dotrc_local` with a minimal comment header (two lines: a `# ~/.dotrc_local` title comment and a blank-line-separated note that the file is machine-local and not tracked in the repository).
4. Call `self._create_dotrc_local()` from `install_dot()`, placed immediately after `self._update_dotfiles()`.
5. Run `uv run pytest tests/test_configure.py` and confirm the new test passes.
6. Write a second failing test `test_create_dotrc_local__skips_when_file_exists` that pre-creates `~/.dotrc_local` with known content, calls `_create_dotrc_local()`, and asserts the content is unchanged.
7. Run the test and confirm it passes (the early-return guard covers it).
8. Update `etc/install.yaml`: add `~/.dotrc_local` as the last entry in `dotfile_paths`.
9. Update `_update_dotfiles` in `configure.py` to resolve `dotfile_path` using `Path(path).expanduser()` instead of `self.root / path`. This handles `~/`-prefixed entries correctly via Python's built-in `~` expansion.
10. Write a failing test `TestDotInstallerUpdateDotfiles.test_update_dotfiles__expands_tilde_paths_against_home` that puts `~/.dotrc_local` in `dotfile_paths`, calls `_update_dotfiles()`, and asserts `source <home>/.dotrc_local` appears in `~/.extra_dotfiles`.
11. Run the test and confirm it passes.
12. Run `uv run pytest` (full suite), `uv run ruff check src tests`, and `uv run ty check`; confirm all pass.


## Acceptance criteria

- AC01: After `DotInstaller._create_dotrc_local()` runs on a home directory where `~/.dotrc_local`
  does not exist, the file is created and contains a comment header line.
- AC02: `_create_dotrc_local()` does not modify `~/.dotrc_local` when it already exists on disk.
- AC03: `install_dot()` calls `_create_dotrc_local()` (it appears in the method body after
  `_update_dotfiles()`).
- AC04: `etc/install.yaml` lists `~/.dotrc_local` in `dotfile_paths`.
- AC05: `_update_dotfiles()` writes `source <home>/.dotrc_local` (not
  `source <repo_root>/~/.dotrc_local`) into `~/.extra_dotfiles` when `~/.dotrc_local` is in the
  manifest's `dotfile_paths`.
- AC06: `uv run pytest`, `uv run ruff check src tests`, and `uv run ty check` all exit 0.


## Technical notes

`_update_dotfiles` currently computes `dotfile_path = self.root / path` for every entry in
`dotfile_paths`. In Python, `Path("/repo") / Path("~/.dotrc_local")` does **not** expand `~` —
it produces `/repo/~/.dotrc_local`, which is wrong. Use `Path(path).expanduser()` instead:

```python
dotfile_path = Path(path).expanduser()
```

For existing repo-relative entries (e.g. `.dotrc`, `.dot_aliases`) that currently resolve via
`self.root / path`, the behavior must be preserved. Inspect whether those entries should remain
repo-relative or switch to absolute paths — if they need to stay repo-relative, keep the
`self.root / path` join for non-`~/` entries and only apply `expanduser()` to `~/`-prefixed ones.
The simplest correct implementation:

```python
raw = str(path)
if raw.startswith("~/"):
    dotfile_path = Path(raw).expanduser()
else:
    dotfile_path = self.root / path
```
