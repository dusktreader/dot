# Execution Review: Tune agent workflows and report OpenCode costs

## Source Artifacts

- **Implementation journal**: `.artifacts/20260715--tune-agent-workflows/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260715--tune-agent-workflows/implementation-plan.md`


## Scope

**whole-plan** — Iteration 01


## Issue Summary

- **Critical**:    0
- **Significant**: 3
- **Trivial**:     2


## Verification Evidence

```text
Linter:   uv run ruff check src tests       → All checks passed
Tests:    uv run pytest                     → 182 passed, 2 warnings
Coverage: uv run pytest                     → 77.60% (threshold 70% met)
Types:    uv run ty check src/              → All checks passed
          uv run ty check (full workspace)  → pre-existing external import errors only
                                               (markdown, PIL — unrelated to this work)
Staged:   uv run python tools/validate_staged_agent_policies.py
          --staging-root .../agent-workflow-tuning
          --manifest .../agent-workflow-tuning/manifest.json
                                            → Validated complete staged policy set
Live:     git diff -- .agents               → (empty — no live policy changes)
```


## Acceptance Criteria Verification

| AC      | Status | Evidence                                                                                                            |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | Schema recorded in journal; `make_database` fixture in `tests/test_opencode_costs.py:19`                            |
| 01/AC02 | ⚠      | `ESTIMATOR_REVISION = "local-snapshot-2026-07-14-sha256-unknown-upstream"` — upstream repo                          |
|         |        | auth failed; local SHA-256 hashes recorded. Limitation documented explicitly.                                       |
| 01/AC03 | ✓      | `ESTIMATOR_PROVENANCE` separate from `recorded_cost`; `opencode_costs.py:18,59`                                     |
| 01/AC04 | ✓      | SQLite URI `mode=ro`; `test_store_is_read_only_and_does_not_change_bytes`                                           |
| 02/AC01 | ✓      | `test_store_loads_sessions_and_resolves_root`; `opencode_costs.py:166–204`                                          |
| 02/AC02 | ✓      | `test_store_loads_sessions_and_resolves_root`; `root_id` and `parent_id` assertions                                 |
| 02/AC03 | ✓      | `test_store_reports_missing_malformed_and_unreadable_databases`; `opencode_costs.py:103,113`                        |
| 02/AC04 | ✓      | `test_store_handles_missing_optional_columns`; `None` asserted, not zero                                            |
| 02/AC05 | ✓      | `test_store_is_read_only_and_does_not_change_bytes`; SHA-256 before/after                                           |
| 03/AC01 | ✓      | `test_report_rejects_dates_and_handles_empty_and_incomplete_data`; `opencode_costs.py:236–238`                      |
| 03/AC02 | ✓      | `test_report_filters_metrics_estimates_and_outliers`; exact-match filter `opencode_costs.py:244–249`                |
| 03/AC03 | ✓      | `tokens` dict with five keys; `None` when absent; `opencode_costs.py:157–159`                                       |
| 03/AC04 | ✓      | `cache_ratio_status`; `opencode_costs.py:258–259`                                                                   |
| 03/AC05 | ✓      | `ReportRow.recorded_cost` / `local_estimate`; `Report.recorded_total` / `estimated_total`                           |
| 03/AC06 | ✓      | `test_report_rejects_dates_and_handles_empty_and_incomplete_data` incomplete status check                           |
| 03/AC07 | ✓      | `opencode_costs.py:253`; threshold `None` for ≤1 rows; deterministic                                                |
| 03/AC08 | ✓      | Empty list → `Report(rows=[])` without exception                                                                    |
| 04/AC01 | ✓      | `cli/opencode.py:14–23`; all options present                                                                        |
| 04/AC02 | ✓      | `render_report` table path; `opencode_costs.py:293–300`                                                             |
| 04/AC03 | ✓      | `test_costs_help_and_json_output`; JSON parsed successfully                                                         |
| 04/AC04 | ✓      | `test_renderers_produce_table_json_and_csv`; header `session_id` asserted                                           |
| 04/AC05 | ✓      | `cli/opencode.py:28–30`; parent-dir check; `test_costs_rejects_invalid_format_and_missing_parent`                   |
| 04/AC06 | ✓      | `test_costs_reports_database_error`; non-zero exit, no traceback                                                    |
| 04/AC07 | ⚠      | `--filter` options not individually exercised in CLI tests; no `--since`, `--agent`,                                |
|         |        | `--model`, `--directory` CLI-layer tests. Logic is tested in unit tests but CLI contract                            |
|         |        | path not covered from `CliRunner`. See S01.                                                                         |
| 05/AC01 | ✓      | Staging root present; `manifest.json` with 69 files                                                                 |
| 05/AC02 | ✓      | `run-feature` present; `run-implementation` absent from staged skills; diff confirms                                |
| 05/AC03 | ✓      | `run-task` and `run-hack` present in staged skills                                                                  |
| 05/AC04 | ✓      | `principal.md` modified in staged tree; manifest checksums present                                                  |
| 05/AC05 | ✓      | Review/verification skills present; manifest confirms                                                               |
| 05/AC06 | ✓      | `manifest.json` promotion block: `approval_required`, `atomic_replacement`, `rollback_required`, `restart_required` |
| 05/AC07 | ✓      | `git diff -- .agents` is empty                                                                                      |
| 06/AC01 | ✓      | `validate()` checks stale `run-implementation`; `tools/validate_staged_agent_policies.py:21`                        |
| 06/AC02 | ✓      | Inventory comparison; `validate_staged_agent_policies.py:16–19`                                                     |
| 06/AC03 | ⚠      | Zen model check uses `"opencode/"` heuristic which could produce false positives or false                           |
|         |        | negatives depending on content. Principal ownership check uses text search, not structured                          |
|         |        | assertions. See S02.                                                                                                |
| 06/AC04 | ✓      | Promotion-safety check; `validate_staged_agent_policies.py:27–29`                                                   |
| 06/AC05 | ✓      | Validator exited zero against real staged tree; no source files modified                                            |
| 07/AC01 | ✓      | Ruff: passed; pytest 182: passed; ty src/: passed                                                                   |
| 07/AC02 | ✓      | 10 focused cost tests; provenance, read-only, malformed, formats all covered                                        |
| 07/AC03 | ✓      | Staged validator exited zero                                                                                        |
| 07/AC04 | ✓      | `git diff -- .agents` empty; recorded in journal                                                                    |
| 07/AC05 | ✓      | Estimator upstream resolution failure documented; promotion remains human-gated                                     |
| 08/AC01 | ✓      | `manifest.json` lists staging root, checksums, validator path                                                       |
| 08/AC02 | ✓      | `approval_required: true`; journal: "Test success does not imply approval"                                          |
| 08/AC03 | ✓      | `atomic_replacement`, `rollback_required`, `restart_required` present                                               |
| 08/AC04 | ✓      | No promotion executed; confirmed by git status and diff                                                             |


