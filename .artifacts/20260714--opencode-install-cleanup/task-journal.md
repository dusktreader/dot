# Implementation Journal: Clean OpenCode dependency installation

This journal records execution of the approved OpenCode dependency installation cleanup plan.


## Source plan

`.artifacts/20260714--opencode-install-cleanup/task-plan.md`


## Status

**Complete**: All implementation tasks and required validations finished. The Markdown validator
reported pre-existing violations in the requested directories and the journal's required AC headings. Review findings
S01, S02, and T01 were resolved in the follow-up pass.


## Tasks


### Task 01: Add focused installer tests

#### Status

**Complete**


#### Overview

Added override-home coverage for the OpenCode dependency check and installation command.


#### Steps taken

- Added tests asserting the check uses the installer home.
- Added tests asserting the install script and subprocess environment use the installer home.
- Ran the focused test module after implementation.


#### Files modified

- UPDATED: `tests/test_configure.py`


#### Acceptance criteria validation

##### Satisfied AC02: Focused tests verify the OpenCode npm tool resolves its location from installer home

`tests/test_configure.py::TestDotInstallerInstallTools` covers both check and install subprocess paths.


### Task 02: Update the install manifest

#### Status

**Complete**


#### Overview

Changed the OpenCode npm tool to use `$HOME/.config/opencode` while retaining its node dependency and package version.


#### Steps taken

- Updated the manifest check command.
- Updated the manifest npm prefix.
- Preserved the node dependency and package metadata.


#### Files modified

- UPDATED: `etc/install.yaml`


#### Acceptance criteria validation

##### Satisfied AC01: OpenCode npm commands use the target home

The manifest now references `$HOME/.config/opencode` and no longer references the repository OpenCode path.


### Task 03: Make tool subprocesses honor override-home

#### Status

**Complete**


#### Overview

Passed the installer home as `HOME` to both tool checks and installation scripts.


#### Steps taken

- Added `HOME` to the installer subprocess environment.
- Passed that environment to tool checks.
- Preserved `DOT_ROOT` for unrelated tools.


#### Files modified

- UPDATED: `src/dot_tools/configure.py`


#### Acceptance criteria validation

##### Satisfied AC02: Override-home subprocess behavior is covered

Focused tests verify the environment passed to both `subprocess.run` and `subprocess.Popen`.


### Task 04: Ignore and remove local npm artifacts

#### Status

**Complete**


#### Overview

Added explicit ignore rules. Artifact removal and isolated installation validation remain.


#### Steps taken

- Added ignore rules for repository-local `node_modules` and `package-lock.json`.
- Removed the repository-local dependency artifacts after confirming both paths are ignored.
- Ran isolated configure validation with a temporary override home; npm created the dependency there.


#### Files modified

- UPDATED: `.gitignore`


#### Acceptance criteria validation

##### Satisfied AC04: Local artifacts are ignored and absent

`git check-ignore` matched both paths, and final `git status --short` reports neither artifact.


### Task 05: Preserve existing working-tree changes and validate

#### Status

**Complete**


#### Overview

Existing unrelated OpenCode and agent changes have not been modified.


#### Steps taken

- Inspected the initial working tree before editing.
- Limited changes to the planned installer, manifest, tests, ignore rules, and journal.
- Confirmed the existing plugin, agent, and Markdown-validator changes remain in the working tree.
- Ran the focused tests, full tests, Ruff, type checks, and isolated configure validation.


#### Files modified

- CREATED: `.artifacts/20260714--opencode-install-cleanup/task-journal.md`


#### Acceptance criteria validation

##### Satisfied AC05: Isolated configure installs dependency artifacts under override home

`uv run dt configure --override-home <temporary home>` completed successfully. The package symlink,
plugin directory, and lockfile were created under the temporary home, with no repository artifacts.


##### Satisfied AC06: Existing working-tree changes remain present

Final status retains both plugins, agent updates, `.agents/tools/check-markdown-format.mjs`, and the
associated documentation changes.


##### Satisfied AC07: Python quality checks pass

`uv run pytest` passed with 169 tests. `uv run ruff check src tests` and `uv run ty check src` both
passed with no errors.


#### Additional notes

The focused test command passed all 49 tests but failed its module-wide coverage threshold because
that command does not exercise the full suite. The full suite passed and met the 70% threshold.

The requested Markdown validator exited nonzero because the existing `.agents` and OpenCode agent
files contain many pre-existing formatting violations. It also flagged the journal's `#####` AC
headings, which the canonical journal format requires. No unrelated Markdown files were changed.


## Reviewer outcomes

### S01: Settings checks honor override home

**Resolved**: `_apply_settings` now builds the installer environment with the override-home `HOME` and passes it to
both settings check and install subprocesses. A focused test verifies the check environment.


### S02: Staleness guard uses input arguments

**Resolved**: The `tool.execute.before` hook now passes `input.args` to `extractPaths`.


### T01: OpenCode npm ignore rules are grouped

**Resolved**: The OpenCode `node_modules` and lockfile rules now sit together in a labelled local npm artifacts block.


### T02 and T03

**Deferred**: These non-blocking review observations were outside the requested S01, S02, and T01 fix scope.
