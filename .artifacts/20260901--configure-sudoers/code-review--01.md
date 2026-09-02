# Code Review: Configure passwordless sudo safely

This independent review compares the current worktree diff with the approved plan, original requirements, and execution
journal, with emphasis on privileged file handling and test isolation.

**Iteration 01**

**Reviewer variant**: `--personal-luna` (`opencode/gpt-5.6-luna`)


## Source

- `tools/configure-sudoers.py`
- `tests/test_install.py`
- `etc/install.yaml`
- `install.sh`
- `.artifacts/20260901--configure-sudoers/task-plan.md`
- `.artifacts/20260901--configure-sudoers/task-journal.md`
- `/Users/tucker.beck/src/dusktreader/dot/sudoers-prompt.md`
- `src/dot_tools/configure.py` (settings execution context)


## Verification Evidence

```text
Tests:       uv run pytest tests/test_install.py --no-cov  → 19 passed, 0 failed
Shell:       bash -n install.sh                           → exit 0
Linter:      uv run ruff check src tests                  → All checks passed!
Diff check:  git diff --check                             → exit 0
Build:       skipped (no project-documented build command)
Type check:  skipped (no project-documented type-check command)
Coverage:    skipped (the required test command uses --no-cov; no project-documented coverage command)
```

The reviewer did not run the configurator against the live system. The test suite is not fully isolated from live
`visudo` execution; see C04.


## Issue Summary

- **Critical**:    6
- **Significant**: 3
- **Trivial**:     0


## Findings

### Summary

| Finding | Title                                                                | Outcome |
| ------- | -------------------------------------------------------------------- | ------- |
| C01     | Standalone configurator is not executable                            |         |
| C02     | Complete sudoers candidate does not contain the staged drop-in       |         |
| C03     | Linux accepts a distinct `/private/etc` include directory            |         |
| C04     | Fixture tests invoke the host `visudo`                               |         |
| C05     | Required security and transaction behaviors lack meaningful tests    |         |
| C06     | Filesystem and command failures can escape with temporary files left |         |
| S01     | `--check` rejects valid active include forms                         |         |
| S02     | Rollback rewrites unchanged files and loses managed metadata         |         |
| S03     | Unsupported-platform validation happens after sudo re-execution      |         |


### Critical

#### C01: Standalone configurator is not executable


#### Where

`tools/configure-sudoers.py` (mode `0644`); `etc/install.yaml:341`


#### Evidence

`stat` reports `-rw-r--r-- 644 tools/configure-sudoers.py`. The manifest invokes the file directly as
`"$DOT_ROOT/tools/configure-sudoers.py"`, and `DotInstaller._apply_settings` runs that command through the shell.


#### Issue

The new file has a shebang but no executable permission. Loading it through `importlib` in the tests bypasses the
permission that the production settings path requires.


#### Impact

`dt configure` reaches the setting, fails to execute the file with `Permission denied`, and never configures sudo.
This violates AC02 and makes the feature nonfunctional on a normal installer run.


#### Fix

Set the file's executable mode, and add a test that asserts the owner execute bit or runs the script's non-privileged
`--help` path through the same direct invocation used by the manifest.


#### Outcome

Pending principal resolution.


#### C02: Complete sudoers candidate does not contain the staged drop-in


#### Where

`tools/configure-sudoers.py:24,151-158`


#### Evidence

The main candidate contains the canonical include for the live `/etc/sudoers.d` directory. The managed candidate is
created as a hidden `.90-dotfiles.*` file in that directory, then the main candidate is validated with
`visudo -c -f` before either replacement. The candidate main file therefore reads the current live drop-ins, not the
new managed rule. Sudoers includedir processing also ignores the dot-prefixed temporary file.


#### Issue

The pre-replacement main validation is not validation of the proposed complete configuration. It validates a main file
against the old live managed file, or no managed file, while the separate managed candidate is validated independently.


#### Impact

AC06's required composite candidate check is absent. A successful pre-replacement check does not prove that the exact
main file and exact `90-dotfiles` content about to be installed work together. The final check detects problems only
after the privileged replacements.


#### Fix

Build a temporary candidate include tree, place the managed candidate at the included filename, point a temporary main
candidate at that tree, and run `visudo -c -f` against that complete candidate. Keep the final live validation as a
post-replacement check. Make the test runner inspect candidate paths and bytes rather than only returning call-order
status codes.


