# dot repository guide

This document covers the layout, conventions, and key workflows for the `dot` repository —
Tucker Beck's personal dotfiles and system-bootstrap tooling.

Repository path: `~/src/dusktreader/dot`


## Repository overview

| Path                        | Purpose                                                      |
|-----------------------------|--------------------------------------------------------------|
| `src/dot_tools/`            | Python package `dot-tools`                                   |
| `src/dot_tools/cli/`        | Typer CLI entry points                                       |
| `src/dot_tools/configure.py`| `DotInstaller` class — core bootstrap logic                  |
| `etc/install.yaml`          | Install manifest (links, copies, tools, settings, services)  |
| `bin/`                      | Shell helper scripts sourced at login                        |
| `.dot_*`, `.dotrc`          | Dotfiles sourced via `.extra_dotfiles` at shell startup      |
| `pyproject.toml`            | Project metadata; entry point `dt = dot_tools.cli.main:cli`  |
| `tests/`                    | pytest test suite                                            |


## The `dt` CLI

The CLI binary is `dt`. It is registered in `pyproject.toml` as:

```text
dt = "dot_tools.cli.main:cli"
```

Top-level commands:

| Command      | Description                                              |
|--------------|----------------------------------------------------------|
| `configure`  | Bootstrap / re-apply the full dotfiles installation      |
| `git`        | Git helper sub-commands                                  |
| `ssh`        | SSH key management sub-commands                          |
| `kv`         | Produce a JSON string from key→value pairs               |
| `line-length`| Report configured line length for the current project    |
| `urlencode`  | URL-encode a string and copy it to the clipboard         |
| `logs`       | View application logs (typerdrive built-in)              |
| `settings`   | Inspect/edit app settings (typerdrive built-in)          |

Run `dt --help` or `dt <command> --help` for full option details.


## `dt configure` — system bootstrap

`dt configure` is the primary bootstrap command. It creates a `DotInstaller` and calls
`install_dot()`, which runs the following steps in order:

1. **`_make_dirs`** — create directories listed under `mkdir_paths` in `etc/install.yaml`
2. **`_make_links`** — create symlinks in `$HOME` for every path under `link_paths`
3. **`_copy_files`** — copy files listed under `copy_paths`; respects file permissions and
   protects files the user has locally modified (compares against last git-committed content)
4. **SSH keypair** — generate `~/.ssh/<user>.ed25519` if it does not already exist
5. **`_install_tools`** — run installation scripts for each entry under `tools`; skips tools
   whose `check` command exits 0
6. **`_apply_settings`** — run scripts for each entry under `settings`; skips settings whose
   `check` command exits 0
7. **`_update_dotfiles`** — append `source <path>` lines for `dotfile_paths` entries to
   `~/.extra_dotfiles`
8. **`_github_cli_login`** — run `gh auth login` if not already authenticated
9. **`_add_ssh_keys`** — upload the generated SSH public key to GitHub via `gh ssh-key add`
10. **`_startup`** — inject an `EXTRA DOTFILES` block into `~/.bashrc` (Linux) or `~/.zshrc`
    (macOS) that sources `~/.extra_dotfiles`
11. **`_install_services`** — register services via launchd (macOS) or systemd user units (Linux)

### Key options for `dt configure`

| Option            | Default                          | Description                                          |
|-------------------|----------------------------------|------------------------------------------------------|
| `--root`          | `~/src/dusktreader/dot`          | Root of the dot repo to install from                 |
| `--override-home` | none                             | Install into this directory instead of `$HOME`       |
| `--force`         | `$DOT_FORCE` env var or `False`  | Overwrite destination files even if locally modified |

### Copy-file conflict resolution

When a file in `copy_paths` already exists at the destination and differs from the source:

- Without `--force`: compare destination against the last git-committed version of the source.
  If the destination matches the committed version, the source has since been updated — safe to
  overwrite. If the destination differs from the committed version, the user has local changes —
  abort with an error.
- With `--force`: always overwrite.


## Install manifest (`etc/install.yaml`)

The manifest is loaded by `DotInstaller.__init__` into an `InstallManifest` pydantic model.
Edit `etc/install.yaml` to add or change what gets installed.

Sections:

- **`link_paths`**: paths relative to repo root that get symlinked into `$HOME`
- **`copy_paths`**: paths that get copied (not linked); may specify `perms` as an octal string
- **`dotfile_paths`**: shell files sourced at login via `~/.extra_dotfiles`
- **`mkdir_paths`**: directories to create under `$HOME`
- **`tools`**: list of `{name, check, scripts: {generic, linux, darwin}}` entries
- **`settings`**: same structure as tools; used for OS/preference configuration
- **`services`**: list of `{name, label, executable, args, config_template}` entries; registered
  as launchd agents (macOS) or systemd user services (Linux)


## Development workflow

Install the package in editable mode with uv:

```shell
uv sync
```

Run the test suite:

```shell
uv run pytest
```

Lint and type-check:

```shell
uv run ruff check src tests
uv run ty check
```

The configured line length is 120 characters (`[tool.ruff] line-length = 120`).


## Platform support

`DotInstaller` branches on `platform.system()`:

- `"Linux"` — uses `apt`, `snap`, systemd user services, `~/.bashrc`
- `"Darwin"` — uses MacPorts (`sudo port`), launchd agents, `~/.zshrc`

Tool and setting scripts can provide `generic`, `linux`, and/or `darwin` variants.
`generic` takes priority if present; otherwise the platform-specific script is required.
