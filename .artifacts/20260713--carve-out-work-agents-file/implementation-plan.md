# Implementation Plan: Carve work-specific configuration into private work-dot repository


## Goal

This plan implements the two-repository split described in the design plan, moving all McGraw Hill-specific
configuration to a new private `work-dot` repository while maintaining `dot` as a standalone, employer-neutral
base layer. The implementation adds a `wdt` CLI that mirrors the shape of `dt` and integrates with `dt` via
subprocess invocation when present. Both CLIs implement two application-owned credential sub-commands: `creds
fetch <key>` retrieves and prints a credential value to stdout for scripting, and `creds set <key> <value>`
writes a single credential with a non-revealing acknowledgement. The `creds` command group is a pure wrapper:
bare invocation (no subcommand) displays help and exits zero, performing no default action on the credentials
store and leaving it byte-identical. Both commands operate exclusively on nested credentials sub-models within
each application's Typerdrive-backed settings store, never on top-level or arbitrary fields. Stores are
strictly isolated: `dt creds set` targets only `Settings.credentials`, `wdt creds set` targets only
`WorkSettings.credentials`, with both verified to never mutate the other's store. Credential migration follows
a rollback-safe sequence: deploy both CLIs with new nested credentials sub-models, populate via both batch
`settings bind` and individual `creds set` commands, validate against both CLIs, then delete the legacy
`~/.agents/credentials.json` file.

The implementation spans two repositories: the existing `dot` at `~/src/dusktreader/dot` (public) and a new
`work-dot` at `~/src/mhe/work-dot` (private, GitHub Cloud, `https://github.com/Tucker-Beck_mcgraw/work-dot`). All
work-owned files are created in `work-dot`; all removals and clarifications happen in `dot`. Neither CLI mutates the
other's repository.


## Terminology

- **`add_settings_subcommand`**: A Typerdrive-provided decorator that automatically adds `settings`,
  `settings view`, `settings bind`, and other settings-management sub-commands to a Typer CLI. Both `dt` and
  `wdt` use this decorator to enable settings storage and access.
- **Settings store**: Typerdrive-managed configuration file/directory where application-defined settings
  (including credential fields) are persisted. `dt` and `wdt` maintain separate, isolated stores managed by
  Typerdrive based on app name.
- **Nested credentials sub-model**: A dedicated Pydantic sub-model (structured type) on each CLI's primary
  settings model that contains all credential entries for that CLI. For example, `Settings.credentials`
  (instance of a `CredentialsModel` class) or `WorkSettings.credentials` (instance of a work-specific
  `WorkCredentialsModel`). Credential values are never top-level settings fields.
- **`creds` command group**: Application-owned (not Typerdrive-provided) Typer sub-command group that
  implements `fetch`, `set`, and other credential-related operations. Both `dt` and `wdt` define their own
  `creds` group; Typerdrive provides no built-in `creds` facility or credentials API.