#### Outcome

Pending principal resolution.


#### C03: Linux accepts a distinct `/private/etc` include directory


#### Where

`tools/configure-sudoers.py:20-26,109-125`


#### Evidence

`ACTIVE_INCLUDE` accepts both `/etc/sudoers.d` and `/private/etc/sudoers.d` without consulting the platform or
resolving either path. `rewrite_includes` then replaces either spelling with `#includedir /etc/sudoers.d`.


#### Issue

The requirement permits the macOS spelling only when it refers to the same directory as `/etc/sudoers.d`. The parser
does not verify that condition, and it applies the alias on Linux too.


#### Impact

On a Linux host where `/private/etc/sudoers.d` exists as a distinct directory, normal execution silently stops loading
that directory's drop-ins and starts loading `/etc/sudoers.d` instead. That can remove unrelated sudo policy and apply
the managed rule to a different directory during a privileged rewrite.


#### Fix

Treat `/private/etc/sudoers.d` as an alias only on Darwin after confirming that it resolves to the configured include
directory. On Linux, accept only `/etc/sudoers.d`. Add a fixture with distinct Linux paths and assert that it is
rejected
or left untouched rather than canonicalized.


#### Outcome

Pending principal resolution.


#### C04: Fixture tests invoke the host `visudo`


#### Where

`tests/test_install.py:66-73,200-211`; `tools/configure-sudoers.py:195-199`


#### Evidence

`test_sudoers_check_does_not_modify_fixture` calls `module.main(["--check"])` without patching
`module.subprocess.run`. The configurator unconditionally calls `validate_with_visudo()`, which runs bare `visudo -c`
against the host configuration. The two unsafe-path tests also call `module.main([])` without a runner patch. The
review environment has `/usr/sbin/visudo`, so these tests invoke a real host command instead of the fixture runner.


#### Issue

Patching the configurator's path constants does not redirect a bare `visudo -c`. These tests are host-dependent and can
read live `/etc/sudoers`; they do not prove that the fixture behavior was exercised.


#### Impact

AC07 and the original test isolation requirement are violated. A host permission or syntax failure can make a fixture
test pass before it reaches the code under test, and the suite performs live sudoers access despite the journal's claim
that no test invokes `visudo`.


#### Fix

Patch the command runner for every test that enters `configure`, including the negative safety tests. Make the fixture
runner fail if an unmocked process is attempted, and assert that all validation commands use fixture candidates or the
mocked live-validation result.


#### Outcome

Pending principal resolution.


#### C05: Required security and transaction behaviors lack meaningful tests


#### Where

`tests/test_install.py:86-247`


#### Evidence

The 19 passing tests do not cover the required `SUDO_UID`/`SUDO_USER` identity cases, main-file symlink/ownership/mode
checks, include-directory ownership/mode/type checks, managed-file ownership/mode/type checks beyond symlinks, missing
`sudo`, write failures, Darwin `@includedir` creation, or metadata and directory-mode preservation. The
`RecordingRunner` returns codes by call order; assertions at lines 97-102 inspect only command prefixes and never
inspect
candidate contents or exact `-f` paths. No test verifies atomic replacement itself.


#### Issue

The test suite exercises the happy path and selected failure returns, but it does not genuinely prove the security,
identity, candidate, atomicity, and metadata requirements listed in AC07. The fixture also patches `ROOT_UID` and
`os.chown`, so it cannot by itself establish production ownership behavior.


#### Impact

The passing count and journal's AC07/AC06 claims overstate coverage. Regressions that overwrite unsafe paths, select the
wrong account, validate the wrong candidate, or lose metadata can pass the required test command.


#### Fix

Add temporary-tree tests for every required safety and identity branch. Make the runner argument-aware in assertions,
inspect candidate bytes and paths, inject filesystem and command failures, and assert content, inode, mtime, mode, and
ownership before and after rollback. Keep all subprocess calls mocked.


#### Outcome

Pending principal resolution.


#### C06: Filesystem and command failures can escape with temporary files left


#### Where

`tools/configure-sudoers.py:40-47,128-154,221-237`


#### Evidence

`run_command` and the sudo re-execution branch catch only `FileNotFoundError` and `TimeoutExpired`; other `OSError`
failures such as `PermissionError` escape as tracebacks. In `install`, creation of `main_candidate` occurs before the
`try` block and creation of `managed_candidate` is the next statement. If the second creation fails, the first temporary
file is not cleaned up. Directory creation and metadata operations in `ensure_include_dir` are also outside a
`ConfigurationError` boundary.