## Scope Verification

| File                                              | Justified By        | Status |
| ------------------------------------------------- | ------------------- | ------ |
| `src/dot_tools/opencode_costs.py`                 | Tasks 01–03, 04     | ✓      |
| `src/dot_tools/cli/opencode.py`                   | Task 04             | ✓      |
| `src/dot_tools/cli/main.py`                       | Task 04, Step 3     | ✓      |
| `tests/test_opencode_costs.py`                    | Tasks 01–03         | ✓      |
| `tests/test_cli_opencode_costs.py`                | Task 04, Step 1     | ✓      |
| `tests/test_validate_staged_agent_policies.py`    | Task 06, Step 1     | ✓      |
| `tools/validate_staged_agent_policies.py`         | Task 06, Step 2     | ✓      |
| `.artifacts/.../implementation-journal.md`        | Task 07 (QA record) | ✓      |
| `/tmp/.../agent-workflow-tuning/**` (staged only) | Tasks 05, 06, 08    | ✓      |


## Findings

### Summary

| Finding | Title                                                      | Outcome |
| ------- | ---------------------------------------------------------- | ------- |
| S01     | CLI filter options lack CliRunner test coverage            |         |
| S02     | Validator Zen-model heuristic is fragile                   |         |
| S03     | `build_report` calls `_estimate` twice per row             |         |
| T01     | Focused cost suite fails in isolation (coverage threshold) |         |
| T02     | `assert` used for internal invariant in `_validate_schema` |         |


### Significant

#### S01: CLI filter options lack CliRunner test coverage


#### Where

`tests/test_cli_opencode_costs.py` — no tests for `--since`, `--until`, `--directory`, `--agent`, `--model`


#### Issue

Task 04 AC07 requires CLI tests to cover "every filter". The three existing CLI tests cover JSON output, invalid
format, missing parent, and database error. The five filter options are passed through `costs()` to `build_report()`
without any CLI-layer test exercising them with a mocked store. The filter logic itself is well-tested in
`test_opencode_costs.py`, but the CLI contract — that the option names reach the underlying call — is unverified.


#### Impact

A future refactor that silently drops a filter option from the CLI definition would not be caught by tests.


#### Fix

Add CliRunner tests for at least `--since`, `--directory`, and `--model` that assert the matching sessions pass
through and non-matching sessions are excluded. A single parameterized test with a mocked store is sufficient.


#### Outcome


