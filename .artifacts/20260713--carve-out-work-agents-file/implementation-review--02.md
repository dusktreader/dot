# Implementation Plan Review: Carve work-specific configuration into private work-dot repository

**Iteration 02**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md


## Overview

The revision resolved six of nine prior findings. Two significant findings were only partially
addressed; one new significant finding and two new trivial findings surfaced in this pass.

- **Critical**:    0
- **Significant**: 3
- **Trivial**:     2


## Prior review resolution

- **C01** ✓: Task 13 no longer contains a static incorrect sample command; it explicitly defers
  the bind syntax to Task 04 research and uses only verified syntax.
- **S01** ✓: All references to `wdt settings set` replaced with `wdt settings bind` or
  `wdt settings update`; AC08 of Task 04 explicitly forbids assuming `set` exists.
- **S02** ⚠: Acknowledged and deferred to Task 04 research, but no concrete AC was added to
  Task 05 confirming seeding works when invoked from the live `wdt configure` command. The
  resolution path is described in Technical Notes but remains unverified by any AC.
- **S03** ⚠: Task 04 now requires schema justification (AC02) and step 6 adds explicit schema
  design guidance. However, the absence of a `dt secrets fetch` command — required by design
  plan AC17 — is still unaddressed. No task implements or tests `dt secrets fetch` in `dot`.
- **S04** ✓: Task 04 AC11 now contains the required risk disclosure language verbatim.
- **S05** ✓: Duplicate `pyproject.toml` step in Task 01 collapsed; duplicate `main.py` step in
  Task 02 removed and replaced with `uv sync` verification step.
- **T01** ✓: `## Unknowns` section now lists the Typerdrive API questions and marks them as
  resolved in-task during Task 04 step 5.
- **T02** ✓: `## Technical Notes` is now richly populated with repo structure, migration
  sequence, shell sourcing order, Git config layering, testing strategy, and Typerdrive details.
- **T03** ✓: Shell rc code fence in Task 09 uses `shell` language hint.


## Findings

### Summary

| Finding | Title                                                            | Outcome |
| ------- | ---------------------------------------------------------------- | ------- |
| S01     | `dt secrets fetch` is unimplemented — design plan AC17 uncovered |         |
| S02     | Task 05 has no AC confirming context-initialized seeding         |         |
| S03     | Task 06 and Task 11 overlap heavily without differentiation      |         |
| T01     | Task 12 AC01 specifies 80% coverage; pyproject.toml floor is 70% |         |
| T02     | GitHub org name in Task 01 contains an invalid underscore        |         |


### Significant

#### S01: `dt secrets fetch` is unimplemented — design plan AC17 uncovered


#### Where

Design plan — AC17; Implementation plan — Execution section (all tasks)


#### Issue

Design plan AC17 requires: "`dt` exposes a `secrets fetch <key>` command that prints the named
secret value to stdout with no surrounding formatting, exiting non-zero if the key is absent or
empty." No implementation task in the plan adds a `secrets fetch` sub-command or `secrets` CLI
group to `dot`. Tasks 04–05 implement `wdt secrets fetch` in `work-dot`; neither task nor any
other extends the same interface to `dt`.

The design plan treats both CLIs symmetrically for secrets access. AC17 is a first-class
acceptance criterion of the approved design, not an optional stretch goal.


#### Impact

Design plan AC17 is undelivered. Any agent or script that uses `dt secrets fetch` — as directed
by the updated agent instructions in Task 14 — will receive a "no such command" error. Task 14
AC02 explicitly states that `dot` agent instructions should document `dt secrets fetch <key>`,
which will be incorrect if the command does not exist.


#### Suggestion

Add a new task (or extend Task 04) to implement a `secrets fetch` sub-command in `dot`. The task
should mirror `work-dot`'s Task 04 implementation: create `dot/src/dot_tools/cli/secrets.py`,
register it in `cli/main.py`, implement `fetch(key: str)`, and add unit tests. The risk
disclosure AC (equivalent to Task 04 AC11) must also be included for `dt secrets fetch`.


#### Outcome


----

#### S02: Task 05 has no AC confirming context-initialized seeding


#### Where

Execution — Task 05 — Acceptance Criteria — lines 452–468


#### Issue

The prior review (S02) requested an AC confirming that `_seed_secrets()` works when invoked
from the live `wdt configure` command. The revision acknowledges the context-initialization
problem in Task 04 and Task 05 Technical Notes, but no AC was added to verify the fix. All
existing Task 05 ACs are unit-test level (AC08: "Unit tests verify seeding..."). None require
running `wdt configure` end-to-end to confirm that seeding completes without a
`SettingsInitError`.

