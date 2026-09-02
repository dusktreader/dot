# Implementation Journal: Configure passwordless sudo safely

This journal records execution of the approved sudoers configuration task plan without modifying the live host sudoers
files.


## Source plan

`.artifacts/20260901--configure-sudoers/task-plan.md`


## Status

**Complete**: The standalone configurator, manifest integration, isolated tests, and installer cleanup are implemented.
The worktree remains uncommitted and no production invocation was run.


## Tasks

### Task 01: Add isolated fixture tests

#### Status

**Complete**


#### Overview

Added `tests/test_install.py` with temporary sudoers trees. The harness patches module paths and ownership only after
loading the standalone script, so tests cannot write to `/etc`.


#### Steps taken

- Added the fixture-tree loader and argument-aware command runner.
- Added the initial contract and fixture tests.
- Ran the focused tests before implementation and confirmed the manifest and legacy-block assertions failed.


#### Files modified

- CREATED: `tests/test_install.py`


#### Acceptance criteria validation


#### Satisfied AC07: Isolated tests cover the required behavior

The final module run passed 19 tests, including fixture isolation, platform handling, parsing, safety, validation,
restoration, identity, escalation, idempotence, and preservation cases.


### Task 02: Add the mocked command runner

#### Status

**Complete**


#### Overview

`RecordingRunner` records exact command arguments and supplies configured return codes for current, candidate, and final
`visudo` validation.


#### Steps taken

- Recorded every subprocess argument list and result.
- Added missing-command and authentication-failure coverage.
- Confirmed no test invokes `sudo`, `visudo`, or a live production path.


#### Files modified

- UPDATED: `tests/test_install.py`


### Task 03: Test the standalone script contract

#### Status

**Complete**


#### Overview

Tests cover the uv shebang, empty PEP 723 dependency declaration, supported platforms, unsupported platforms, root
execution, and noninteractive sudo re-execution.


#### Steps taken

- Asserted the exact shebang and standard-library-only metadata.
- Tested Darwin and Linux paths through the harness.
- Tested noninteractive `sudo -n` re-execution and clear failure reporting.


#### Files modified

- CREATED: `tools/configure-sudoers.py`


### Task 04: Implement include parsing and preservation

#### Status

**Complete**


#### Overview

The script recognizes active Linux and macOS include spellings, removes duplicate owned directives, writes one canonical
directive, and preserves unrelated bytes and drop-ins.


#### Steps taken

- Added a narrow active-include regular expression rather than a general sudoers parser.
- Accepted `/etc/sudoers.d` and `/private/etc/sudoers.d` with optional trailing comments.
- Added creation and duplicate-collapse coverage.


#### Files modified

- UPDATED: `tools/configure-sudoers.py`
- UPDATED: `tests/test_install.py`


### Task 05: Implement managed-path safety and rule content

#### Status

**Complete**


#### Overview

The configurator checks root ownership, file types, symlinks, and write permissions before touching the sudoers files.
It
uses fixed `90-dotfiles` and writes the exact invoking-user rule.


#### Steps taken

- Added safe checks for the main file, include directory, and managed drop-in.
- Added safe creation of a missing include directory with mode `0755`.
- Resolved identity through `SUDO_UID`, `SUDO_USER`, or the current UID, never `$USER`.


#### Files modified

- UPDATED: `tools/configure-sudoers.py`
- UPDATED: `tests/test_install.py`


### Task 06: Implement validation and atomic transaction behavior

#### Status

**Complete**


#### Overview

The script validates the existing configuration, both same-directory candidates, and the installed result. It atomically
replaces only changed managed files and restores prior content after failures.


#### Steps taken

- Added bounded noninteractive `visudo -c` and `visudo -c -f` execution.
- Added same-directory temporary files, metadata preservation, and atomic replacement.
- Added candidate-validation, final-validation, restoration, and idempotent-rerun tests.


#### Files modified