#### Issue

The privileged path does not give all external failures a clear controlled error, and candidate setup is not covered by
the transaction cleanup path.


#### Impact

A failed write can leave hidden candidate files in `/etc` or `/etc/sudoers.d` and terminate with a Python traceback
instead of a bounded configuration failure. This violates the required failed-write handling and weakens the safety
guarantee around sudoers changes.


#### Fix

Put all candidate creation and cleanup under one guarded transaction, remove every temporary file in a `finally` path,
and convert expected filesystem and process `OSError` failures into `ConfigurationError` with context. Add injected
write, metadata, and command-error tests that assert no candidate remains and no managed content changes.


#### Outcome

Pending principal resolution.


----

### Significant

#### S01: `--check` rejects valid active include forms


#### Where

`tools/configure-sudoers.py:109-125,207-211`


#### Evidence

`--check` defines `active` as `rewrite_includes(original_main) == original_main`. Rewriting always canonicalizes an
existing `@includedir`, a valid include with a trailing comment, or the accepted `/private/etc` spelling to a new
`#includedir /etc/sudoers.d` line. Each of those configurations is active, but the byte comparison returns false.


#### Issue

The semantic active-include check is coupled to the normalizer's canonical bytes instead of counting valid active target
directives.


#### Impact

The manifest check command reports a correct configuration as missing and invokes the privileged normal path on every
configure run. It also fails the required recognition behavior for accepted active forms and weakens idempotent use of
`--check`.


#### Fix

Separate parsing from normalization. For check mode, accept exactly one active target include in any required spelling
and preserve the existing managed rule and metadata checks. Add check-mode tests for `@includedir`, trailing comments,
and the valid Darwin alias.


#### Outcome

Pending principal resolution.


#### S02: Rollback rewrites unchanged files and loses managed metadata


#### Where

`tools/configure-sudoers.py:167-183`


#### Evidence

The exception path always writes and replaces the main sudoers file, even when candidate validation failed before the
main replacement or when the main content was unchanged. It snapshots only `old_managed` bytes, then restores an old
managed file with mode `0440` instead of its prior mode and group metadata.


#### Issue

Rollback restores content but not the exact prior filesystem state, and it performs an unnecessary replacement for paths
that the transaction never changed.


#### Impact

Candidate or final validation failure can change the main file's inode and mtime and can change a previously safe
managed file's permissions or group. That violates the metadata and idempotence expectations around failure recovery and
can trigger unnecessary consumers of `/etc/sudoers`.


#### Fix

Track which replacements completed, restore only those paths, and snapshot and restore the managed file's mode, owner,
and group. Add failure tests that assert bytes, inode, mtime, mode, and ownership for both changed and unchanged paths.


#### Outcome

Pending principal resolution.


#### S03: Unsupported-platform validation happens after sudo re-execution


#### Where

`tools/configure-sudoers.py:191-235`; `tests/test_install.py:236-240`


#### Evidence

The platform check is inside `configure`, but `main` escalates first whenever the effective UID is non-root. The only
unsupported-platform test patches the fixture's `ROOT_UID` to the current user UID, so it exercises the post-escalation
branch without testing a normal non-root invocation.


#### Issue

An unsupported non-root host attempts noninteractive sudo before reporting that the operating system is unsupported. If
sudo is unavailable, the user receives an authentication/tool error rather than the platform error required by AC03.


#### Impact

The command can prompt or fail for an unrelated privilege reason on an unsupported platform, obscuring the real cause
and
making the platform contract dependent on sudo availability.


#### Fix

Reject unsupported platforms before escalation, or explicitly test and preserve the platform error through the
escalation
path. Add a non-root unsupported-platform test with exact command assertions.


#### Outcome

Pending principal resolution.


## Skills Applied

- `review-implementation-execution`: project-local
- `review-code`: global fallback
- `write-docs`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

C01, C02, C03, C04, C05, and C06 must be resolved before approval. S01, S02, and S03 should be addressed in the same
pass or recorded as explicit follow-up work by the principal.


## Re-review 02