Without a verifiable AC, an executor may pass all unit tests while the actual configure command
fails silently on the context requirement, leaving the issue undetected until manual testing.


#### Impact

If the context initialization pattern is incorrect, `wdt configure` will fail at the seeding
step (AC01–AC03 describe the desired behavior but none require end-to-end exercise). The bug
could persist through all unit tests and surface only during Task 06 integration work or manual
acceptance.


#### Suggestion

Add to Task 05 Acceptance Criteria:

> AC09: Running `uv run wdt configure --override-home /tmp/test-wdt-seed-live` completes without
> error, and a subsequent `uv run wdt secrets fetch <any-seeded-key>` exits non-zero (placeholder
> present), confirming seeding ran from within the live CLI context.


#### Outcome


----

#### S03: Task 06 and Task 11 overlap heavily without differentiation


#### Where

Execution — Task 06 — Steps — lines 536–565; Task 11 — Steps — lines 845–858


#### Issue

Task 06 already instructs the implementor to build the subprocess invocation with correct
argument passing (step 2, lines 537–546), including constructing the `wdt configure` command
with `--override-home` and `--force`. Task 11 then covers "Ensure `dt configure` passes the
correct `--root` and `--override-home` arguments to `wdt configure`" and provides an identical
code snippet (lines 848–853) for the same `wdt_cmd` construction.

Task 11 adds no new behavior — it re-describes what Task 06 already builds, with the only
difference being `--root` (which Task 06 also implicitly covers via the `--force` and
`--override-home` pattern). An implementor will reach Task 11 having already implemented
everything it describes, with no clear incremental action.


#### Impact

The implementor either skips Task 11 as already-done (leaving its ACs unverified) or
re-implements the same logic a second time (risking divergence). Both outcomes reduce
confidence in the task structure.


#### Suggestion

Merge Task 11 into Task 06: add its ACs (AC01–AC05) directly to Task 06, and add `--root`
argument handling and the corresponding tests to Task 06's Steps. Remove Task 11 as a
standalone task and renumber subsequent tasks accordingly.


#### Outcome


----

### Trivial

#### T01: Task 12 AC01 specifies 80% coverage; configured floor is 70%


#### Where

Execution — Task 12 — Acceptance Criteria — line 879


#### Issue

Task 12 AC01 reads: "Test coverage for `dot` includes at least 80% of code touched in this
implementation." Task 12 AC02 sets the same 80% bar for `work-dot`. The `pyproject.toml` for
`dot` configures a 70% coverage floor (`fail_under = 70`). The implementation plan description
says coverage must "meet or exceed the configured floor," yet Task 12 raises the bar to 80%
without noting that this exceeds the project setting.


#### Suggestion

Either lower the Task 12 ACs to 70% to match the configured floor, or explicitly note that the
80% figure applies only to the files touched in this implementation (using `--cov-fail-under 80`
for a scoped run), and document the exact `pytest` invocation that enforces it.


#### Outcome


----

#### T02: GitHub org name in Task 01 contains an invalid underscore


#### Where

Execution — Task 01 — Acceptance Criteria — AC04; Technical Notes — line 208; Goal — line 15


#### Issue

The plan references `https://github.com/Tucker-Beck_mcgraw/work-dot` in several places. GitHub
organization and user names may contain hyphens but not underscores. The org name
`Tucker-Beck_mcgraw` is invalid; GitHub will reject it at creation time. The actual org or user
account name under which `work-dot` will be hosted is unclear.


#### Suggestion

Confirm the correct GitHub Cloud account name for the McGraw Hill work account and replace all
occurrences of `Tucker-Beck_mcgraw` with the verified name. If the account does not yet exist,
note this as a prerequisite in Task 01 and add an AC for account creation before the remote
is configured.


#### Outcome


----

## Notes

S01 is the highest-priority remaining finding. Design plan AC17 is a first-class deliverable,
not a nice-to-have. The fix is straightforward and does not require human input — it mirrors the
`wdt secrets fetch` work already planned in Task 04.

S02 and S03 can be resolved without discussion: S02 requires adding one AC to Task 05; S03
requires merging Task 11 into Task 06.

T02 (invalid org name) may require a brief human confirmation of the correct GitHub account
name before Task 01 can be executed.
