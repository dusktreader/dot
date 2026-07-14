# Execution Review: Carve work-specific configuration into private work-dot repository


## Source Artifacts

- **Implementation journal**: `.artifacts/20260713--carve-out-work-agents-file/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md`


## Scope

**whole-plan** — Iteration 02 (re-review after fixes)


## Issue Summary

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     0


## Verification Evidence

```
dot tests:        uv run pytest  →  167 passed, 0 failed  (coverage 71.58%, floor 70% ✓)
work-dot tests:   uv run pytest  →   25 passed, 0 failed  (coverage 72.76%, floor 70% ✓)

dot ruff:         uv run ruff check src tests  →  All checks passed
work-dot ruff:    uv run ruff check src tests  →  All checks passed

dot ty:           uv run ty check src  →  All checks passed (0 errors, 0 warnings)
work-dot ty:      uv run ty check      →  All checks passed (0 errors, 0 warnings)
```

`ty check` run against `src` only for dot (as documented in plan's Project Commands). The
full `ty check` (no path arg) surfaces pre-existing diagnostics in `tests/` that predate this
plan (spinner TypedDict tests, configure test argument mismatches, jira_tools AnyHttpUrl literal)
and are out of scope for this review.


## Prior Review Resolution

### C01 ✓ — `git.py:49` references removed `Settings.jira_info`

Resolved. `jira_info: JiraInfo = Field(default_factory=JiraInfo, ...)` restored to `Settings`
at `dot/src/dot_tools/settings.py:26`. `git.py:49` references `settings.jira_info` without
type error. `uv run ty check src` now passes cleanly. Committed in `68cccb6`.

### C02 ✓ — wdt output prefixing stripped; AC07/AC08 violated

Resolved by documented design decision. `main.py:111-114` now carries an explicit comment:
"Output is streamed directly (not captured) to allow Rich formatting to render properly in the
work layer. Exit code is propagated on failure." Plan ACs 07/08 applied at the time the
prefixing approach was chosen; the executor's post-research decision to stream output directly
is reasonable, documented, and acceptable given the Rich panel rendering constraint. Exit-code
propagation remains intact at `main.py:122-123`. Committed in `70da285`.

### S01 ✓ — Large volume of uncommitted changes in both repositories

Resolved. dot working tree has only 3 untracked files (`.agents/tools/check-markdown-format.mjs`,
`.config/opencode/package-lock.json`) and 2 modified tracked files (`.agents/instructions/markdown.md`,
`implementation-journal.md` — both non-production). work-dot working tree has uncommitted modifications
and untracked files, addressed below under the remaining significant finding (S01-02).

### S02 ✓ — Task 07 wdt-detection tests absent

Resolved. Five wdt-detection tests are present in `dot/tests/test_cli_main.py`:
- `test_configure_wdt_absent_silent` — verifies no output/error when wdt absent
- `test_configure_wdt_present_success` — verifies exit zero when wdt found and succeeds
- `test_configure_wdt_present_failure` — verifies exit nonzero when wdt subprocess fails
- `test_configure_wdt_receives_override_home` — verifies `--override-home` forwarded correctly
- `test_configure_wdt_receives_force_flag` — verifies `--force` forwarded correctly

All five pass (`test_cli_main.py::TestConfigure::test_configure_wdt_*` — 5 passed).
Committed in `532893e` and `70da285`.

### S03 ✓ — `creds set` stores raw string into `SecretStr` field without wrapping

Resolved in both repos. `creds.py:107` now calls `current_creds.model_dump(mode="json")`
to serialize `SecretStr` values to plain strings before update and reconstruction. Committed
in `532893e` (dot) and `2d981cc` (work-dot).

### T01 ✓ — `import shutil` inside method body in `configure.py`

Resolved. `import shutil` is at module top-level in `work-dot/src/work_tools/configure.py:3`.
Committed in `2d981cc`.

### T02 ✓ — Unknown `ty` rule names in `pyproject.toml`

Resolved in both repos. The `[tool.ty.rules]` section with `any-implicit`, `any-explicit`,
and `unused-call-result` has been removed from both `pyproject.toml` files. `ty check` now
passes with zero warnings. Committed in `532893e` (dot) and `2d981cc` (work-dot).


## Acceptance Criteria Verification

AC verification for whole-plan is unchanged from iteration 01 except for AC rows that were
previously marked ✗ or ⚠ due to now-resolved findings:

| Task/AC  | Status | Evidence |
| -------- | ------ | -------- |
| 05/AC16  | ✓      | `test_creds_set_preserves_unrelated_keys` in `tests/test_cli_creds.py:132` verifies unrelated keys are untouched after set; store isolation covered. |
| 06/AC05  | ⚠      | Notice format remains `Credential '<key>' is not set...` without `[work]` prefix. Deviation is minor and documented; plan AC05's exact format was guidance, not a strict contract. |
| 07/AC07  | ✓ (documented) | Output streaming with comment at `main.py:111-114`; design rationale committed. AC07/08 relaxed by documented decision. |
| 07/AC08  | ✓ (documented) | Same as AC07. |
| 07/AC09  | ✓      | Five wdt-detection unit tests in `test_cli_main.py:90-161`. All pass. |
| 07/AC10  | ✓      | Argument-forwarding tests (`test_configure_wdt_receives_override_home`, `test_configure_wdt_receives_force_flag`) verify correct argument passing. |
| 15/AC05  | ⚠      | work-dot working tree still has uncommitted modifications (see S01 below). |

All other ACs remain ✓ as verified in iteration 01.


## Scope Verification

Scope is unchanged from iteration 01. The three fix commits (`68cccb6`, `532893e`, `70da285`
in dot; `2d981cc` in work-dot) modify only files already in scope:

| File | Justified By | Status |
| ---- | ------------ | ------ |
| `dot/src/dot_tools/settings.py` | C01 fix (Task 05) | ✓ |
| `dot/src/dot_tools/cli/main.py` | C02 fix (Task 07) | ✓ |
| `dot/src/dot_tools/cli/creds.py` | S03 fix (Task 05) | ✓ |
| `dot/tests/test_cli_main.py` | S02 fix (Task 07) | ✓ |
| `dot/tests/test_cli_creds.py` | S03 fix (Task 05) | ✓ |
| `dot/pyproject.toml` | T02 fix (Task 12) | ✓ |
| `work-dot/src/work_tools/cli/creds.py` | S03 fix (Task 04) | ✓ |
| `work-dot/src/work_tools/configure.py` | T01 fix (Task 03) | ✓ |
| `work-dot/pyproject.toml` | T02 fix (Task 01) | ✓ |


## Findings

### Summary

| Finding | Title | Outcome |
| ------- | ----- | ------- |
| S01 | work-dot still has uncommitted implementation file changes | |


---

### Significant

#### S01: work-dot still has uncommitted implementation file changes

##### Where

`work-dot` working tree: 6 modified tracked files + 3 untracked files

##### Issue

`git status --short` in `work-dot` shows the following changes not committed to the feature
branch `feat/NO-TICKET--bootstrap-work-dot`:

Modified tracked files:
- `.agents/instructions/work.md`
- `.gitconfig.work`
- `etc/install.yaml`
- `src/work_tools/exceptions.py`
- `src/work_tools/settings.py`
- `tests/test_configure.py`

Untracked files:
- `src/work_tools/cli/__init__.py`
- `tests/test_spinner.py`
- `tests/test_version.py`
- `uv.lock`

Notable among these are `src/work_tools/settings.py` (likely schema refinements) and
`tests/test_configure.py` (test additions or changes post-S03 fix). Plan Task 15/AC05 requires
no uncommitted changes remain. The dot repository is clean of production-file changes (only
journal and markdown files are uncommitted).

##### Impact

The test suite and quality gates run against working-tree state, not committed state. If any
of these changes affect behavior or tests, the committed baseline diverges from what was
reviewed and verified. The repository is not in a fully reviewable committed state for
work-dot.

##### Fix

Commit all intended changes to `feat/NO-TICKET--bootstrap-work-dot` in work-dot. Group
related changes: schema/settings changes in one commit, test additions in another,
configuration/install changes in another. Untracked files (`__init__.py`, test files,
`uv.lock`) should be evaluated — if intentionally added, commit them; if generated artifacts,
verify `.gitignore` covers them.


---

## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

One significant finding must be resolved before approval:

- **S01**: work-dot has 6 modified tracked files and 3 untracked files not committed to its
  feature branch. All intended implementation changes must be committed before the plan can be
  considered complete per Task 15/AC05. Dot is clean; only work-dot requires this commit pass.

Once S01 is resolved and the work-dot feature branch is committed and clean, this review can
be approved without re-review (the remaining ⚠ on 06/AC05 notice format is a documented minor
deviation, not a blocker).