This independent re-review uses Iteration 01's C01-C06 and S01-S03 findings as its sole checklist. Reviewer variant:
`--personal-luna` (`opencode/gpt-5.6-luna`).


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 32 passed.
- `bash -n install.sh`: exit 0.
- `uv run ruff check src tests`: `All checks passed!`.
- `git diff --check`: exit 0.
- No live sudoers configuration was run.


### Checklist outcomes

| Finding | Outcome            | Evidence                                                                                                                                                                                                                                                                                                                |
| ------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01     | Resolved           | The script is mode `0755`; the direct `--help` test asserts executability (`tests/test_install.py:69-73`).                                                                                                                                                                                                              |
| C02     | Resolved           | The staged rule is placed in a temporary includedir before complete-candidate validation (`tools/configure-sudoers.py:188-231`).                                                                                                                                                                                        |
| C03     | Resolved           | The `/private/etc` alias is Darwin-only and requires matching resolved directories (`tools/configure-sudoers.py:134-147`).                                                                                                                                                                                              |
| C04     | Resolved           | Fixture setup patches every configurator subprocess runner (`tests/test_install.py:25-43`); the suite passes without live `visudo`.                                                                                                                                                                                     |
| C05     | Partially resolved | Required branches remain untested, including Darwin `@includedir` creation, duplicate active targets, `SUDO_USER`/UID fallback, missing `sudo`, real unsafe ownership/mode cases, and non-root unsupported-platform execution (`tests/test_install.py:115-140,214-265,286-294,351-372`).                                |
| C06     | Partially resolved | Several filesystem failures remain outside a controlled boundary: fixture reads in `configure` (`tools/configure-sudoers.py:291-299`) and candidate cleanup (`tools/configure-sudoers.py:244-275`) can escape or mask restoration; `write_temp` also performs unguarded cleanup (`tools/configure-sudoers.py:157-165`). |
| S01     | Resolved           | Check mode counts exactly one active include and accepts the required forms/comments (`tools/configure-sudoers.py:291-299, tests/test_install.py:275-283`).                                                                                                                                                             |
| S02     | Resolved           | Rollback tracks completed replacements and restores managed mode, owner, and group (`tools/configure-sudoers.py:227-269`).                                                                                                                                                                                              |
| S03     | Resolved           | Unsupported platforms are rejected before sudo re-execution (`tools/configure-sudoers.py:303-310`).                                                                                                                                                                                                                     |


## Re-review decision

**NOT APPROVED — CHANGES REQUIRED.** C05 still leaves AC07 coverage unproven, and C06 still permits uncontrolled
filesystem failures during the privileged transaction. The implementation is not approved for the human code-review
gate.


## Final compact re-review

This final independent re-review uses the prior C01-C06 and S01-S03 findings as its sole checklist. Reviewer variant:
`--personal-luna` (`opencode/gpt-5.6-luna`).


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 45 passed.
- `uv run pytest tests/test_install.py --no-cov -k sudo`: 44 passed, 1 deselected.
- `bash -n install.sh`: exit 0.
- `uv run ruff check src tests`: `All checks passed!`.
- `git diff --check`: exit 0.
- `tools/configure-sudoers.py`: mode `0755`.

All configurator fixture tests patch the module subprocess runner, and the only direct script invocation uses `--help`.
No host `sudo` or `visudo` was invoked and no live sudoers configuration was run.


### Checklist outcomes