----

#### S02: Validator Zen-model heuristic is fragile


#### Where

`tools/validate_staged_agent_policies.py:23` — `if "opencode/" in text and "work-project" in text`


#### Issue

The check reports a Zen-model violation when both the strings `opencode/` and `work-project` appear anywhere in the
concatenated policy text. Because both strings can appear in legitimate context (a policy file explaining what *not*
to do, or referencing these strings in examples), the check produces false positives. Conversely, a Zen model
reference expressed differently (e.g., `opencode/zen`) in a file that does not contain `work-project` on the same
scan pass would be missed.

The principal-ownership check at line 25 is similarly loose — presence of the words `principal`, `risk`, and
`escalat` anywhere in the combined text does not confirm they appear together in a structural ownership statement.


#### Impact

The validator could pass a staged tree that violates the Zen-model and principal-ownership requirements, or reject a
valid one. Its guarantee is weaker than the AC implies.


#### Fix

Tighten the heuristic or document the limitation as an accepted approximation. At minimum, add a comment noting the
check is text-search based, not structural, so reviewers know to inspect flagged and unflagged files manually.
Alternatively, check for the model string only in files that are identified as dispatch policies by their path
(e.g., files under `agents/`).


#### Outcome


----

#### S03: `build_report` calls `_estimate` twice per row


#### Where

`src/dot_tools/opencode_costs.py:251,260` — `_estimate` called once to populate `estimates` list, again inside the
loop via `status = _estimate(session)[1]`


#### Issue

`_estimate` is called twice for every session: once at line 251 to compute the value list, and again at line 260
inside the row-building loop to retrieve only the status string. Because `_estimate` is pure and the input is
unchanged, the results are identical, but the redundant call doubles the computation and makes the code harder to
follow.


#### Impact

No correctness risk. Performance is negligible at current scale. Code clarity suffers slightly.


#### Fix

Unpack both the estimate value and status in a single pass:

```python
estimates = [_estimate(s) for s in selected]  # list of (value, status) tuples
# then in the loop:
estimate, status = estimates[i]
```

or collect `(value, status)` tuples in the first pass and destructure in the loop.


#### Outcome


----

### Trivial

#### T01: Focused cost suite fails in isolation due to coverage threshold


#### Where

`pyproject.toml` coverage configuration — running `uv run pytest tests/test_opencode_costs.py
tests/test_cli_opencode_costs.py` exits with a coverage failure


#### Issue

The plan documents a focused test command. Running it in isolation produces a coverage failure (`41% < 70%`) because
the threshold is project-wide and the focused run excludes the other modules that other tests cover. The 10 tests
pass; only the exit code signals failure. The journal notes this but it can mislead CI or a reviewer who runs only
the focused command.


#### Impact

No production impact. Confusion risk during development and review.


#### Fix

Document in the plan's focused-test command that it requires `--no-cov` or `--cov-fail-under=0` when run in
isolation, or add a `pyproject.toml` override for the focused suite.


#### Outcome


----

#### T02: `assert` used for internal invariant in `_validate_schema`


#### Where

`src/dot_tools/opencode_costs.py:117` — `assert self.conn is not None`


#### Issue

`assert` statements are stripped by Python's optimizer (`-O` / `-OO`) and should not be used to guard against
reachable runtime states. Although `self.conn` being `None` here is architecturally unreachable (the connection is
set in `__init__` before `_validate_schema` is called), using `assert` for safety invariants is inconsistent with
the codebase's other explicit error handling. The same pattern appears at `opencode_costs.py:169`.


#### Impact

No production impact under normal execution. Under `-O` flag the guard is silently removed.


#### Fix

Replace with a standard guard or document with a comment that the assertion is only for static analysis:

```python
if self.conn is None:  # pragma: no cover
    raise OpenCodeCostError("Connection unexpectedly closed before schema validation")
```

or just remove the assert and rely on the surrounding context if the unreachability is clear.


#### Outcome


----

## Skills Applied

- `review-implementation-execution`: global fallback (`~/.agents/skills/review-implementation-execution/SKILL.md`)


## Decision

**APPROVED — WITH RECOMMENDED CHANGES**

All quality gates pass (ruff, pytest 182 passed, ty src/, staged validator, git diff clean). All ACs are
satisfied with one documented exception: 01/AC02 upstream estimator revision is unresolvable due to authentication
failure; the limitation is explicitly recorded and promotion remains human-gated.

No Critical findings. S01, S02, and S03 are improvements but do not block delivery. T01 and T02 are cosmetic.

Recommended: address S01 (filter CLI tests) and S02 (validator heuristic comment) before policy promotion review,
as they relate directly to the correctness claims of the staged content and its test coverage.