- **`creds fetch`**: Application-defined CLI command that reads a named field from the nested credentials
  sub-model within the settings store (via Typerdrive's settings access APIs) and prints its value to stdout.
  Validation (empty check, placeholder detection) is application-controlled.
- **`creds set`**: Application-defined CLI command that writes a single named field to the nested credentials
  sub-model within the settings store (via Typerdrive's settings access APIs), restricted to known credential
  keys only. On success, exits zero and prints a non-revealing acknowledgement (without echoing the value or
  any derivation to stdout or stderr). On unknown key or validation failure, exits non-zero with a diagnostic
  on stderr and leaves settings on disk completely unchanged. Used for individual credential configuration
  after `configure` seeding or as a manual/interactive companion to batch `settings bind`.
- **Settings binding/update**: Typerdrive-provided `settings bind` or `settings update` sub-command that
  allows CLI users to populate individual settings fields, including fields inside nested sub-models. Usage:
  `dt settings bind --credentials.jira_api_key <value>` or `dt settings bind --credentials
  '{"jira_api_key": ...}'` (exact syntax discovered during Task 04 research). The batch migration path.


## Project Commands

### Run dot tests

Prerequisites:

- uv: [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)

Command:

```shell
cd /Users/tucker.beck/src/dusktreader/dot && uv run pytest
```

Expected Output:

All tests pass, including new tests for wdt detection, credentials fetch, and configuration integration.
Coverage meets or exceeds the configured floor (70%).

### Run work-dot tests

Command:

```shell
cd /Users/tucker.beck/src/mhe/work-dot && uv run pytest
```

Expected Output:

All tests pass. Coverage meets or exceeds configured floor for new work-specific code.

### Run quality gate (dot)

Command:

```shell
cd /Users/tucker.beck/src/dusktreader/dot && uv run ruff check src tests && uv run ty check
```

Expected Output:

Zero lint errors, zero type check errors.

### Run quality gate (work-dot)

Command:

```shell
cd /Users/tucker.beck/src/mhe/work-dot && uv run ruff check src tests && uv run ty check
```

Expected Output:

Zero lint errors, zero type check errors.

### Validate dt configure with wdt absent

Command:

```shell
dt configure --override-home /tmp/test-home-dt-only
```

Expected Output:

All steps complete successfully. No warnings, errors, or references to work layer in output.
Work configuration is silent/absent.

### Validate dt configure with wdt present

Command:

```shell
# Ensure wdt is on PATH, then:
dt configure --override-home /tmp/test-home-both
```

Expected Output:

All dot steps complete. Final step invokes wdt and reports success of work configuration step.
Exit code is zero.

### Validate wdt configure standalone

Command:

```shell
wdt configure --override-home /tmp/test-home-wdt-only
```

Expected Output:

All work steps complete. Secrets are seeded with placeholders and notices printed to stderr for each
empty secret. Exit code is zero even with empty secrets.

### Validate creds fetch (dt)

Command:

```shell
dt creds fetch jira_base_url
```

Expected Output:

Raw secret value printed to stdout with no surrounding formatting. Missing keys exit non-zero.

### Validate creds fetch (wdt)

Command:

```shell
wdt creds fetch jira_api_key
```

Expected Output:

Raw secret value printed to stdout with no surrounding formatting. Behavior matches `dt creds fetch`
exactly.

----

## Project Standards

- [dot repository guide](~/.dot_agents/dot.md)
- [Markdown style guide](~/.agents/instructions/markdown.md)
- [Python style guide](~/.agents/instructions/python.md)
- [Git safety and commit guidance](~/.agents/instructions/git-safety.md) and
  [git.md](~/.agents/instructions/git.md)
- [Editing standards](~/.agents/instructions/editing.md)


## Relevant Skills

- `run-implementation` (orchestration)
- `execute-implementation-plan` (task execution)
- `review-implementation-execution` (code review)
- `run-hotfix` (post-implementation fixes)


## Execution


### 01: Initialize work-dot repository and establish feature branch

Initialize the new private `work-dot` repository at `~/src/mhe/work-dot` with a mandatory clean repository
history: a minimal `Initial Commit` on main/master containing only README.md, followed by a feature branch
for all remaining scaffolding and implementation work. This repository will be hosted on GitHub Cloud under
the `Tucker-Beck_mcgraw` account at `https://github.com/Tucker-Beck_mcgraw/work-dot`.


#### Acceptance Criteria

- AC01: `~/src/mhe/work-dot` directory exists locally with git initialized (.git exists).
- AC02: `main` (or `master`) branch exists with exactly one commit.
- AC03: The first commit has message `Initial Commit` (exact message).
- AC04: The first commit contains only `README.md` with entire content `# work-dot\n` (H1 heading plus
  newline, nothing else).
- AC05: A feature branch named according to convention (e.g., `feat/NO-TICKET--bootstrap-work-dot`) exists
  and branches from the `Initial Commit`.
- AC06: Feature branch is checked out and all remaining scaffolding is applied to it: `pyproject.toml`,
  `.gitignore`, `src/work_tools/`, `tests/`, `etc/install.yaml`, and all other implementation files.
- AC07: `work-dot/pyproject.toml` on feature branch defines the `wdt` CLI entry point as
  `wdt = "work_tools.cli.main:cli"`.
- AC08: `work-dot` feature branch has a structure matching `dot`'s layout: `src/work_tools/`, `tests/`,
  `etc/install.yaml`.
- AC09: `.gitignore` on feature branch excludes `__pycache__`, `.venv`, `poetry.lock` (if uv is used), and
  any credential/secret files, exactly as `dot` does.
- AC10: `work-dot/pyproject.toml` on feature branch has the same Python version requirement (≥3.13), same
  dev dependencies (pytest, ruff, ty), and `typerdrive>=0.9.8` as a runtime dependency.
- AC11: `.git/config` points remote.origin to `https://github.com/Tucker-Beck_mcgraw/work-dot` (not yet
  pushed; local only).
- AC12: Feature branch has all scaffolding committed and is ready for Task 02 implementation. Task executor
  records actual branch name in implementation journal.
- AC13: Main/master branch remains clean with only the `Initial Commit`; no scaffolding or other files are
  present on main.


#### Steps

1. Create directory `~/src/mhe/` if it does not exist.
2. Create `~/src/mhe/work-dot` and initialize git: `git init ~/src/mhe/work-dot`.
3. Create `README.md` in `~/src/mhe/work-dot/` with exactly this content: `# work-dot\n` (one line: H1
   heading plus newline).
4. Run `git add README.md` and `git commit -m "Initial Commit"` in `work-dot`. Verify commit contains only
   README.md and nothing else.
5. Create feature branch with conventional name. Example: `feat/NO-TICKET--bootstrap-work-dot`. Check it
   out: `git checkout -b feat/NO-TICKET--bootstrap-work-dot`.
6. On the feature branch, create directory structure: `src/work_tools/`, `tests/`, `etc/`.
7. Copy `.gitignore` from `dot` to `work-dot`; no modifications needed.
8. Create `pyproject.toml` on feature branch with:
    - Entry point: `wdt = "work_tools.cli.main:cli"`.
    - Project name: `work-tools`.
    - Same dependencies and dev-dependencies as `dot`.
    - Same line-length (120) and pytest coverage settings as `dot`.
9. Create empty `src/work_tools/__init__.py` and `tests/__init__.py`.
10. Create `etc/install.yaml` on feature branch with empty sections (no installations at this stage).
11. Verify `.git/config` has remote.origin pointing to `https://github.com/Tucker-Beck_mcgraw/work-dot`.
    If not present, run:
    ```shell
    git config remote.origin.url https://github.com/Tucker-Beck_mcgraw/work-dot
    ```
12. Commit all scaffolding on feature branch with a clear message such as:
    ```
    feat: bootstrap work-dot with project structure and dependencies

    - Add pyproject.toml with wdt CLI entry point
    - Create src/work_tools/ and tests/ directories
    - Add .gitignore matching dot repository standards
    - Create etc/install.yaml template
    ```
13. Verify AC01–AC13 are satisfied:
    - `git log --oneline` on main shows only one commit: `Initial Commit`.
    - `git log --oneline` on feature branch shows at least two commits (Initial Commit, scaffolding commit).
    - `git branch` shows both main and feature branch.
    - Main branch contains only README.md.
    - Feature branch contains README.md plus pyproject.toml, .gitignore, src/, tests/, etc/.
14. Document the feature branch name (e.g., `feat/NO-TICKET--bootstrap-work-dot`) in implementation
    journal for reference by task executor and reviewer.


#### Technical Notes

- **Mandatory repository history**: The `Initial Commit` on main/master must contain ONLY README.md with
  exactly the content `# work-dot\n`. No pyproject, gitignore, scaffolding, or other files are in that
  first commit. This clean history is a requirement and must be directly testable by the user.
- **Feature branch naming**: Follow conventional branch naming (e.g., `feat/NO-TICKET--bootstrap-work-dot`,
  `feat/work-dot-scaffolding`). The exact name must be recorded in the implementation journal for the
  user's reference and for later merging.
- **Main/master cleanliness**: After Task 01 completes, the main branch must remain clean with only the
  `Initial Commit`. All implementation work stays on the feature branch. The user will merge when ready.
- **No push or remote configuration in commit**: The `.git/config` remote.origin entry is set but not
  pushed. The user controls when to push and to which remote.
- **Feature branch contains full scaffolding**: All pyproject, gitignore, directory structure, and Task 02+
  implementation files are added to the feature branch. The feature branch is production-ready for merging
  once the user chooses to do so.
- The `work-dot` repository is not pushed to GitHub in this step; that happens when the user decides (if
  at all). Local bootstrap on feature branch is sufficient for development and testing.
- All paths use `~/src/mhe/` as the work source root, matching the design plan. This path is referenced
  in the conditional Git include in `dot` but never hard-coded into `dot` beyond that include.
- The directory hierarchy, naming, and structure must exactly parallel `dot` so that the same CLI
  pattern (Typer, typerdrive integration, test layout) can be reused.

----

### 02: Create base work-tools CLI scaffold and typerdrive integration

Build the `wdt` CLI entry point, main command structure, and typerdrive integration to mirror `dt`'s
design. The CLI will have `configure` and `creds` sub-commands at minimum.


#### Acceptance Criteria

- AC01: `work-dot/src/work_tools/cli/main.py` exists and exports a `cli` Typer application.
- AC02: `wdt --help` lists at least `configure` and `creds` sub-commands.
- AC03: `wdt --help` displays a help text describing it as the work-layer bootstrap CLI.
- AC04: `wdt configure --help` shows options for `--root` (default `~/src/mhe/work-dot`),
  `--override-home`, and `--force`.
- AC05: `wdt creds --help` shows at least a `fetch` sub-command.
- AC06: `wdt creds fetch --help` shows an argument `<key>` and explains that it prints the secret
  value to stdout.
- AC07: Importing `work_tools.cli.main.cli` succeeds and the CLI is Typer-based.
- AC08: All typerdrive decorators (`add_settings_subcommand`, `add_logs_subcommand`) are applied to
  the `wdt` CLI, parallel to `dt`.


#### Steps

1. Create `work-dot/src/work_tools/cli/__init__.py` (empty).
2. Create `work-dot/src/work_tools/__init__.py` and `work-dot/src/work_tools/version.py` (returning
   a placeholder version like "0.1.0").
3. Create `work-dot/src/work_tools/cli/main.py` with:
    - Import typerdrive utilities: `add_logs_subcommand`, `add_settings_subcommand`, `terminal_message`,
      `handle_errors`, `attach_logging`.
    - Import the (to-be-created) `WorkInstaller` from `work_tools.configure`.
    - Import the (to-be-created) `WorkSettings` from `work_tools.settings`.
    - Create a `cli = typer.Typer(rich_markup_mode="rich")`.
    - Call `add_settings_subcommand(cli, WorkSettings)`.
    - Call `add_logs_subcommand(cli)`.
    - Define a `main()` callback that shows help or processes a `--version` flag, matching `dt`'s
      pattern.
    - Define a `configure()` command with options for `--root`, `--override-home`, and `--force`,
      delegating to `WorkInstaller`.
    - Leave the `creds` sub-command group scaffolded but not yet implemented; it will be added in
      Task 04.
4. Run `uv sync` in `work-dot` and verify the `wdt` command is installed on PATH (when in the venv
   or via `uv run wdt`).
5. Test the CLI: run `uv run wdt --help`, `uv run wdt configure --help`, and `uv run wdt creds --help`
   and verify all succeed and produce expected output.


#### Technical Notes

- The structure mirrors `dt` exactly: entry point in `cli/main.py`, decorators, option patterns.
- Use the same `handle_errors()` and `attach_logging()` patterns as `dt`.
- Typerdrive's `add_settings_subcommand()` will automatically add `settings`, `settings view`, `settings bind`,
  and other settings sub-commands; no custom implementation is needed for the base structure. The application
  (in Task 04) adds a separate `creds` sub-command group on top.
- The `creds` sub-command is application-defined, not provided by Typerdrive; it will be added in Task 04.

----

### 03: Create WorkInstaller and install manifest for work-dot

Implement the `WorkInstaller` class in `work-dot/src/work_tools/configure.py` that parallels
`DotInstaller` but owns work-specific files, directories, symlinks, and shell integration.


#### Acceptance Criteria

- AC01: `work-dot/src/work_tools/configure.py` exists and exports `WorkInstaller` class.
- AC02: `WorkInstaller` accepts `root`, `override_home`, and `force` parameters in `__init__`, matching
  `DotInstaller`'s signature.
- AC03: `WorkInstaller.install_dot()` (or `install_work()`) method exists and runs the install sequence.
- AC04: `work-dot/etc/install.yaml` defines `link_paths`, `copy_paths`, `dotfile_paths`, `mkdir_paths`,
  `tools`, and `settings` sections (all empty or with placeholders until later tasks populate them).
- AC05: `WorkInstaller` creates directories named in `mkdir_paths` under the override home if provided.
- AC06: `WorkInstaller` symlinks files from `link_paths` without touching any `dot`-owned paths.
- AC07: `WorkInstaller` appends source lines to `~/.extra_dotfiles` for paths under `dotfile_paths`,
  creating the file if absent.
- AC08: `WorkInstaller` never writes to any file under the `dot` repository or to any `dot`-owned
  path (e.g., `~/.gitconfig`, `~/.agents/` if not already work-specific).
- AC09: `WorkInstaller.install_dot()` completes successfully on a fresh home directory override.
- AC10: Running `WorkInstaller` twice on the same home directory (re-running `wdt configure`) succeeds
  without error, respecting existing files and not overwriting them unless `--force` is passed.


#### Steps

1. Copy and adapt `DotInstaller` from `dot/src/dot_tools/configure.py` to
   `work-dot/src/work_tools/configure.py`, renaming the class to `WorkInstaller`.
2. Modify `WorkInstaller` to use `WorkSettings` (to-be-created) instead of `Settings`.
3. Modify all hardcoded paths in `WorkInstaller` to reference `work-dot` repo root, not `dot` repo root.
4. In the `_make_dirs` step, ensure only work-owned directories are created (not touching
   `~/.config/opencode/agents` or any `dot`-exclusive directories).
5. In the `_make_links` step, ensure only work-owned symlinks are created. If the link target path
   (relative to the work repo) doesn't exist, raise an error.
6. In the `_copy_files` step, skip any copy operations that would overwrite `dot`-owned files. Raise
   an error if a copy target conflicts with a known `dot`-owned path.
7. In the `_update_dotfiles` step, append to `~/.extra_dotfiles` (creating it if absent), but check for
   and skip duplicate source lines.
8. Create `work-dot/etc/install.yaml` with the following structure (all sections initially empty or
   with comments):

   ```yaml
   link_paths: []
   copy_paths: []
   dotfile_paths: []
   mkdir_paths: []
   tools: []
   settings: []
   services: []
   ```

9. Run `uv run wdt configure --override-home /tmp/test-wdt-01` and verify it succeeds, creates the
   override home directory, and produces no errors.
10. Run `uv run wdt configure --override-home /tmp/test-wdt-01` a second time and verify it is
    idempotent.
11. Add unit tests for `WorkInstaller._make_dirs`, `_make_links`, `_copy_files`, `_update_dotfiles` to
    `work-dot/tests/test_configure.py`, mirroring `dot`'s test structure.
12. Run `uv run pytest` in `work-dot` and verify all new tests pass.


#### Technical Notes

- `WorkInstaller` should be a near-identical copy of `DotInstaller` with the class name changed and
  paths updated. Any shared utility functions (e.g., `resolve_tool_order`, `parse_octal`) can be
  moved to a shared module or duplicated; duplication is acceptable for now to avoid coupling
  the two repositories.
- The `~/.extra_dotfiles` file is shared between `dt` and `wdt` by design; both append source lines
  to it. The implementation must detect and skip duplicates to avoid sourcing the same file twice.
- Error messages in `WorkInstaller` should clearly identify themselves as coming from the work layer
  so troubleshooting is unambiguous.

----

### 04: Create work credentials store, WorkSettings, and credentials commands

Implement the work-specific secrets storage using Typerdrive's settings facility, define `WorkSettings`,
and add application-owned `creds fetch` and `creds set` sub-commands to the `wdt` CLI that retrieve and
write credential values to/from the nested credentials sub-model.


#### Acceptance Criteria

- AC01: `work-dot/src/work_tools/settings.py` exists and exports `WorkSettings` pydantic BaseModel.
- AC02: `WorkSettings` defines a nested `credentials` sub-model attribute (e.g., `credentials:
  WorkCredentialsModel`) that holds all work credential fields. Credential values must not be top-level
  fields in `WorkSettings`. The schema and structure are documented in Technical Notes. All required work
  secrets are included in the nested credentials model: at minimum `jira_api_key`, `confluence_token`,
  `datadog_api_key`.
- AC03: `wdt creds fetch <key>` prints the secret value to stdout with no surrounding formatting. Lookup
  is constrained to `WorkSettings.credentials` (the nested credentials sub-model), never top-level
  `WorkSettings` fields or arbitrary fields.
- AC04: `wdt creds fetch <missing-key>` exits non-zero (code 1) and prints an error to stderr
  (no output to stdout).
- AC05: `wdt creds fetch <key>` with an empty/placeholder value exits non-zero and prints an error.
- AC06: `wdt creds set <key> <value>` writes the credential value to the nested credentials sub-model
  only, never to top-level or arbitrary fields. Unknown keys exit non-zero with a diagnostic on stderr,
  and settings on disk remain completely unchanged (byte-identical verification in tests).
- AC07: `wdt creds set <key> <value>` exits zero on success with a non-revealing acknowledgement
  (e.g., "credential <key> updated") and prints nothing to stdout or stderr that echoes or derives the
  `<value>`.
- AC08: `wdt creds` (bare invocation) displays the `creds` command group's help output and exits zero.
  Help output is identical to `wdt creds --help`. The bare invocation performs no default action, reads
  no credentials from the store, writes no credentials to the store, and leaves the credentials store
  byte-identical (verified in tests). The `creds` group is a pure wrapper for `fetch` and `set`
  sub-commands only.
- AC09: `wdt creds --help` and `wdt creds` (bare invocation) produce identical help output.
- AC10: `wdt settings view` shows the current work settings (managed by Typerdrive's `add_settings_subcommand`).
- AC11: Research and document Typerdrive's settings access APIs, nested model support, and app-managed
  settings persistence pattern (critical blocking research). Verify by inspecting `Settings` in `dot`,
  examining its nested structure (if any), running `dt settings --help`, testing `dt settings bind` with
  nested field paths, and testing `dt settings view` before/after bind. Document the exact syntax for
  updating a nested field (e.g., `dt settings bind --credentials.jira_api_key <value>` or alternative
  syntax) in Technical Notes. Clarify which settings sub-commands (`bind`, `update`, etc.) are correct
  for Typerdrive. Determine how to programmatically read nested model fields and write them back safely.
- AC12: Typerdrive stores personal settings (via `dt settings`) and work settings (via `wdt settings`)
  in separate configuration files / directories, isolated by app name. Verify by checking config paths
  and confirming `dt` and `wdt` have separate storage with no cross-access.
- AC13: A `creds` command implementation must be discoverable in `work_tools.cli.main` or a
  sub-module (`work_tools.cli.creds`), added to the CLI as a sub-command group. The `creds` group is
  application-owned, not provided by Typerdrive.
- AC14: The `creds fetch` help text includes a plain statement that the command prints a secret value
  to stdout, that this is intentional for scripting, and that callers must not log or echo the output.
- AC15: The `creds set` help text includes a plain statement that the command does not echo the value
  or any derivation to stdout or stderr on success (only a non-revealing acknowledgement), so operators
  can paste values interactively without worrying about terminal transcript leaks.
- AC16: Unit tests for `creds fetch` verify successful fetch, missing-key error, empty-value error, and
  that help text includes the output-risk disclosure.
- AC17: Unit tests for `creds set` verify successful write with non-echo acknowledgement, unknown-key
  error with settings unchanged, write-to-nested-model-only scoping (cannot write to top-level fields).
- AC18: Unit tests verify bare `wdt creds` invocation (AC08-AC09): exits zero, displays help output
  identical to `wdt creds --help`, performs no store access (no read/write/mutate), and leaves the
  credentials store byte-identical before and after invocation.
- AC19: Unit tests for store isolation verify that `wdt creds set` writes only to `WorkSettings.credentials`
  and never mutates `Settings` or any personal store (byte-identical file snapshots before/after set on
  personal store).
- AC20: Use a temporary config directory (pytest fixture) in all tests to avoid touching real settings.


#### Steps

1. Research Typerdrive's settings storage and access APIs:
     - Inspect `dot/src/dot_tools/settings.py` to see how `Settings` is defined and passed to
       `add_settings_subcommand()`.
     - Run `dt settings --help` and record all available sub-commands (e.g., `view`, `bind`, `update`, etc.).
     - Run `dt settings bind --help` to understand the argument syntax and which fields can be updated.
     - Verify how Typerdrive initializes the context when `add_settings_subcommand()` is called.
     - Determine whether `SettingsManager` or another API is used to load/access settings programmatically.
     - Document all findings in Technical Notes (Step 2) so Task 05 and Task 06 can reference them.

2. Document Typerdrive API findings in Technical Notes:
     - Exact available sub-commands under `settings`.
     - Syntax for `bind` (or `update`) including field path (nested or flat).
     - How to programmatically load current settings via Typerdrive APIs.
     - How Typerdrive's context initialization works for CLI commands vs. direct API calls.
     - Config file location and format (used by Task 06 to seed secrets).

3. Create `work-dot/src/work_tools/settings.py` with a `WorkSettings` pydantic model:
     - Define a nested `credentials` sub-model class (e.g., `WorkCredentialsModel`) that contains all
       credential fields.
     - Add a `credentials: WorkCredentialsModel` attribute to `WorkSettings`. Credential values must not be
       top-level fields.
     - Document the nested structure and field names in Technical Notes.
     - Include all required work secrets in the nested credentials model: at minimum `jira_api_key`,
       `confluence_token`, `datadog_api_key`.

4. Create `work-dot/src/work_tools/cli/creds.py` with a `cli` Typer sub-command group.

5. Implement `cli.command()` for `fetch(key: str)` that:
      - Uses Typerdrive's settings access APIs (determined in step 1) to load the current `WorkSettings`.
      - Retrieves the value from the nested `credentials` sub-model by key name using `getattr` or nested
        access as appropriate. Lookup is scoped to the credentials sub-model only, never to top-level fields.
      - Raises an error if the key does not exist in `WorkSettings.credentials`.
      - Raises an error if the value is `None`, empty string, or a placeholder string (e.g.,
        "PLACEHOLDER_*").
      - Prints the value to stdout with no surrounding text and exits zero on success.
      - On any error, prints a clear error message to stderr and exits non-zero (code 1).
      - Include help text documenting that the command prints secrets to stdout and callers must not log
        or echo the output (AC13, fulfilling AC22 from design plan).

6. Implement `cli.command()` for `set(key: str, value: str)` that:
      - Uses Typerdrive's settings access APIs to load the current `WorkSettings`.
      - Validates that `<key>` is a known field in the nested `credentials` sub-model only. Reject any
        top-level fields, arbitrary dotted paths, or unknown credential names.
      - If validation fails (unknown key), exit non-zero with a diagnostic on stderr and do not modify
        settings on disk (leave settings byte-identical).
      - If validation passes, update the nested `credentials` sub-model field to `<value>` and persist
        via Typerdrive's write APIs.
      - Exit zero on success with a non-revealing acknowledgement to stdout (e.g., "credential <key>
        updated") that does not echo or derive `<value>`.
      - Include help text documenting that the command does not echo the value or any derivation, so
        operators can paste values interactively without worrying about terminal transcript leaks (AC14).

7. Add the `creds` CLI to `work-dot/src/work_tools/cli/main.py` via `cli.add_typer(creds_cli,
   name="creds")`.

8. Write unit tests in `work-dot/tests/test_cli_creds.py`:
       - Test `fetch` with a valid secret returns the value to stdout.
       - Test `fetch` with a missing key exits non-zero.
       - Test `fetch` with an empty value exits non-zero.
       - Test `fetch` with a placeholder value exits non-zero.
       - Test that help text includes the stdout/logging risk disclosure (AC16).
       - Test `set` with a known key writes the value and exits zero with non-echo acknowledgement.
       - Test `set` with an unknown key exits non-zero with settings unchanged (byte-identical verification).
       - Test `set` cannot write to top-level fields (scoped to nested credentials only).
       - Test that help text includes the non-echo behavior description (AC17).
       - Test bare `wdt creds` invocation exits zero and displays help output (AC18).
       - Test bare `wdt creds` invocation produces help output identical to `wdt creds --help` (AC18).
       - Test bare `wdt creds` invocation performs no store access: capture and verify settings file is
         unchanged before and after invocation using byte-identical snapshots (AC18).
       - Test store isolation: `wdt creds set` does not mutate personal settings store (AC19).
       - Use a temporary config directory (pytest fixture) to avoid touching real settings (AC20).

9. Write integration tests in `work-dot/tests/test_configure.py` (to be implemented after Task 05):
       - Test `wdt configure` seeds all secrets with placeholders.
       - Test `wdt creds fetch <key>` on a seeded-but-empty secret exits non-zero.
       - Test `wdt creds set <key> <value>` populates a seeded credential and `creds fetch` returns it.
       - Test bare `wdt creds` invocation during and after `wdt configure` exits zero and leaves
         settings unchanged.

10. Run `uv run pytest` and verify all tests pass.

11. Manually run:
       - `uv run wdt creds` (bare invocation) and verify it exits zero and displays help.
       - `uv run wdt creds --help` and verify output is identical to bare `wdt creds`.
       - `uv run wdt creds fetch <key>` (before any settings are configured) and verify it exits non-zero
         with a meaningful error.
       - `uv run wdt creds set <key> <value>` with a known key and verify it exits zero with non-echo
         acknowledgement.
       - `uv run wdt creds set unknown_key <value>` with an unknown key and verify it exits non-zero,
         settings are unchanged.


#### Technical Notes

##### Nested credentials sub-model (AC02)

The design plan AC17 requires credentials to nest under a dedicated sub-model in the primary settings
schema. This Task 04 research must verify that Typerdrive supports binding to and reading from nested
Pydantic models and must determine the exact syntax for `dt settings bind --credentials.jira_api_key
<value>` or an equivalent dotted-path or JSON-based syntax. Document the verified approach in Technical
Notes so Tasks 05, 06, and 13 use the correct syntax.


##### Typerdrive API research (Step 1)

Determine and document:

1. How `add_settings_subcommand()` manages settings storage and context initialization.
2. What programmatic APIs exist to load settings (e.g., `SettingsManager`, context manager, etc.).
3. The exact syntax for `dt settings bind` to populate fields inside a nested sub-model (e.g.,
   `--credentials.jira_api_key` or `--credentials '{"jira_api_key": ...}'`).
4. How separate CLI apps (`dt` vs. `wdt`) maintain separate config directories.
5. Whether Typerdrive can access/validate nested model fields programmatically.

Results must be recorded in Technical Notes so Task 05 (`dt creds fetch`), Task 06 (secret seeding),
and Task 13 (migration guide) all reference verified facts, not assumptions. This is critical because
the migration path and credential binding syntax depend on Typerdrive's actual nested model support.


##### Creds fetch implementation (Step 5)

Access to settings requires Typerdrive context initialization. Task 04 determines the correct pattern
from APIs; Task 05 and Task 06 reference this pattern. For CLI commands (like `creds fetch`), context
is typically initialized by the framework when the CLI runs. For programmatic access outside the CLI
(like seeding in Task 06), an explicit initialization pattern must be determined and documented.


##### Placeholder values

Use pattern `f"PLACEHOLDER_{field_name.upper()}"` for consistency and ease of detection during seeding
and validation.

##### Bare invocation behavior (AC29 from design plan)

The `creds` sub-command group is a pure wrapper: running `wdt creds` (bare invocation, no subcommand)
must exit zero, display help output identical to `wdt creds --help`, and perform no default action on
credentials storage. Ensure Typer is configured (likely via `invoke_without_command=True` on the sub-group)
to show help on bare invocation without running any credential fetch/set logic. Tests verify that the
credentials store remains byte-identical before and after a bare invocation, confirming no store access
occurred.

----

### 05: Implement dt creds fetch and creds set commands

Implement application-owned `creds fetch` and `creds set` sub-commands in the `dt` CLI that satisfy design
plan AC27–AC28: fetch or write personal credential fields from/to the nested credentials sub-model via
Typerdrive, with strict sub-model scoping, no-echo behavior on set, and store isolation validation.


#### Acceptance Criteria

- AC01: `dot/src/dot_tools/cli/creds.py` exists and exports a `cli` Typer sub-command group
  (application-defined, not provided by Typerdrive).
- AC02: `dt creds fetch <key>` prints the named secret value to stdout with no surrounding formatting.
  The lookup is constrained to `Settings.credentials` (the nested credentials sub-model), never
  top-level `Settings` fields or arbitrary fields.
- AC03: `dt creds fetch <key>` exits non-zero (code 1) and prints a diagnostic message to stderr
  if the key does not exist in `Settings.credentials` (the nested credentials sub-model).
- AC04: `dt creds fetch <key>` exits non-zero (code 1) and prints a diagnostic message to stderr
  if the key is `None`, empty string, or a placeholder value.
- AC05: `dt creds fetch --help` displays help text including a warning that the command prints a
  secret value to stdout and callers must not log or echo the output.
- AC06: `dt creds set <key> <value>` writes the credential value to the nested credentials sub-model
  only, never to top-level or arbitrary fields. Unknown keys exit non-zero with a diagnostic on stderr,
  and settings on disk remain completely unchanged (byte-identical verification in tests).
- AC07: `dt creds set <key> <value>` exits zero on success with a non-revealing acknowledgement
  (e.g., "credential <key> updated") and prints nothing to stdout or stderr that echoes or derives
  the `<value>`.
- AC08: `dt creds set --help` displays help text including a statement that the command does not echo
  the value or any derivation, so operators can paste values interactively without worrying about
  terminal transcript leaks.
- AC09: `dt creds fetch` and `dt creds set` are registered in `dot/src/dot_tools/cli/main.py` and
  invoked as `dt creds fetch <key>` and `dt creds set <key> <value>`.
- AC10: No access to work-store state; the commands only operate on personal `Settings`, never from
  `WorkSettings` or work-dot.
- AC11: `dt creds` (bare invocation) displays the `creds` command group's help output and exits zero.
  Help output is identical to `dt creds --help`. The bare invocation performs no default action, reads
  no credentials from the store, writes no credentials to the store, and leaves the credentials store
  byte-identical (verified in tests). The `creds` group is a pure wrapper for `fetch` and `set`
  sub-commands only (aligns with design plan AC30).
- AC12: `dt creds --help` and `dt creds` (bare invocation) produce identical help output (aligns with
  design plan AC30).
- AC13: Unit tests verify successful fetch, missing-key error, empty-value error, and help text
  includes the output-risk disclosure (fetch) and non-echo behavior (set).
- AC14: Unit tests for `set` verify successful write, unknown-key error with settings unchanged,
  write-to-nested-model-only scoping (cannot write to top-level fields).
- AC15: Unit tests verify bare `dt creds` invocation (AC11-AC12): exits zero, displays help output
  identical to `dt creds --help`, performs no store access (no read/write/mutate), and leaves the
  credentials store byte-identical before and after invocation.
- AC16: Unit tests verify store isolation: `dt creds set` does not mutate work settings store
  (byte-identical file snapshots before/after set on work store).
- AC17: Unit tests use a temporary config directory to avoid touching real settings.
- AC18: Manual verification: `dt creds` exits zero and displays help; `dt creds fetch <key>` exits
  non-zero before any settings are configured, with a meaningful error message; `dt creds set <key>
  <value>` exits zero with non-echo acknowledgement.


#### Steps

1. Create `dot/src/dot_tools/cli/creds.py` with a `cli` Typer sub-command group (application-owned).

2. Implement `cli.command()` for `fetch(key: str)` that:
     - Uses Typerdrive's settings access APIs (documented in Task 04 Technical Notes) to load the
       personal `Settings`.
     - Retrieves the attribute from the nested `Settings.credentials` sub-model by name using `getattr`
       or nested access as appropriate. Lookup is constrained to the nested credentials sub-model,
       never top-level `Settings` fields or arbitrary fields.
     - Raises an error if the key does not exist in `Settings.credentials`.
     - Raises an error if the value is `None`, empty string, or a placeholder string (e.g.,
       "PLACEHOLDER_*").
     - Prints the value to stdout with no surrounding text and exits zero.
     - On any error, prints the error to stderr and exits non-zero (code 1).

3. Implement `cli.command()` for `set(key: str, value: str)` that:
     - Uses Typerdrive's settings access APIs to load the current `Settings`.
     - Validates that `<key>` is a known field in the nested `credentials` sub-model only. Reject any
       top-level fields, arbitrary dotted paths, or unknown credential names.
     - If validation fails (unknown key), exit non-zero with a diagnostic on stderr and do not modify
       settings on disk (leave settings byte-identical).
     - If validation passes, update the nested `credentials` sub-model field to `<value>` and persist
       via Typerdrive's write APIs.
     - Exit zero on success with a non-revealing acknowledgement to stdout (e.g., "credential <key>
       updated") that does not echo or derive `<value>`.

4. Add help text for `fetch` documenting that the command prints secrets to stdout and callers are
   responsible for not logging output (AC05, satisfying design plan AC22).

5. Add help text for `set` documenting that the command does not echo the value or any derivation,
   so operators can paste values interactively without worrying about terminal transcript leaks (AC08).

6. Register the `creds` CLI in `dot/src/dot_tools/cli/main.py` via
   `cli.add_typer(creds_cli, name="creds")`.

7. Write unit tests in `dot/tests/test_cli_creds.py`:
      - Test `fetch` with a valid secret returns the value to stdout.
      - Test `fetch` with a missing key exits non-zero with a diagnostic error.
      - Test `fetch` with an empty value exits non-zero with a diagnostic error.
      - Test `fetch` with a placeholder value exits non-zero with a diagnostic error.
      - Test that help text includes the stdout/logging risk disclosure (AC13).
      - Test `set` with a known key writes the value and exits zero with non-echo acknowledgement.
      - Test `set` with an unknown key exits non-zero with settings unchanged (byte-identical verification).
      - Test `set` cannot write to top-level fields (scoped to nested credentials only) (AC14).
      - Test that help text includes the non-echo behavior description (AC14).
      - Test bare `dt creds` invocation exits zero and displays help output (AC15).
      - Test bare `dt creds` invocation produces help output identical to `dt creds --help` (AC15).
      - Test bare `dt creds` invocation performs no store access: capture and verify settings file is
        unchanged before and after invocation using byte-identical snapshots (AC15).
      - Test store isolation: `dt creds set` does not mutate work settings store if present
        (byte-identical file snapshots before/after set on work store) (AC16).
      - Use a temporary config directory (pytest fixture) to avoid touching real settings (AC17).

8. Run `uv run pytest` in `dot` and verify all tests pass.

9. Manually run:
      - `uv run dt creds` (bare invocation) and verify it exits zero and displays help.
      - `uv run dt creds --help` and verify output is identical to bare `dt creds`.
      - `uv run dt creds fetch <key>` (before any settings are configured) and verify it exits
        non-zero with a meaningful error.
      - `uv run dt creds set <key> <value>` with a known key and verify it exits zero with non-echo
        acknowledgement.
      - `uv run dt creds set unknown_key <value>` with an unknown key and verify it exits non-zero,
        settings are unchanged.


#### Technical Notes

- The implementation mirrors Task 04's `wdt creds fetch` but operates on the personal `Settings`
  model instead of `WorkSettings`.
- Both `dt creds fetch` and `wdt creds fetch` are application-defined commands, not provided by
  Typerdrive. Each CLI owns and implements its own `creds` sub-command group.
- Settings access from within a CLI command benefits from automatic Typerdrive context initialization
  when the CLI runs.
- Error messages must clearly indicate "personal secrets" to distinguish from work secrets if both CLIs
  are present.
- Bare invocation behavior (AC11-AC12, AC30 from design plan): The `creds` group must be configured
  as a pure wrapper sub-command that displays help on bare invocation and exits zero. Use Typer's
  `invoke_without_command` pattern or equivalent to ensure no default action runs: no store reads,
  writes, or mutations occur on bare invocation, and the help text produced matches `--help` exactly.

----

### 06: Implement wdt configure credential seeding and notices

Enhance `WorkInstaller.install_dot()` to seed the work credentials store (nested sub-model) with
placeholder entries for all required credential keys during the `wdt configure` step.


#### Acceptance Criteria

- AC01: When `wdt configure` runs, it creates or updates the work settings file and ensures all
  credential fields are present in the nested `credentials` sub-model within `WorkSettings`.
- AC02: Any key that is not yet set (missing or empty) is seeded with a placeholder value like
  `"PLACEHOLDER_JIRA_API_KEY"`.
- AC03: If a key already has a non-empty, non-placeholder value, `wdt configure` leaves it untouched
  (re-running `wdt configure` does not destroy existing credentials).
- AC04: After seeding, `wdt configure` walks all seeded keys and prints a notice to stderr for each
  empty or placeholder value, directing the operator to populate it via `wdt settings update` or
  `wdt settings bind` (the exact command is determined in Task 04 step 5).
- AC05: Notices are printed in a consistent format: `[work] Secret '<key>' is not set. Configure it
  via: wdt settings bind --<key> <value>` or `wdt settings update --<key> <value>` (exact syntax
  determined in Task 04).
- AC06: Even with notices printed, `wdt configure` exits zero (zero exit code).
- AC07: `wdt configure` completes without blocking for input (fully non-interactive).
- AC08: Unit tests verify that seeding creates placeholders, re-running preserves existing values, and
  notices are printed to stderr.
- AC09: Running `uv run wdt configure --override-home /tmp/test-wdt-seed-live` completes without
  error and produces seeding notices on stderr; a subsequent `uv run wdt creds fetch <any-seeded-key>`
  exits non-zero with a diagnostic, confirming seeding ran successfully from within the live CLI context.


#### Steps

1. Add a method `WorkInstaller._seed_credentials()` that:
     - Uses Typerdrive's settings access and update APIs (documented in Task 04 Technical Notes) to
       access the work settings store and specifically the nested `credentials` sub-model.
     - Loads the current `WorkSettings` via Typerdrive.
     - Iterates over all fields in the nested `credentials` sub-model (not top-level settings fields).
     - For each credential field not yet set (missing, `None`, or empty), sets it to a placeholder value.
     - Saves the updated settings using Typerdrive's APIs, targeting the nested credentials sub-model.
     - Collects the credential keys that are empty/placeholder and returns them.

2. Call `_seed_credentials()` from `WorkInstaller.install_dot()` after all other install steps complete,
   initializing Typerdrive context as documented in Task 04's Technical Notes.

3. For each collected credential key from seeding, print a notice to stderr (using `logger.warning()` or
   direct stderr write) in the format defined in AC05. Reference the exact `wdt settings bind` syntax for
   nested credentials (e.g., `wdt settings bind --credentials.jira_api_key <value>`) discovered during
   Task 04 research. The notice must guide the operator to populate the nested credential field.

4. Add integration tests to verify credential seeding behavior:
     - Test that `wdt configure` on a fresh home creates all seed entries.
     - Test that running `wdt configure` twice preserves existing non-placeholder values.
     - Test that `wdt creds fetch <seeded-key>` exits non-zero with a diagnostic when the value
       remains a placeholder.

5. Manually run `wdt configure --override-home /tmp/test-wdt-seeds` and verify notices are printed
   to stderr for each unseeded credential, and exit code is zero.


#### Technical Notes

##### Nested credentials access (critical)

Task 04 research determines the exact APIs for:

1. Loading and accessing the nested `credentials` sub-model from `WorkSettings`.
2. Iterating over the fields within the nested credentials sub-model.
3. Updating individual credential fields inside the nested model and saving back to disk.
4. Initializing Typerdrive context programmatically (outside the CLI command context).

Document these findings in Task 04's Technical Notes. This Task 06 implementation must use only
verified, nested-model-aware APIs; it does not access top-level settings fields.

##### Seeding timing

Credential seeding happens at the end of `install_dot()` after all file/directory operations complete,
ensuring the environment is ready for `WorkSettings` to be initialized and updated.

##### Placeholder values

Use pattern `f"PLACEHOLDER_{field_name.upper()}"` for consistency and ease of detection in validation
and notices.

##### Notice format

Notices guide the operator to use the correct `wdt settings bind` syntax for nested credentials (e.g.,
`wdt settings bind --credentials.jira_api_key <value>`), using the exact syntax verified in Task 04.

----

### 07: Update dt configure to detect and invoke wdt

Modify the `dt configure` command in `dot/src/dot_tools/cli/main.py` to detect `wdt` on PATH,
invoke `wdt configure` as a final step with correct argument passing, and handle output and exit codes.

#### Acceptance Criteria

- AC01: `dt configure` checks for `wdt` on PATH as its final step (after all personal layer install
  steps).
- AC02: If `wdt` is not found, `dt configure` exits zero with no warning, no error, and no reference
  to the work layer anywhere in output.
- AC03: If `wdt` is found, `dt configure` invokes `wdt configure` with the same `--root`,
  `--override-home`, and `--force` options, passing `--override-home` and `--force` when present.
- AC04: When `dt configure --override-home <home>` is run, `wdt configure` receives `--override-home
  <home>`.
- AC05: When `dt configure` is run without `--override-home`, `wdt configure` is invoked without
  `--override-home` (each defaults to its own home).
- AC06: If `wdt configure` exits zero, `dt configure` prints a success message for the work layer and
  exits zero.
- AC07: If `wdt configure` exits non-zero, `dt configure` reprints both stdout and stderr from the
  `wdt` subprocess under a labeled prefix (e.g., `[work] ...`) and exits non-zero itself.
- AC08: The labeled prefix is applied to every line of work-layer output so the source is unambiguous.
- AC09: Unit tests mock `wdt` on and off PATH, testing both success and failure modes.
- AC10: Unit tests verify correct argument passing in all combinations (with/without `--override-home`,
  with/without `--force`).
- AC11: Integration tests exercise `dt configure` with both `wdt` absent and present (using a stub
  script on PATH), verifying output, exit codes, and argument passing match expectations.


#### Steps

1. In `dot/src/dot_tools/cli/main.py`, find the `configure()` command definition.
2. Modify `DotInstaller.install_dot()` (or create a new wrapper in `main.py`) to:
   - After all `DotInstaller` steps complete successfully, check if `wdt` is on PATH using
     `shutil.which("wdt")`.
   - If not found, print nothing and return (exit zero).
   - If found, construct the `wdt configure` command with the correct arguments:
     ```python
     wdt_cmd = ["wdt", "configure"]
     if override_home:
         wdt_cmd.extend(["--override-home", str(override_home)])
     if force:
         wdt_cmd.append("--force")
     ```
   - Invoke `wdt configure` as a subprocess, capturing stdout and stderr.
   - If exit code is zero, print `"[work] Configuration complete."` and continue.
   - If exit code is non-zero, prefix every line of the captured output with `"[work] "` and print
     to stdout/stderr respectively, then raise an error or exit non-zero.
3. Test helpers:
   - Create a stub `wdt` script that takes options and exits with a configurable exit code (for
     testing).
   - Add it to PATH during tests.
4. Write unit tests in `dot/tests/test_configure.py`:
   - Test `dt configure` with `wdt` absent (using `monkeypatch` to mock `shutil.which` returning
     `None`).
   - Test `dt configure` with `wdt` present and successful (mock `subprocess.run` returning exit code
     0).
   - Test `dt configure` with `wdt` present and failing (mock `subprocess.run` returning non-zero).
   - Verify output prefixing in the failure case.
5. Write integration tests:
   - Create a minimal test home directory.
   - Run `dt configure --override-home <test-home>` and verify work layer is silent.
   - Create a stub `wdt` script on PATH (in a test bin directory).
   - Run `dt configure --override-home <test-home>` again and verify `wdt` is invoked.
6. Run `uv run pytest` in `dot` and verify all tests pass.
7. Manually run `dt configure` on your actual machine (where `wdt` is likely not yet installed) and
   verify it completes as before with no work-related output.


#### Technical Notes

- Use `shutil.which("wdt")` to find `wdt` on PATH, not a direct path lookup.
- Capture both stdout and stderr from the subprocess so both are reported in case of failure.
- The prefixing logic must handle multiline output correctly; each line gets the prefix.
- The exit code propagation ensures that a failed `wdt configure` fails the entire `dt configure`
  command, as required by AC04 in the design plan.

----

### 08: Remove work-specific content from dot repository

Remove all McGraw Hill-specific configuration from `dot`, including work agent guidance, work Git
config, work shell aliases, hardcoded work paths, and references to the retired GHES hostname. This
is a cleanup pass to strip `dot` to employer-neutral content only.


#### Acceptance Criteria

- AC01: All references to `Tucker-Beck_mcgraw` GitHub account are removed from `dot` (if any exist).
- AC02: All references to `github.mheducation.com` (GHES hostname) are removed from `dot` config and
  agent guidance.
- AC03: Hardcoded work paths (e.g., `~/src/mhe/`, specific Jira URLs, work-specific aliases like
  `cdwork`) are removed from `dot` shell rc files and agent guidance.
- AC04: Work-specific Jira identity (email, tenant, cloud ID) is removed from any Jira client code
  in `dot`. The generic `cojira` command and generic Jira scaffold remain, but with all hardcoded
  work identity stripped.
- AC05: Any work-specific agent guidance or instructions in `dot/.agents/instructions/` are removed.
  Only generic personal and machine context remain.
- AC06: Credential-file guidance (references to `~/.agents/credentials.json` for work secrets) is
  removed from `dot` agent guidance.
- AC07: Git config in `.gitconfig` or `.gitconfig.dusktreader` no longer references any work paths or
  work-specific includes (except for the conditional include that points to the work overlay file,
  which is added in task 09).
- AC08: All changes are committed to `dot` with a clear message indicating removal of work-specific
  content.
- AC09: After cleanup, `dot` can be cloned or installed on a fresh machine and contains no
  McGraw Hill-specific information anywhere.
- AC10: No push to the remote `dot` repository occurs. All changes remain committed locally on the
  feature branch. The user decides whether and when to push or merge.


#### Steps

1. Review `dot/.agents/instructions/` and remove any work-specific guidance or Jira tenant identity.
   Keep generic personal guidance (register, writing preferences, working hours that are not
   employer-specific).
2. Review `dot/.dot_zshrc` and remove the `cdwork` alias and any hardcoded `~/src/mhe/` paths. Keep
   generic shell configuration.
3. Review `dot/.gitconfig` and `dot/.gitconfig.dusktreader` and remove any `insteadOf` rules or
   includes for the GHES hostname. Remove any hardcoded work paths or work-specific config.
4. Review `dot/src/dot_tools/jira_tools.py` and remove any hardcoded work identity (email, tenant,
   cloud ID). The generic `cojira` command and branch-checkout code remain, but all configuration
   should be read from settings, not hardcoded.
5. Review `dot/etc/install.yaml` and ensure no work-specific paths or tools are listed. If any work
   identity was embedded in config, remove it.
6. Run a full-text search in `dot` for keywords like "mcgraw", "mhe", "jira.mheducation", "TuckerBeck"
   and remove matches that are work-specific (keep personal identity like "tucker.beck@gmail.com").
7. Search for "github.mheducation.com" and remove all occurrences.
8. Add a task to the .dot_agents/dot.md or AGENTS.md documenting that work configuration is now
   separate and installed via `wdt` if needed.
9. Commit all changes with message:
   ```
   refactor(dot): remove McGraw Hill-specific configuration

   - Removed work Jira identity and tenant references
   - Removed GHES hostname insteadOf rules
   - Removed hardcoded work paths (~/src/mhe/, cdwork alias)
   - Removed work-specific agent guidance
   - Removed credential-file references for work secrets
   - Kept generic personal context and machine configuration
   - Kept generic Jira client scaffold for any tenant

    Work-specific configuration now lives in private work-dot repository.
    Both dt and wdt are needed for full environment on work machine.
    ```
10. Verify all changes are committed on the feature branch. Do not push. The user will push and
    merge when ready.


#### Technical Notes

- This step is destructive (removing content) but reversible via git history. Take care to not remove
  generic content by mistake.
- Search queries should be case-insensitive for robustness (e.g., "McGraw", "MCGRAW", "mhe", "MHE").
- After cleanup, `dot` alone should work on any non-McGraw machine and provide no work-related hints.

----

### 09: Add conditional Git include for work overlay in dot

Add a conditional `includeIf` directive in `dot`'s main Git config that references the work-layer
Git-config overlay file owned by `work-dot`. The overlay file itself is created in task 09.


#### Acceptance Criteria

- AC01: `dot/.gitconfig` (or whichever file is sourced by the main Git config) contains a conditional
  include directive for the work source root.
- AC02: The conditional include is structured as:
  ```
  [includeIf "gitdir:~/src/mhe/"]
    path = ~/.gitconfig.work
  ```
- AC03: The path `~/.gitconfig.work` does not exist yet in `dot` (it will be created and symlinked by
  `wdt configure`).
- AC04: When the overlay file is absent, Git silently ignores the conditional include and produces no
  error.
- AC05: Documentation in the Git config explains that the work overlay is installed by `wdt` and is
  optional.


#### Steps

1. Open `dot/.gitconfig` (or `.gitconfig.dusktreader`).
2. Add the conditional include block at the end or in a logical location (e.g., after personal-only
   includes):
   ```
   [includeIf "gitdir:~/src/mhe/"]
     path = ~/.gitconfig.work
   ```
3. Add a comment above the block explaining it is for work-specific Git config managed by `wdt`.
4. Run `git config --list` and verify the conditional include appears.
5. Verify that Git does not produce an error when the overlay file is absent.
6. Commit to `dot` with a message indicating the conditional include addition.


#### Technical Notes

- The conditional include path uses `~/.gitconfig.work` (a dotfile in the home directory) rather than
  a path under a specific repo, so the overlay applies to all repositories under `~/src/mhe/`.
- Git's `includeIf` silently ignores missing files, so there is no error if the overlay does not
  exist until `wdt configure` creates and symlinks it.
- The exact path name `~/.gitconfig.work` is a design choice; it is clear and unlikely to conflict
  with other configs.

----

### 10: Create work shell rc and work Git config in work-dot

Create the work-layer shell rc file and work Git-config overlay in the `work-dot` repository. These
files define the work environment (paths, aliases, exports) and work-specific Git settings.


#### Acceptance Criteria

- AC01: `work-dot/.workrc` exists and exports `MHE_ROOT=~/src/mhe/`.
- AC02: `work-dot/.workrc` defines an alias `cdwork='cd $MHE_ROOT'` or similar for jumping to
  the work root.
- AC03: `work-dot/.workrc` can be sourced in bash/zsh without errors.
- AC04: `work-dot/.gitconfig.work` exists and contains work-specific Git configuration.
- AC05: `work-dot/.gitconfig.work` includes a `[user]` section with work email (e.g.,
  tucker.beck@mcgraw-hill.com) and name if applicable.
- AC06: `work-dot/.gitconfig.work` includes conditional or per-directory Git settings that apply
  inside `~/src/mhe/`.
- AC07: Both files are listed in `work-dot/etc/install.yaml` under `link_paths` so `wdt configure`
  will symlink them into the home directory.
- AC08: `wdt configure` creates symlinks `~/.workrc` and `~/.gitconfig.work` pointing to the
  files in the `work-dot` repo.
- AC09: After `wdt configure`, sourcing `~/.workrc` sets `MHE_ROOT` and defines `cdwork`.


#### Steps

1. Create `work-dot/.workrc` with:
     ```shell
     # Work environment configuration (sourced from ~/.workrc by ~/.extra_dotfiles)

     export MHE_ROOT="${HOME}/src/mhe"

     alias cdwork="cd ${MHE_ROOT}"
     ```
2. Create `work-dot/.gitconfig.work` with:
    ```
    [user]
      email = tucker.beck@mcgraw-hill.com
      name = Tucker Beck
    ```
3. Update `work-dot/etc/install.yaml` to add both files to `link_paths`:
    ```yaml
    link_paths:
      - .workrc
      - .gitconfig.work
    ```
4. Update `work-dot/etc/install.yaml` to add the work shell rc to `dotfile_paths`:
    ```yaml
    dotfile_paths:
      - .workrc
    ```
5. Run `uv run wdt configure --override-home /tmp/test-wdt-rc` and verify:
    - `~/.workrc` symlink is created.
    - `~/.gitconfig.work` symlink is created.
    - Sourcing `~/.workrc` sets `MHE_ROOT` and `cdwork` alias.
6. Verify Git sees the work config: `git config --list` in a repo under `~/src/mhe/` shows the work
   email if the overlay is linked.
7. Commit to `work-dot` with a message: `"feat(work): add work shell rc and git config"`.


#### Technical Notes

- The shell rc file uses the standard naming convention `.workrc` to match `dot`'s `.dot_zshrc`,
  `.dot_misc`, etc.
- Work email and Git identity should be accurate for the implementation but can be updated as needed
  (it's configuration, not code).
- Both files are symlinked into the home directory, so they are easily sourced and included by the
  existing shell and Git config infrastructure.

----

### 11: Create work-specific agent instructions in work-dot

Create a work-specific agent instructions file in `work-dot` that contains McGraw Hill-specific
guidance. This file is symlinked into `~/.agents/instructions/` by `wdt configure`.


#### Acceptance Criteria

- AC01: `work-dot/.agents/instructions/work.md` exists and contains McGraw Hill and Fusion team
  specific guidance.
- AC02: The file documents the work Jira tenant, Confluence URL, Datadog account, and other
  work-specific service endpoints (without hardcoding secrets).
- AC03: The file documents how to fetch work secrets via `wdt creds fetch <key>`.
- AC04: The file is symlinked into `~/.agents/instructions/work.md` by `wdt configure`.
- AC05: The filename clearly identifies it as work-specific (e.g., `work.md`, not generic).
- AC06: Agent sessions that read `~/.agents/instructions/` pick up this file and can reference it
  during work tasks.


#### Steps

1. Create `work-dot/.agents/instructions/work.md` with content covering:
   - McGraw Hill Fusion team identity and scope.
   - Work Jira tenant: `fusion.jira.com` (example; use actual).
   - Work Confluence: `fusion.confluence.com` (example; use actual).
   - Work Datadog: account and organization details.
   - How to fetch secrets: `wdt creds fetch jira_api_key`, etc.
   - Work source root: `~/src/mhe/`.
   - Note that work secrets are stored via `wdt settings`, not `~/.agents/credentials.json`.
2. Add `work-dot/.agents/instructions/work.md` to `work-dot/etc/install.yaml` under `link_paths`:
   ```yaml
   link_paths:
     - .agents/instructions/work.md
   ```
3. Ensure `WorkInstaller._make_dirs` creates `~/.agents/instructions/` if it does not exist.
4. Run `uv run wdt configure --override-home /tmp/test-wdt-agents` and verify
   `~/.agents/instructions/work.md` symlink is created.
5. Verify agent sessions can read the file.
6. Commit to `work-dot` with message: `"feat(work): add work-specific agent instructions"`.


#### Technical Notes

- This is the first work-specific agent guidance file. It replaces the work-tainted sections that were
  removed from `dot` in task 07.
- The file name `work.md` is clear and distinct from `dot`'s personal guidance files.
- No secrets are hardcoded in this file; all secret values are fetched via CLI.

----


### 12: Create comprehensive unit and integration tests for both CLIs

Write thorough test coverage for new functionality: wdt detection, credential seeding, credentials fetch,
and configure integration across both CLIs.


#### Acceptance Criteria

- AC01: Test coverage for `dot` meets or exceeds the configured floor (70%) for code touched in this
  implementation (wdt detection, subprocess invocation, argument passing).
- AC02: Test coverage for `work-dot` meets or exceeds the configured floor (70%) for new code
  (WorkInstaller, WorkSettings, credentials fetch, credential seeding).
- AC03: All tests pass when run via `uv run pytest` in their respective repositories.
- AC04: Integration tests exercise the full flow: `dt configure` with `wdt` present and absent,
  `wdt configure` standalone, and end-to-end secret configuration.
- AC05: Tests use temporary home directories and config paths to avoid touching real system state.
- AC06: Test output clearly indicates which tests are new vs. existing.


#### Steps

1. In `dot/tests/`, add tests for new `dt configure` functionality:
   - `test_configure_wdt_absent_silent` — verifies no work output when `wdt` is not on PATH.
   - `test_configure_wdt_present_success` — verifies `wdt` is invoked and output is included.
   - `test_configure_wdt_present_failure` — verifies failure output is prefixed and exit code is
     non-zero.
   - `test_configure_passes_override_home_to_wdt` — verifies arguments are passed correctly.
2. In `work-dot/tests/`, add tests for new `wdt` functionality:
    - `test_work_installer_creates_dirs` — verifies work directories are created.
    - `test_work_installer_creates_symlinks` — verifies work symlinks are created.
    - `test_work_installer_seeds_secrets_with_placeholders` — verifies seeding.
    - `test_work_installer_preserves_existing_secrets_on_rerun` — verifies idempotency.
    - `test_secrets_fetch_returns_secret_to_stdout` — verifies fetch behavior.
    - `test_secrets_fetch_empty_key_exits_nonzero` — verifies error handling.
    - `test_secrets_fetch_missing_key_exits_nonzero` — verifies error handling.
    - `test_work_settings_model_has_required_fields` — verifies WorkSettings schema.
    - `test_creds_bare_invocation_exits_zero_shows_help` — verifies bare `wdt creds` displays help
      and exits zero (AC29).
    - `test_creds_bare_invocation_matches_help_flag` — verifies bare `wdt creds` output matches
      `wdt creds --help` exactly (AC29).
    - `test_creds_bare_invocation_no_store_access` — verifies bare invocation leaves settings
      byte-identical (no read/write/mutate).
3. In `dot/tests/`, add tests for bare `dt creds` invocation:
    - `test_creds_bare_invocation_exits_zero_shows_help` — verifies bare `dt creds` displays help
      and exits zero (AC30).
    - `test_creds_bare_invocation_matches_help_flag` — verifies bare `dt creds` output matches
      `dt creds --help` exactly (AC30).
    - `test_creds_bare_invocation_no_store_access` — verifies bare invocation leaves settings
      byte-identical (no read/write/mutate).
3. Use pytest fixtures to create temporary home directories and config files:
   ```python
   @pytest.fixture
   def temp_home(tmp_path):
       home = tmp_path / "home"
       home.mkdir()
       yield home
       # cleanup
   ```
4. Mock `shutil.which()` in `dt` tests to simulate `wdt` presence/absence on PATH.
5. Mock `subprocess.run()` in `dt` tests to simulate `wdt` success/failure.
6. Use temporary Typerdrive config directories in `wdt` tests to avoid touching real settings.
7. Run `uv run pytest --cov` and verify coverage meets or exceeds the configured floor (70% configured in `pyproject.toml`).
8. Document any new test fixtures in comments or docstrings.


#### Technical Notes

- Both test suites use existing patterns from `dot/tests/` as templates.
- Use `pytest.MonkeyPatch` and `pytest.TempPathFactory` for isolation.
- Temporary home directories must include `.extra_dotfiles` file stubs if tests depend on appending
  to them.

----

### 13: Implement credentials migration workflow and nested model transition

Design and document the sequence for migrating credentials from the legacy `~/.agents/credentials.json`
to the Typerdrive-backed nested credentials sub-models in `dt` and `wdt`, and for transitioning existing
dot Settings/JiraInfo structure to the new nested credentials model.


#### Acceptance Criteria

- AC01: A document or script exists that outlines the exact steps for credential migration.
- AC02: The migration steps are:
   1. Deploy and install both `dot` and `work-dot` packages with new nested credentials sub-models.
   2. Discover exact syntax for `dt settings bind` targeting nested `credentials` sub-model fields
      (e.g., `--credentials.jira_api_key` or equivalent) from Task 04 research.
   3. Transition existing `Settings` model in `dot` (if it contains inline secrets like `JiraInfo`)
      to nested credentials model: determine which fields move into nested model, verify Task 04
      syntax works for binding them, and test on a staging home directory.
   4. Run `dt settings bind --credentials.<field> <value>` (batch path) OR `dt creds set <field>
      <value>` (individual path) with personal secret values to populate the nested credentials
      sub-model.
   5. Run `wdt settings bind --credentials.<field> <value>` (batch path) OR `wdt creds set <field>
      <value>` (individual path) with work secret values to populate the work nested credentials
      sub-model.
   6. Validate `dt creds fetch <key>` returns the expected value for each personal credential.
   7. Validate `wdt creds fetch <key>` returns the expected value for each work credential.
   8. Only after validation passes, delete `~/.agents/credentials.json`.
   9. Re-run dependent workflows (shell aliases, scripts, agent tasks) to confirm they use the
      CLI-backed credentials successfully.
- AC03: The migration document is accessible to the implementor (Tucker) and provides exact commands,
  not just guidelines.
- AC04: The document explains the rollback procedure if validation fails (keep the legacy file, debug
  the CLI-backed stores, re-validate).
- AC05: The migration is fully manual (operator-driven) and has clear success criteria at each step.


#### Steps

1. Create a migration guide in `dot/docs/MIGRATION_CREDENTIALS.md` or similar with sections:
     - **Overview**: Why migration is needed, what changes, and both available credential-setting paths.
     - **Prerequisites**: Both `dot` and `work-dot` must be installed with new CLI versions.
     - **Batch migration path (`settings bind`)**: Detailed instructions with exact commands for binding
       nested credential fields and validation.
     - **Individual migration path (`creds set`)**: Detailed instructions for populating credentials one
       at a time, with non-echo behavior documented.
     - **Mixed approach**: How to combine batch and individual methods.
     - **Rollback**: How to recover if validation fails.
     - **Verification**: How to confirm all dependent workflows still work after deletion of the legacy
       file.
2. Before writing the migration guide, consult Task 04 Technical Notes to understand the verified
   syntax for both `dt settings bind` and `dt creds set` targeting nested credentials sub-model fields
   (confirmed syntax from Task 04, not assumed). Document both approaches in the guide.
3. Enumerate all required credential keys (personal and work) from the current `~/.agents/credentials.json`
   and from any other ad-hoc credential sources (shell environment, hardcoded configs, etc.). Document
   them in the guide and map each to its field name in the nested credentials sub-model.
4. Verify the guide provides exact field names and example values.
5. Include a validation checklist in the guide so the operator knows when it is safe to delete the
   legacy file.
6. Include sample `dt settings bind` commands (batch path, with correct syntax from Task 04):
     - For nested credentials: `dt settings bind --credentials.jira_api_key <value>` or JSON syntax
       (exact syntax from Task 04).
     - Document the actual syntax used in production.
7. Include sample `dt creds set` commands (individual path):
     - Example: `dt creds set jira_api_key <value>` (no echo of value, only acknowledgement).
     - Document that this is the safe interactive/manual companion to batch binding.
8. Include corresponding `wdt settings bind` and `wdt creds set` commands for all work credential keys.
9. Document the secret keys needed by each CLI:
     - `dt`: personal keys (if any; examples might be GitHub token, etc.).
     - `wdt`: work keys (structured as determined in Task 04; at minimum jira credentials, confluence,
       datadog).
10. Document the transition plan for existing `Settings` structure (if it includes inline secrets):
      - Identify which fields in the current `Settings` model (e.g., fields in `JiraInfo`) should move
        into the new nested `credentials` sub-model.
      - Verify Task 04 research confirms that the new nested binding syntax works for these fields.
      - Test the transition on a staging home directory: run `dt configure`, then use either `dt
        settings bind` or `dt creds set` to populate, then `dt creds fetch` to validate the values are
        accessible.
      - Document the exact field mappings and any schema changes required.

11. Test the migration steps manually on a test machine or scratch home directory to verify the steps
    work and produce the expected result, including both batch and individual credential-setting paths.

12. Update `dot`'s README or `AGENTS.md` to reference the migration guide and clarify that both
    `settings bind` (batch) and `creds set` (individual/interactive) are available migration paths for
    bootstrapping credentials.


#### Technical Notes

##### Nested credentials binding (critical)

The migration guide must use only the verified nested-model binding syntax from Task 04 (e.g.,
`dt settings bind --credentials.jira_api_key <value>` or Task 04's confirmed alternative). Incorrect
syntax will cause binding to fail and risk credential loss if the operator proceeds to deletion anyway.
This is a high-stakes, one-shot credential cutover.

##### Settings/JiraInfo transition

If the current `Settings` model in `dot` contains inline secrets (like fields within `JiraInfo`), the
migration guide must cover transitioning those fields to the new nested credentials sub-model. This
includes:

1. Verifying the new nested binding syntax works with Task 04's verified API.
2. Testing the transition on a staging home directory before production.
3. Confirming `dt creds fetch` resolves fields from the nested model after migration.

##### Nested model schema from Task 04

The `Settings` and `WorkSettings` models (defined in Task 04) must both use nested credentials
sub-models. The exact field names, class names, and binding paths are determined in Task 04. Use only
verified syntax and schema from Task 04 Technical Notes.

##### Rollback is essential

If validation fails, the legacy file remains on disk as a fallback, so the operator is not locked out.

##### Manual testing required

The guide must be tested by the implementor to ensure every command (including nested binding syntax)
works end-to-end before deployment.

----

### 14: Remove credential-file guidance and update agent instructions

Update agent instructions in `dot` to remove references to `~/.agents/credentials.json` and to
document the CLI-mediated credential retrieval path via `dt creds fetch`. Document the configuration
paths (both `dt settings bind` for batch and `dt creds set` for individual) to operators. Add
corresponding guidance in `work-dot` for work credentials via both `wdt creds fetch` and configuration
methods.


#### Acceptance Criteria

- AC01: All references to `~/.agents/credentials.json` are removed from `dot` agent instructions.
- AC02: Agent instructions in `dot` document how to retrieve personal secrets via `dt creds fetch <key>`.
  They do not instruct agents to configure credentials.
- AC03: Agent instructions in `work-dot` document how to retrieve work secrets via `wdt creds fetch
  <key>`. They do not instruct agents to configure credentials.
- AC04: No agent-facing guidance directs an agent to read a plaintext credential file.
- AC05: Ignore rules in `.gitignore` that were created solely to hide `~/.agents/credentials.json` are
  removed or clarified (the file is no longer special-cased).
- AC06: Shell scripts and aliases that previously used `jq` against the credentials file are updated
  to use CLI commands.


#### Steps

1. Review `dot/.agents/instructions/*.md` and remove all guidance directing readers to read
   `~/.agents/credentials.json`.
2. Search `dot` for shell aliases or scripts that invoke `jq` against the credentials file and
   update them to use `dt creds fetch` or `wdt creds fetch` as appropriate.
3. In `dot`'s agent instructions, add a note: "Personal secrets are retrieved via `dt creds fetch
   <key>`. Work secrets (if McGraw Hill configuration is installed) use `wdt creds fetch <key>`
   analogously. Do not read `~/.agents/credentials.json` directly."
4. In `work-dot/.agents/instructions/work.md`, add: "Work secrets are retrieved via
   `wdt creds fetch <key>`. Do not read plaintext credential files."
5. Review `dot/.gitignore` for entries like `**/credentials.json` that were added only to hide the
   legacy file. If appropriate, add a comment explaining they are retained for historical reasons
   or remove them if no longer needed.
6. Search for any remaining hardcoded references to `~/.agents/credentials.json` in code or docs and
   remove them.
7. Commit changes to both `dot` and `work-dot`.


#### Technical Notes

- This is a documentation pass; the actual secret stores are already in place from earlier tasks.
- The guidance change is critical for long-term usability: agents and humans must know how to access
  secrets once the legacy file is deleted.
- Shell script updates are minor but important for compatibility.

----

### 15: Create end-to-end migration validation plan and acceptance

Design and execute an end-to-end validation of the entire migration, including repository split,
CLI configuration, secret migration, and cleanup.


#### Acceptance Criteria

- AC01: A comprehensive validation plan document exists that covers all aspects of the migration.
- AC02: The plan is tested on a scratch/test home directory or machine, not Tucker's production
  environment initially.
- AC03: Validation confirms:
   - `dt` alone works on a machine with `work-dot` absent.
   - `wdt` alone does not work (expected; it is optional).
   - Both `dt` and `wdt` work together when both are installed.
   - Agent sessions read both personal and work instructions when both are present.
   - Git config in work repos includes the work overlay.
   - `dt creds fetch` and `wdt creds fetch` return the expected values for all required keys.
   - After migration, `~/.agents/credentials.json` can be safely deleted.
   - Workflows that depended on the legacy file work correctly against the CLI-backed stores.
   - `dt` repo is publishable to public GitHub with no work-identifying content.
   - `work-dot` repo is private and contains all work-specific content.
- AC04: All tests pass (both unit and integration) on both CLIs.
- AC05: No uncommitted changes remain; all implementation work is committed to the appropriate
  feature branches. Pushes to remote repositories occur only when the user explicitly authorizes
  them.


#### Steps

1. Create a validation plan document `dot/docs/MIGRATION_VALIDATION.md` with:
   - Test environment setup (scratch home, test machines).
   - Validation steps for `dt` alone, `wdt` present/absent, and both together.
   - Checks for agent instructions, Git config, shell sourcing.
   - Secret migration and deletion validation.
   - Repository state checks (no work content in `dot`, all work content in `work-dot`).
2. Prepare a test environment:
   - Create a test home directory or use a virtual machine.
   - Ensure neither `dt` nor `wdt` are installed in the test environment initially.
3. Run step-by-step validation:
   - Install `dt` from the updated `dot` repo and run `dt configure`.
   - Verify no work-related output or content appears.
   - Verify `dt` alone is fully functional.
   - Install `wdt` from `work-dot` and run `wdt configure`.
   - Verify work configuration is applied correctly.
   - Verify both `dt` and `wdt` are functional together.
   - Run `dt settings bind` and `wdt settings bind` with test values.
   - Run `dt creds fetch` and `wdt creds fetch` and verify output.
   - Check agent sessions for both instruction files.
   - Verify Git uses work config in work repos.
   - Delete `~/.agents/credentials.json` and re-run dependent workflows.
   - Verify everything still works.
4. Document results in the validation plan.
5. If any step fails, debug and fix the issue, then re-run validation.
6. Once all steps pass, mark the migration as validated.
7. Commit validation results to the repository (or a branch).


#### Technical Notes

- Validation should be thorough but pragmatic; the goal is confidence that the migration works,
  not testing every edge case (that is covered by unit tests).
- Use a test home directory or VM to avoid contaminating Tucker's real environment during validation.
- If working on a branch, create a separate branch for integration work so the main implementation
  branches can be clean.

----

## Unknowns

**Typerdrive nested credentials support, binding syntax, and safe write/persist API**: Task 04 includes
critical research on Typerdrive's support for nested Pydantic models, especially the exact syntax for
binding to fields inside a nested sub-model, for programmatically reading from nested models, and for
safely writing/persisting nested fields. This research is resolved in-task (Task 04 steps 1–2), so it
does not block planning, but it remains an open question during planning that is resolved during
implementation. This research is **strictly blocking**: downstream tasks (05, 06, 13, 14) cannot proceed
with verified implementations until Task 04's findings are documented in Technical Notes.

Critical research questions for Task 04:

- **What is the exact structure of the existing `Settings` model in `dot`?** (Does it include inline
  credentials like `jira_info: JiraInfo`, or are credentials currently elsewhere?)
- **Can Typerdrive bind to nested Pydantic model fields?** (e.g., can `dt settings bind --credentials.jira_api_key
  <value>` target a field inside a nested `credentials` sub-model?)
- **What is the exact syntax for `dt settings bind` to update a nested field?** (Dotted path like
  `--credentials.jira_api_key`, or JSON-based like `--credentials '{"jira_api_key": "..."}'`?)
- **How does Typerdrive programmatically access nested model fields?** (needed for Task 06's credential
  seeding logic and Task 05's `creds set` write logic)
- **What is the exact API for safely writing/persisting nested model fields?** (needed for `creds set`
  to verify no partial writes, no file corruption, and atomic/transactional safety)
- **How does Typerdrive manage config directories for multiple CLIs?** (separate app names, config dirs,
  file paths?)
- **How does Typerdrive persist settings to disk and handle concurrent access/recovery?** (critical for
  `creds set` to guarantee settings remain byte-identical on validation failure)

Results are documented in Task 04 Technical Notes so Task 05, Task 06, Task 13, and later tasks use
verified, nested-model-aware syntax and safe APIs, not assumptions. **This research is blocking**: no
downstream implementation can proceed until Task 04's findings are documented.

All credential field names are enumerated during Task 13 (migration workflow) when the current
credential sources are audited. That audit informs the nested credentials model structure but the
schema is conservative (includes all known keys) so the implementation is not blocked if additional
keys are discovered later.


## Technical Notes

### Repository structure summary

After implementation, the two repositories will have this structure:

- **`dot` (public, `~/src/dusktreader/dot`)**:
  - `src/dot_tools/` — Python package for `dt` CLI.
  - `src/dot_tools/cli/main.py` — entry point; contains wdt detection and invocation logic.
  - `etc/install.yaml` — install manifest; no work-specific content.
  - `.gitconfig` — includes conditional include for work overlay.
  - `.agents/instructions/` — personal agent guidance only; no work-specific content.
  - Tests for new wdt-detection logic.

- **`work-dot` (private, `~/src/mhe/work-dot`)**:
   - `src/work_tools/` — Python package for `wdt` CLI.
   - `src/work_tools/cli/main.py` — entry point; no dependency on `dt`.
    - `src/work_tools/cli/creds.py` — credentials fetch sub-command group.
   - `src/work_tools/configure.py` — WorkInstaller class.
   - `src/work_tools/settings.py` — WorkSettings pydantic model.
   - `etc/install.yaml` — install manifest; work-specific symlinks and dotfiles.
   - `.workrc` — work shell environment.
   - `.gitconfig.work` — work Git configuration.
   - `.agents/instructions/work.md` — work-specific agent guidance.
      - Tests for WorkInstaller, credentials fetch, and integration.


### Credential migration sequence

The migration follows this sequence to minimize risk:

1. **Phase 1: Deploy both CLIs with nested credentials** — Install updated `dot` and new `wdt` with
   nested credentials sub-models. Legacy `~/.agents/credentials.json` remains untouched. Task 04
   research determines verified binding syntax.
2. **Phase 2: Transition existing `Settings` (if needed)** — If `dot`'s current `Settings` contains
   inline credential fields, migrate them to the nested credentials sub-model using the verified
   binding syntax from Task 04.
3. **Phase 3: Populate CLI-backed nested credential stores** — Run `dt settings bind --credentials.<field>
   <value>` and `wdt settings bind --credentials.<field> <value>` (exact syntax from Task 04) to
   populate personal and work nested credential stores from authoritative sources.
4. **Phase 4: Validate** — Run `dt creds fetch <key>` and `wdt creds fetch <key>` for every required
   credential and confirm values match expectations.
5. **Phase 5: Delete legacy** — Remove `~/.agents/credentials.json` and update all guidance
   (agents, scripts, shells) to remove references to it.

Until Phase 5 completes, the legacy file remains on disk and available as a fallback if Phase 4
fails. This minimizes the risk of being locked out during the cutover.


### Shell sourcing order

After both CLIs configure, shell startup will source:

1. `~/.extra_dotfiles` (added by both `dt` and `wdt`).
2. `~/.dot_misc`, `~/.dot_tools_helpers`, `~/.dot_colors`, `~/.dotrc` (from `dot`).
3. `~/.workrc` (from `work-dot`).
4. `~/.dotrc_local` (user-local overrides).

The order ensures `dot` sets up the personal base first, then `work-dot` overlays work-specific
settings. Local overrides come last so the user can customize both layers.


### Git config conditionals

Git config layering works through Git's built-in `includeIf`:

1. `~/.gitconfig` — loaded by Git at startup.
2. `~/.gitconfig.dusktreader` — sourced from `~/.gitconfig` for personal config.
3. `[includeIf "gitdir:~/src/mhe/"] path = ~/.gitconfig.work` — conditional include for work repos.
4. `~/.gitconfig.work` — sourced when Git is running inside `~/src/mhe/`.

This ensures work repos see work identity and work-specific settings, while personal repos see
personal config. The conditional include is "silent fail" — if the work overlay is absent,
Git continues without error.


### Testing strategy

Tests are organized by layer:

- **Unit tests**: Individual functions and classes (DotInstaller, WorkInstaller, credentials fetch,
  credential seeding).
- **Integration tests**: Full `dt configure` and `wdt configure` flows on scratch home directories.
- **Manual acceptance**: Full end-to-end validation on test machine or VM.

Unit tests use temporary directories and mocked typerdrive clients to avoid touching real state.
Integration tests use `--override-home` to isolate from the real home. Manual acceptance is the
final confirmation on Tucker's actual machine or a production-like environment.


### Exit codes and error handling

Both CLIs follow these conventions:

- Exit code 0: Success.
- Exit code 1: Configuration error (missing required file, invalid option, etc.).
- Exit code 2: Runtime error (credential not found, seeding failed, subprocess invocation failed, etc.).

The `dt configure` command propagates the exit code from `wdt configure` if `wdt` is present and
fails, ensuring errors are visible to the caller.


### Bare creds group invocation behavior (AC29/AC30)

Both `dt creds` and `wdt creds` must behave identically when invoked with no subcommand and no arguments:

- Exit code is zero (success).
- Output is the `creds` command group's help text (identical to what `--help` produces).
- No action occurs on the credentials store: no reads, writes, or mutations.
- The credentials store remains byte-identical before and after invocation.
- The `creds` group is a pure wrapper: it contains only `fetch` and `set` sub-commands and performs
  no default behavior.

Implementation uses Typer's `invoke_without_command` pattern (or equivalent) to ensure that when the
group is invoked without a subcommand, help is displayed and the CLI exits successfully without
executing any credentials logic. Tests verify this behavior by:

1. Capturing the store state before bare invocation (hash or byte-for-byte snapshot).
2. Invoking `dt creds` or `wdt creds` with no arguments.
3. Verifying exit code is zero.
4. Verifying output matches `dt creds --help` or `wdt creds --help` (identical, not just similar).
5. Capturing the store state after invocation and confirming it matches the pre-invocation state
   byte-for-byte (no store access occurred).

This ensures both CLIs have one consistent contract for bare invocation across both applications,
consistent with design plan AC29 and AC30.


### Typerdrive integration details

Typerdrive provides:

1. **Settings models** — Pydantic BaseModel subclasses (Settings in `dt`, WorkSettings in `wdt`).
2. **Application context** — Automatic config directory management (app-specific per CLI).
3. **Settings sub-commands** — `dt settings` and `wdt settings` auto-added by `add_settings_subcommand()`.
4. **Logging context** — `attach_logging()` and `log_error()` decorators.

Settings are persisted to the app's config directory (typically `~/.config/dot-tools/` for `dt` and
`~/.config/work-tools/` for `wdt` or similar). Each CLI has its own app name and config namespace,
so personal and work settings do not mix.

The `creds fetch` and `creds set` commands are not Typerdrive built-ins; they are custom
application-owned sub-commands that read from or write to named fields in the nested credentials
sub-model within the settings model. The implementation is thin and straightforward, delegating to
Typerdrive's settings access and write APIs. No claim is made that these commands are Typerdrive-provided;
they are entirely application-owned. Task 04 research (step 1) must validate safe write/persist APIs.


### Task 04 research findings (critical, blocking gate)

Task 04 steps 1–2 research the Typerdrive API, nested model support, `Settings` model, and safe
write/persist APIs, documenting findings in Task 04 Technical Notes that are **required** before any
downstream task proceeds:

- **Nested credentials support** — Whether Typerdrive can bind to and read from fields inside a nested
  Pydantic sub-model. This is the critical blocker; if unsupported, the entire nested credentials
  design requires rework.
- **Exact `Settings` structure** — Whether the current `Settings` uses nested models (e.g., `jira_info:
  JiraInfo`). This informs whether the dot repository needs to transition existing inline credentials
  to a nested model.
- **Nested bind syntax** — Exact command-line syntax for `dt settings bind` to update a field inside
  a nested sub-model (e.g., `--credentials.jira_api_key <value>` or `--credentials
  '{"jira_api_key": "..."}'`).
- **Nested field access and programmatic write APIs** — How to programmatically iterate over, read,
  and safely write fields inside a nested credentials sub-model (needed for Task 06's credential
  seeding and Task 05's `creds set` write logic).
- **Safe write/persist guarantees** — Exact APIs and behavior for safely writing nested model fields,
  with verification that writes are atomic, file corruption is prevented, and settings remain
  byte-identical on validation failure (critical for `creds set` tests that verify settings unchanged
  on unknown-key error).
- **Available `settings` sub-commands** — Confirmed list of commands Typerdrive auto-generates (bind,
  update, unset, reset, show; note: `set` is application-owned, not Typerdrive-provided).
- **Config directory isolation** — How Typerdrive manages app-specific config dirs and settings file
  paths, ensuring `dt` and `wdt` have separate stores with no cross-access.

All downstream work (Tasks 05, 06, 13, 14, and beyond) uses verified, nested-model-aware syntax and
safe APIs from Task 04 Technical Notes, not assumptions. This prevents silent failures in credential
binding and migration (high-risk operations) and ensures the nested credentials design is
Typerdrive-compatible and operationally safe.