| Finding | Outcome            | Evidence                                                                                                                                                                                                                                                                                                                                                |
| ------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01     | Resolved           | The script is mode `0755`; the direct executable test asserts the mode and successful `--help` execution (`tests/test_install.py:75-79`).                                                                                                                                                                                                               |
| C02     | Resolved           | Setup stages the managed rule in a temporary includedir and validates the complete candidate before replacement (`tools/configure-sudoers.py:224-256,274-276`; `tests/test_install.py:365-380`).                                                                                                                                                        |
| C03     | Resolved           | The `/private/etc` spelling is accepted only on Darwin and only when resolved paths match (`tools/configure-sudoers.py:134-147`; `tests/test_install.py:145-156`).                                                                                                                                                                                      |
| C04     | Resolved           | The fixture patches every configurator subprocess call with an argument-checking runner (`tests/test_install.py:25-43,46-65`).                                                                                                                                                                                                                          |
| C05     | Partially resolved | Identity, platform, safety, candidate, cleanup, and command-failure cases were added, but replacement atomicity, wrong-type branches, successful main-file metadata/ownership, and replacement/restoration failures still lack meaningful tests (`tests/test_install.py:365-417,449-513`; `tests/test_install.py:506-512` only checks an inode change). |
| C06     | Partially resolved | Candidate setup is guarded, but failures after a newly created include directory are outside the cleanup scope (`tools/configure-sudoers.py:350-384`), best-effort cleanup can leave candidates (`tools/configure-sudoers.py:180-193,334-339`), and restoration-error reporting omits the original failure (`tools/configure-sudoers.py:287-333`).      |
| S01     | Resolved           | Check mode counts active directives semantically and accepts the required forms/comments (`tools/configure-sudoers.py:364-373`; `tests/test_install.py:326-334`).                                                                                                                                                                                       |
| S02     | Resolved           | Restoration tracks completed replacements and restores managed content and metadata (`tools/configure-sudoers.py:271-339`; `tests/test_install.py:383-399`).                                                                                                                                                                                            |
| S03     | Resolved           | Unsupported platforms fail before privilege escalation (`tools/configure-sudoers.py:342-345,387-394`; `tests/test_install.py:292-300`).                                                                                                                                                                                                                 |


### Findings

#### C05: Required security and transaction coverage remains incomplete

**Severity**: Critical

The added tests cover the previously missing identity, platform, mode, candidate-content, and command-isolation cases.
They do not prove the required atomic transaction behavior: the atomicity test only observes a changed inode, and no
test
exercises `os.replace` failure or restoration failure. The safe-path type branches and successful main-file metadata and
ownership behavior are also untested; the fixture patches `os.chown` globally (`tests/test_install.py:37-40`).

**Recommendation**: Add isolated behavior tests for each remaining type and replacement-failure branch, assert the main
file's preserved metadata, and verify candidate cleanup and restoration state after each injected failure.


#### C06: Pre-transaction cleanup and primary-error preservation remain unsafe

**Severity**: Critical

`ensure_include_dir()` can create the directory and then fail during `chown` or `chmod` without removing it
(`tools/configure-sudoers.py:81-93`). After creation, `desired_rule()`, include parsing, or file reads can fail before
the
`try` that removes a newly created directory (`tools/configure-sudoers.py:350-384`). The cleanup helpers suppress unlink
and
tree-removal errors, so a cleanup failure can leave a candidate behind (`tools/configure-sudoers.py:180-193,334-339`).
If
restoration fails, the raised message reports only restoration errors, while `main()` prints that message and hides the
primary validation or replacement failure (`tools/configure-sudoers.py:287-333,409-413`).

**Recommendation**: Put all post-creation work under one cleanup-scoped transaction, report failed cleanup paths, and
include
the original failure alongside restoration failures in the user-visible error.


### Re-review decision

**NOT APPROVED — CHANGES REQUIRED.** C05 and C06 remain only partially resolved. The implementation is not approved for
the
human code-review gate. No separate regression outside these checklist findings was identified.


## Final compact independent re-review

This final `--personal-luna` re-review independently checked the approved plan, journal, current implementation, tests,
and prior C05/C06 remediation against all C01-C06 and S01-S03 findings.


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 57 passed.
- `uv run pytest tests/test_install.py --no-cov -k sudo`: 56 passed, 1 deselected.
- `bash -n install.sh`: exit 0.
- `uv run ruff check src tests`: `All checks passed!`.
- `git diff --check`: exit 0.
- `tools/configure-sudoers.py`: mode `0755`.

All configurator subprocess calls are mocked by the fixture runner; the only direct subprocess call is the standalone
`--help` contract test. No live `sudo` or `visudo` command was invoked, and no live sudoers configuration was run.


### Checklist outcomes