- UPDATED: `tools/configure-sudoers.py`
- UPDATED: `tests/test_install.py`


### Task 07: Implement the production script

#### Status

**Complete**


#### Overview

`tools/configure-sudoers.py` is a standalone standard-library script with explicit Darwin/Linux checks, privilege
handling, parsing, validation, safety checks, and transaction logic.


#### Steps taken

- Kept fixture paths and identity substitutions in the test harness.
- Avoided `sudo tee` and interactive `visudo` editing.
- Confirmed normal execution was not run against the host.


#### Files modified

- CREATED: `tools/configure-sudoers.py`


### Task 08: Integrate the setting

#### Status

**Complete**


#### Overview

Added one `passwordless sudo` setting using the existing `DotInstaller._apply_settings` environment and quoted
`$DOT_ROOT` commands.


#### Steps taken

- Added the exact `--check` command and generic execution command to `etc/install.yaml`.
- Added a manifest assertion to the isolated tests.


#### Files modified

- UPDATED: `etc/install.yaml`
- UPDATED: `tests/test_install.py`


### Task 09: Remove the legacy installer block

#### Status

**Complete**


#### Overview

Removed only the username-derived passwordless sudo block from `install.sh`. Ordinary package-install `sudo` commands
remain unchanged.


#### Steps taken

- Removed the `sudo grep`, username-derived `sudo tee`, and related status messages.
- Added assertions that the legacy block and username-derived write are absent.


#### Files modified

- UPDATED: `install.sh`
- UPDATED: `tests/test_install.py`


### Task 10: Run verification and record results

#### Status

**Complete**


#### Overview

All required verification commands passed. The task plan was not modified, no commit or push was performed, and no
unrelated pre-existing test failure was observed in the required checks.


#### Steps taken

- Ran the focused sudoers tests during development.
- Ran the complete required `tests/test_install.py` module.
- Ran shell syntax validation and Ruff.
- Inspected the worktree to confirm only planned files plus the journal are changed.


#### Files modified

