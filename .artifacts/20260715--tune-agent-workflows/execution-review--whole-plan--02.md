# Execution Review: Tune agent workflows and report OpenCode costs


## Source Artifacts

- **Implementation journal**: `.artifacts/20260715--tune-agent-workflows/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260715--tune-agent-workflows/implementation-plan.md`


## Scope

**whole-plan** — Iteration 02 (re-review)


## Issue Summary

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     1


## Verification Evidence

```
Linter:   uv run ruff check src tests tools       → All checks passed
Tests:    uv run pytest                            → 190 passed, 2 warnings (was 182 before changes)
Coverage: uv run pytest                            → 77.69% (threshold 70% met)
Focused:  uv run pytest tests/test_cli_opencode_costs.py
          tests/test_validate_staged_agent_policies.py
          tests/test_opencode_costs.py --no-cov -q → 20 passed
Staged:   uv run python tools/validate_staged_agent_policies.py
          --staging-root .../agent-workflow-tuning
          --manifest .../agent-workflow-tuning/manifest.json
                                                   → Validated complete staged policy set
Live:     git diff -- .agents                      → (empty — no live policy changes)
```


## Prior Review Resolution

- **S01** ✓: `test_costs_applies_each_filter_at_the_cli_boundary` added in
  `tests/test_cli_opencode_costs.py:38–65`. Parameterized over all five filter options
  (`--since`, `--until`, `--directory`, `--agent`, `--model`). Each invokes the CLI via
  `CliRunner`, patches `OpenCodeSessionStore`, supplies two sessions that differ on the
  filtered dimension, and asserts the expected session ID appears in the JSON output.
  The `--since` case correctly expects the _later_ session (excluded means the earlier one
  falls before the date); all others assert `"matching"`. Evidence: `opencode_costs.py`
  filter logic exercised end-to-end through the CLI contract.

- **S02** ✓: Validator Zen-model check replaced with path-scoped regex
  `_ZEN_DISPATCH` (`validate_staged_agent_policies.py:11–13`), limited to files under
  `.agents/agents/`. The negative-lookahead `(?!.*\b(?:do not|don't|not)\b.*opencode/)`
  excludes negated mentions. Principal-ownership check replaced with structured regex
  `_PRINCIPAL_OWNERSHIP` (`validate_staged_agent_policies.py:15–18`) that requires
  `own/decid/control` within 120 characters of `principal` and `risk/escalat` in the
  same proximity. Fixture tests confirm acceptance, benign mentions pass, negated
  dispatch passes, and a weak ownership text (`"participates in reviews"`) fails.
  Evidence: `test_validate_staged_agent_policies.py:25–53`.

- **S03** ✓: `build_report` now collects `_estimate(session)` once per session into
  `estimates = [_estimate(session) for session in selected]` at `opencode_costs.py:253`,
  then destructures with `for session, (estimate, status) in zip(selected, estimates):`
  at `opencode_costs.py:257`. No second call to `_estimate` anywhere in the loop body.

- **T01** — Not resolved (accepted). Journal explicitly notes T01 is a project-policy
  issue: the coverage threshold is workspace-wide and the focused command should use
  `--no-cov`. The journal documents this and the focused command now consistently uses
  `--no-cov -q`. No regression.

- **T02** ✓: `assert self.conn is not None` at old line 117 replaced with an explicit
  `if self.conn is None: raise OpenCodeCostError(...)` at `opencode_costs.py:117–118`.
  Same replacement applied at the `sessions()` entry guard `opencode_costs.py:169–170`.
  Both guards are now optimizer-safe.


## Acceptance Criteria Verification

All ACs from iteration 01 carry forward unchanged. New tests added for S01 and S02 do not
alter existing ACs. Selected spot-checks for changed files:

| AC      | Status | Evidence                                                                                      |
| ------- | ------ | --------------------------------------------------------------------------------------------- |
| 04/AC07 | ✓      | `test_costs_applies_each_filter_at_the_cli_boundary` (was ⚠ in iteration 01)                |
| 06/AC03 | ✓      | `_ZEN_DISPATCH` path-scoped regex + `_PRINCIPAL_OWNERSHIP` structured regex (was ⚠)         |
| All others | ✓   | Unchanged from iteration 01 — no regressions detected                                        |


## Scope Verification

Changes since iteration 01 touch only files already in scope:

| File                                           | Change                                    | Justified By         | Status |
| ---------------------------------------------- | ----------------------------------------- | -------------------- | ------ |
| `tests/test_cli_opencode_costs.py`             | Added parameterized filter test (S01 fix) | Task 04 AC07 / S01   | ✓      |
| `tools/validate_staged_agent_policies.py`      | Regex-based dispatch + ownership checks   | Task 06 AC03 / S02   | ✓      |
| `tests/test_validate_staged_agent_policies.py` | New (4 tests for validator contract)      | Task 06 AC03 / S02   | ✓      |
| `src/dot_tools/opencode_costs.py`              | `_estimate` dedup (S03) + guard → raise (T02) | Tasks 01–03 / S03, T02 | ✓  |


## Findings

### Summary

| Finding | Title                                              | Outcome                   |
| ------- | -------------------------------------------------- | ------------------------- |
| T01*    | Focused suite requires `--no-cov` (carried over)   | Accepted — see note below |
| T03     | `--since` filter test asserts inverted expectation | Trivial                   |


### Trivial

#### T03: `--since` filter test asserts the non-obvious session

##### Where

`tests/test_cli_opencode_costs.py:64`

```python
expected = "excluded" if option == "--since" else "matching"
```


##### Issue

The `--since 2025-10-10` case correctly excludes `"matching"` (timestamp `1760000000000` ≈
2025-10-09 UTC, which is one day _before_ `2025-10-10`) and retains `"excluded"` (timestamp
`1760086400000` ≈ 2025-10-10). The logic is correct, but the session named `"excluded"` is
the _retained_ session for this case while the session named `"matching"` is the _excluded_
one. This naming inversion will confuse the next reader who modifies the test.


##### Fix

Rename the sessions to `"earlier"` and `"later"` (or `"session_a"` / `"session_b"`), and
document the expected result for each option in a comment. No behavioral change required.


##### Outcome


----

> **T01 (carried from iteration 01)**: Focused `pytest` run without `--no-cov` exits non-zero
> due to project-wide 70% threshold. The journal documents this and the implementation uses
> `--no-cov -q` in all verification commands. Accepted as-is; no production impact.


## Skills Applied

- `review-implementation-execution`: global fallback (`~/.agents/skills/review-implementation-execution/SKILL.md`)


## Decision

**APPROVED**

All quality gates pass: ruff, 190 pytest (up from 182), 77.69% coverage, staged validator,
git diff clean. All five prior findings are resolved or accepted (T01). No Critical or
Significant findings remain. T03 is cosmetic and does not affect correctness.

The staged policy tree remains human-gated per the promotion handoff. This review does not
constitute promotion approval.