| Finding | Outcome  | Evidence                                                                                                                                                                                                   |
| ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01     | Resolved | Executable mode and direct `--help` coverage at `tests/test_install.py:84-88`.                                                                                                                             |
| C02     | Resolved | Staged include-tree and complete-candidate validation at `tools/configure-sudoers.py:252-284`; tested at `tests/test_install.py:374-389`.                                                                  |
| C03     | Resolved | Darwin-only resolved-path alias handling at `tools/configure-sudoers.py:140-153`; Linux distinction tested at `tests/test_install.py:162-166`.                                                             |
| C04     | Resolved | Argument-aware fixture runner and fixture patching at `tests/test_install.py:25-74`; only direct call is `--help`.                                                                                         |
| C05     | Resolved | Non-regular paths, replacement failures, restoration, exact metadata, and candidate state are covered at `tests/test_install.py:537-688`.                                                                  |
| C06     | Resolved | Creation, transaction, cleanup, failure reporting, and primary-error preservation are guarded at `tools/configure-sudoers.py:81-99,204-368,396-418` and tested at `tests/test_install.py:430-447,657-688`. |
| S01     | Resolved | Semantic active-include counting accepts required forms and comments at `tools/configure-sudoers.py:376-392`; tested at `tests/test_install.py:335-343`.                                                   |
| S02     | Resolved | Replacement tracking restores only changed paths and prior managed metadata at `tools/configure-sudoers.py:296-364`; tested at `tests/test_install.py:392-407,577-628`.                                    |
| S03     | Resolved | Unsupported platforms fail before privilege escalation at `tools/configure-sudoers.py:421-442`; tested at `tests/test_install.py:301-309`.                                                                 |


### Remaining findings

None.


### Final decision

**APPROVED.** C01-C06 and S01-S03 are resolved, all required checks pass, and the implementation is approved for the
human code-review gate.


## Revision re-review

This compact independent `--personal-luna` re-review covers only the requested py-buzz revision against the prior
approved review.


### Findings

None. The inline PEP 723 block declares `py-buzz>=8.0` (`tools/configure-sudoers.py:1-5`), `ConfigurationError`
derives from `buzz.Buzz` (`tools/configure-sudoers.py:20,31`), and `require_safe_path()` routes its safety assertions
through `ConfigurationError.check_expressions()` (`tools/configure-sudoers.py:62-80`). The existing sudoers fixture
module passes unchanged behavior coverage: `uv run pytest tests/test_install.py --no-cov` reports 58 passed. The script
remains under `tools/`, is absent from `bin/`, retains executable mode `0755`, and direct `--help` execution succeeds.

The supplemental full-suite run reported one unrelated existing failure in
`tests/test_configure.py:651`: the committed `.config/opencode/package.json` contains
`{"dependencies": {"@opencode-ai/plugin": "1.18.14"}}`, while that test expects `{}`. No sudoers test or requested
revision check failed.


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 58 passed.
- `uv run ruff check src tests`: passed.
- `bash -n install.sh`: passed.
- `./tools/configure-sudoers.py --help`: exit 0.
- Contract assertions for metadata, inheritance, `check_expressions()`, location, and mode: passed.
- No live sudoers configuration, `sudo`, or `visudo` invocation was run.


### Final decision

**APPROVED.** This revision is approved for the human code-review gate. The unrelated full-suite baseline failure is not
attributable to this revision.


## Rich revision re-review

This compact independent `--personal-luna` re-review covers only the Rich error-output revision against the original
request and prior approved review.


### Findings

None. The inline PEP 723 metadata declares `py-buzz>=8.0` and `rich>=14.0` (`tools/configure-sudoers.py:1-5`).
`fail()` uses Rich `Console` and `Text`, emits a red `Error` renderable to stderr, and preserves the
`: configure-sudoers: ...` message (`tools/configure-sudoers.py:20-41`; `tests/test_install.py:84-94`). The script
remains
under `tools/`, is absent from `bin/`, retains executable mode `0755`, and direct `--help` execution succeeds.


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 59 passed.
- `uv run ruff check src tests`: passed.
- `bash -n install.sh`: passed.
- `./tools/configure-sudoers.py --help`: exit 0.
- `git diff --check`: passed.
- Full suite: 372 passed, 1 pre-existing failure in `tests/test_configure.py:651` because the committed
  `.config/opencode/package.json` contains the `@opencode-ai/plugin` dependency while the test expects `{}`.
- No live sudoers configuration, `sudo`, or `visudo` invocation was run.


### Final decision

**APPROVED.** This Rich revision is approved for the human code-review gate. The focused behavior and direct execution
checks pass; the unrelated full-suite baseline failure is not attributable to this revision.


## Missing-path revision re-review

This compact independent `--personal-luna` re-review covers only the missing-path revision against the original request
and the prior approved review.


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 59 passed.
- `uv run pytest tests/test_install.py --no-cov -k sudo`: 58 passed, 1 deselected.
- `uv run ruff check src tests`: passed.
- `bash -n install.sh`: passed.
- `./tools/configure-sudoers.py --help`: exit 0.
- `uv run ty check tools/configure-sudoers.py`: passed.
- `git diff --check`: passed; the script remains mode `0755` under `tools/`.