- CREATED: `.artifacts/20260901--configure-sudoers/task-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Standalone uv script and standard-library dependencies

`tests/test_install.py::test_sudoers_contract_has_uv_shebang_and_no_dependencies` passed. The script begins with the
required
shebang and declares `dependencies = []` in inline PEP 723 metadata.


#### Satisfied AC02: Manifest integration and legacy removal

`tests/test_install.py::test_sudoers_manifest_contains_passwordless_sudo_setting` and
`tests/test_install.py::test_sudoers_install_script_has_no_username_derived_write` passed. The manifest has one setting
with both quoted `$DOT_ROOT` commands, and the old block is absent.


#### Satisfied AC03: Platform, identity, escalation, and failures

The Darwin, unsupported-platform, noninteractive sudo, sudo failure, and identity fixture tests passed. The production
entry point rejects unsupported systems and uses `sudo -n` when not root.


#### Satisfied AC04: Check mode and include behavior

The check-mode creation and active-configuration tests passed. Include parsing tests cover Linux, Darwin, private-etc
spelling, comments, duplicates, unrelated paths, and preservation.


#### Satisfied AC05: Exact safe managed rule

`tests/test_install.py::test_sudoers_linux_creates_include_and_exact_managed_rule` and both unsafe-path tests passed.
The fixed
drop-in is `90-dotfiles`, mode `0440`, and contains exactly the expected dotted username rule.


#### Satisfied AC06: Validation, atomic replacement, metadata, and restoration

The candidate-validation, final-validation, invalid-existing-config, and idempotent-rerun tests passed. The
implementation uses same-directory temporary files, atomic replacement, and restoration without `sudo tee`.


#### Satisfied AC07: Isolated required coverage

`uv run pytest tests/test_install.py --no-cov -k sudo` passed with `18 passed, 1 deselected`. The complete module then
passed with `19 passed`. All command execution was mocked and fixture paths were patched in the harness, not exposed as
production CLI overrides.


#### Satisfied AC08: Required verification and journal

`bash -n install.sh` exited 0. `uv run pytest tests/test_install.py --no-cov` passed with 19 tests. `uv run ruff check
src tests` exited 0 with `All checks passed!`. This journal records the implementation and exact results.


#### Additional notes

The first focused test run failed as intended before implementation: the manifest entry was absent and the legacy
installer write was still present. An early fixture helper yielded the `etc` directory instead of the sudoers file; the
harness was corrected before final verification. No unrelated repository failures occurred in the required checks.


## Final QA pass

The final QA pass was run once against the current worktree. No production script was run, and live `/etc/sudoers` was
not accessed for modification.

- `bash -n install.sh`: exit 0.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; 32 passed.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no whitespace errors.

No QA fixes were required. No acceptance-criteria regressions or straightforward defects were exposed. The plan was not
modified, and no commit or push was performed.


## Review remediation

The independent review identified nine findings. The implementation now addresses each finding:

- Set `tools/configure-sudoers.py` to mode `0755` and added a direct executable `--help` test that does not configure
  sudoers.
- Built a temporary include tree containing the staged `90-dotfiles` rule and unrelated regular drop-ins, then validated
  a main candidate that points to that tree before any live replacement.
- Limited `/private/etc/sudoers.d` recognition to Darwin and require it to resolve to the configured include directory.
  Linux treats that spelling as unrelated content.
- Applied an argument-aware mocked runner to every fixture test that enters configuration. No fixture test invokes a
  live
  `visudo` or other host command.
- Added coverage for direct execution, active check forms, invoking identity, candidate bytes and paths, metadata
  restoration, candidate cleanup, and filesystem failure reporting.
- Converted expected process and filesystem failures to controlled configuration errors and cleaned all candidates in
  guarded setup and transaction paths.
- Made `--check` count exactly one active target include rather than compare normalized bytes, so valid aliases,
  directive
  forms, and trailing comments pass without writes.
- Tracked completed replacements and restored only those paths, including the managed file's prior mode, owner, and
  group.
- Rejected unsupported operating systems before attempting sudo re-execution.

The plan and production paths remain unchanged by test fixture substitutions. No live-system configuration was run.


## Remediation verification

- `uv run pytest tests/test_install.py --no-cov -k sudo`: exit 0; 31 passed, 1 deselected.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; 32 passed.
- `bash -n install.sh`: exit 0.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no whitespace errors.
- `stat -f '%Sp %OLp %N' tools/configure-sudoers.py`: `-rwxr-xr-x 755`.


## Post-remediation QA

QA was rerun against the current worktree on 2026-09-01 with the `--personal-luna` model variant. The production
configurator was not run, and live `/etc/sudoers` was not modified.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `32 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

No straightforward QA defects were found, so no remediation changes were made. The approved plan was not modified. No
commit or push was performed.


## Compact re-review remediation

The compact re-review left C05 and C06 partially unresolved. This pass addressed those findings without changing the
approved plan or review artifact.


### C05 coverage

- Added Darwin `@includedir` creation and duplicate-active-target preservation tests.
- Added `SUDO_USER` and current-UID identity fallback tests alongside `SUDO_UID` coverage.
- Added missing-`sudo`, missing-`visudo`, command `OSError`, and non-root unsupported-platform tests.
- Added real fixture mode checks for the main file, include directory, and managed drop-in, plus an ownership seam using
  the actual fixture owner and an alternate configured root UID.
- Strengthened the mocked runner to reject unexpected commands, require readable `visudo -f` candidates, and record
  candidate paths and bytes. No fixture configurator test can invoke host `sudo` or `visudo`.


### C06 robustness

- Guarded configuration and transaction reads, candidate directory operations, writes, metadata changes, replacements,
  restoration, and cleanup with clear `ConfigurationError` boundaries.