No live sudoers configuration, `sudo`, or `visudo` invocation was run.


### Findings

#### C01: Optional return is hidden from the type contract


#### Where

`tools/configure-sudoers.py:65-74`


#### Issue

`require_safe_path()` is annotated as returning `os.stat_result`, but returns `None` for the new
`allow_missing=True` path and suppresses the mismatch with `# type: ignore[return-value]`. The current optional callers
check for `None`, but the public function contract now permits a value that static checking cannot expose to future
callers.


#### Impact

Future optional callers can dereference `None` without a type-checking diagnostic. The new opt-in contract is therefore
not type-safe even though the current callers narrow the result correctly.


#### Fix

Change the return annotation to `os.stat_result | None` (or provide overloads for the default and opt-in forms), remove
the suppression, and explicitly narrow required callers.


#### Outcome

Pending principal resolution.


### Final decision

**NOT APPROVED — CHANGES REQUIRED.** C01 must be resolved before this revision is approved for the human code-review
gate. The runtime missing-path behavior, optional caller opt-in, required sudoers path, creation paths, Buzz/Rich
behavior, tests, and direct execution otherwise remain correct.


## Typed-contract revision re-review

This compact independent `--personal-luna` re-review checks the typed missing-path fix against C01 and the prior
missing-path revision review.


### Findings

None. C01 is fully resolved. `require_safe_path()` overloads return `os.stat_result` for default and explicit
`allow_missing=False` calls, and `os.stat_result | None` for explicit `allow_missing=True` calls
(`tools/configure-sudoers.py:66-78`). No `# type: ignore` remains. Required callers use the non-optional overload;
optional include-directory and managed-drop-in callers use the explicit opt-in and retain their `None` handling
(`tools/configure-sudoers.py:101-119,391-413`). Buzz exception behavior, Rich error output, and sudoers behavior remain
covered by the passing test module.


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 59 passed.
- Focused Buzz/Rich and sudoers tests: 58 passed, 1 deselected.
- `uv run ruff check src tests`: passed.
- `uv run ty check tools/configure-sudoers.py`: passed.
- `bash -n install.sh`: passed.
- `./tools/configure-sudoers.py --help`: exit 0.
- `git diff --check`: passed.

No live sudoers configuration, `sudo`, or `visudo` invocation was run.


### Final decision

**APPROVED.** The typed contract is sound, required and optional callers behave correctly, and no Buzz, Rich, or
sudoers-test regression was found. This revision is approved for the human code-review gate.


## Path-based metadata refactor re-review

This compact independent `--personal-luna` re-review checks only the path-based metadata refactor against the user
request and the prior approved review.


### Verification

- `uv run pytest tests/test_install.py --no-cov`: 59 passed.
- `uv run pytest tests/test_install.py --no-cov -k sudo`: 58 passed, 1 deselected.
- `uv run ruff check src tests`: passed.
- `uv run ty check tools/configure-sudoers.py`: passed.
- `bash -n install.sh`: passed.
- `./tools/configure-sudoers.py --help`: exit 0.
- `git diff --check`: passed.

No live sudoers configuration, `sudo`, or `visudo` invocation was run.


### Findings

None. `install()` and `configure_existing_paths()` accept paths and retrieve metadata at the point of use
(`tools/configure-sudoers.py:232-251,381-403`). Root metadata still supplies candidate and rollback mode, owner, and
group
values (`tools/configure-sudoers.py:280-293,326-331`); managed metadata still controls replacement decisions and
restores
the prior mode, owner, and group (`tools/configure-sudoers.py:240-256,347-353`). `ensure_include_dir()` no longer
threads an include-directory stat result (`tools/configure-sudoers.py:90-108`), and optional missing-path handling
remains
explicit through `allow_missing=True` while required callers retain the default
(`tools/configure-sudoers.py:65-87,387-417`).
The fixture patches all configurator subprocesses and the focused suite passes without host commands
(`tests/test_install.py:25-74`).


### Final decision

**APPROVED.** The path-based API, metadata preservation and restoration, optional-path contract, and test isolation
remain
correct. This revision is approved for the human code-review gate.