- Made temporary-file and temporary-directory cleanup best-effort so cleanup errors do not mask the original failure.
- Tracked completed replacements, restored only changed paths with their original content and metadata, and reported
  restoration failures while retaining the original exception as the cause.
- Removed a newly created include directory after a failed transaction when it remains empty, while preserving existing
  include-directory and main-file metadata.


### Remediation verification

- `uv run pytest tests/test_install.py --no-cov -k sudo`: exit 0; 44 passed, 1 deselected.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; 45 passed.
- `bash -n install.sh`: exit 0; no output.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

Changed files in this remediation are `tools/configure-sudoers.py`, `tests/test_install.py`, and this task journal.
The task plan and review artifact were not modified. No production configurator, live `/etc/sudoers`, commit, or push
was used.


## Final targeted remediation

Resolved C05 and C06 from `code-review--01.md` using the `--personal-luna` variant. Added isolated tests for FIFO-backed
main, include, and managed paths; main and managed `os.replace` failures; restoration failure reporting; exact atomic
replacement arguments; successful main mode, owner, and group preservation; include-directory creation failures;
post-creation failure cleanup; candidate cleanup failure reporting; and candidate/restoration state after injected
failures. The command runner remains argument-aware and fully mocked.

Hardened the configurator so include-directory creation cleans up after ownership, mode, or revalidation failure. All
post-creation resolution, reads, parsing, preparation, validation, replacement, restoration, and cleanup now run inside
one failure cleanup scope. Cleanup reports paths that remain while preserving the primary error. Restoration errors now
include the primary failure and retain it as `__cause__`; temporary-file cleanup reports its own failure as well.

Final verification:

- `uv run pytest tests/test_install.py --no-cov -k sudo`: exit 0; 56 passed, 1 deselected.
- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; 57 passed.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

Changed files remain `tools/configure-sudoers.py`, `tests/test_install.py`, and this task journal. The plan and review
artifact were not modified. The production configurator was not run, live `/etc/sudoers` was not touched, and no
commit or push was performed.


## Final QA pass

The required final QA pass ran against the current worktree on 2026-09-01 with the `--personal-luna` variant. No
production configurator was run, and live `/etc/sudoers` was not modified.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `57 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

No straightforward QA defects were exposed, so no fixes were made. The task plan and review artifact were not
modified. No commit or push was performed.


## Post-revision QA

Post-revision QA ran on 2026-09-01 with the `--personal-luna` variant against the current worktree. The revision adds
the inline PEP 723 dependency `py-buzz>=8.0`, derives `ConfigurationError` from `Buzz`, and uses
`ConfigurationError.check_expressions()` in `require_safe_path()`. The direct executable `--help` test verifies the
standalone dependency path, and the safe-path test verifies the Buzz exception behavior. No production configurator was
run, and live `/etc/sudoers` was not modified.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `58 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

No straightforward QA defects were exposed, so no fixes were made. Only this journal was updated. The task plan and
review artifact were not modified. No commit or push was performed.


## Live verification attempt

The explicitly requested live verification began with the non-mutating check:

```shell
./tools/configure-sudoers.py --check
```

The command reported that the desired configuration is not active, then failed at the required noninteractive privilege
boundary because this shell had no cached sudo authorization:

```text
Error : configure-sudoers: desired sudoers configuration is not active
Error : configure-sudoers: noninteractive sudo authentication failed
```

No sudoers file was modified. Normal execution was not attempted after the authentication failure. Authenticate in a
terminal with `sudo -v`, then rerun `./tools/configure-sudoers.py --check` before any normal execution attempt.


## Post-revision QA

Post-revision QA ran on 2026-09-02 with the `--personal-luna` variant against the current worktree. The revision adds
`rich>=14.0` to the standalone script's inline PEP 723 metadata, imports Rich `Console` and `Text`, and changes
`fail()` to print a red `Error` prefix. `test_sudoers_errors_use_rich_red_error_prefix` verifies the Rich output
objects and their exact text and style. The direct executable `--help` path also verified uv-script dependency
resolution without configuring sudoers. No production configurator was run, and live `/etc/sudoers` was not modified.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `59 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.
- `./tools/configure-sudoers.py --help`: exit 0; help displayed; no configuration performed.

No straightforward QA defects were exposed, so no fixes were made. Only this journal was updated. The task plan and
review artifact were not modified. No commit or push was performed.


## Post-revision QA

Post-revision QA ran on 2026-09-02 with the `--personal-luna` variant against the current worktree. The revision makes
missing paths fail in `require_safe_path()` by default with `ConfigurationError`, while `allow_missing=True` remains an
explicit seam for optional include-directory and managed-drop-in creation. The tests cover both required and optional
missing paths. The direct executable `--help` path also passed through the test suite without configuring sudoers.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `59 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

No straightforward QA defects were exposed, so no fixes were made. Only this journal was updated. The task plan and
review artifact were not modified. No production configurator was run, live `/etc/sudoers` was not modified, and no
commit or push was performed.


## Post-revision QA

Post-revision QA ran on 2026-09-02 with the `--personal-luna` variant against the current worktree. The revision adds
overloads to `require_safe_path()`: default calls return `os.stat_result`, while explicit `allow_missing=True` calls
return `os.stat_result | None`. The revision removes the previous type-ignore suppression. No production configurator
was run, and live `/etc/sudoers` was not modified.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `59 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `uv run ty check tools/configure-sudoers.py`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

No straightforward QA defects were exposed, so no fixes were made. Only this journal was updated. The task plan and
review artifact were not modified. No commit or push was performed.


## Post-revision QA

Post-revision QA ran on 2026-09-02 with the `--personal-luna` variant against the current worktree. The revision
simplifies `require_safe_path()` to one signature with `allow_missing: bool = False` and return type
`os.stat_result | None`, removing the Literal overloads. Required callers explicitly assert or handle non-`None`
metadata. Optional callers pass `allow_missing=True`. The unused `include_metadata` parameter was removed from
`install()` and `configure_existing_paths()`. Root and managed `stat_result` fields remain the source of file metadata;
include-directory metadata is not threaded through the transaction. No production configurator was run, and live
`/etc/sudoers` was not modified.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `59 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `uv run ty check tools/configure-sudoers.py`: initially reported the missing root-metadata narrowing; after adding
  the explicit assertion, exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

The only straightforward QA defect was the missing explicit non-`None` assertion for required root metadata; it was
fixed in `tools/configure-sudoers.py`. The task plan and review artifact were not modified. No commit or push was
performed.


## Post-revision QA

Post-revision QA ran on 2026-09-02 with the `--personal-luna` variant against the current worktree. The revision
replaces
stat-result plumbing with path-based APIs: `install()` accepts `sudoers_path` and `managed_path` and retrieves root and
managed metadata at the point of use, while `configure_existing_paths()` also accepts paths. `ensure_include_dir()` no
longer returns an unused stat result. `require_safe_path()` remains a plain optional-result helper so optional callers
can distinguish absence. No production configurator was run, and live `/etc/sudoers` was not modified.

The implementation preserves root metadata for candidate creation and rollback, and managed metadata for replacement
decisions and rollback. Include-directory metadata is not threaded through the transaction. Existing fixture tests
invoke
the path-based APIs through the normal configuration flow, with all configurator subprocesses mocked.

- `bash -n install.sh`: exit 0; no output.
- `uv run pytest tests/test_install.py --no-cov`: exit 0; `59 passed`.
- `uv run ruff check src tests`: exit 0; `All checks passed!`.
- `uv run ty check tools/configure-sudoers.py`: exit 0; `All checks passed!`.
- `git diff --check`: exit 0; no output.

No straightforward QA defects were exposed, so no fixes were made. Only this journal was updated. The task plan and
review artifact were not modified. No commit or push was performed.
