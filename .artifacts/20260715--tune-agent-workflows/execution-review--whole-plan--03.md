# Execution Review: Tune agent workflows and report OpenCode costs


## Source Artifacts

- **Implementation journal**: `.artifacts/20260715--tune-agent-workflows/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260715--tune-agent-workflows/implementation-plan.md`


## Scope

**whole-plan** — Iteration 03


## Issue Summary

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     2


## Verification Evidence

```
Linter:    uv run ruff check src tests tools  → All checks passed
Tests:     uv run pytest (focused)             → 30 passed (test_opencode_costs, test_cli_opencode_costs, test_validate_staged_agent_policies)
Tests:     uv run pytest (full suite)          → 200 passed, 2 pre-existing warnings
Coverage:  77.69% (above 70% threshold)
Staged validator: uv run python tools/validate_staged_agent_policies.py
                  --staging-root /Users/tucker.beck/agent-workflow-staging
                  --manifest /Users/tucker.beck/agent-workflow-staging/manifest.json
                  → Validated complete staged policy set: /Users/tucker.beck/agent-workflow-staging
Type check: uv run ty check → pre-existing unresolved optional imports and legacy typing diagnostics only; no new errors introduced
Live policy: git diff -- .agents → empty
Live .config/opencode/agents: unvaried static definitions, identical to tracked repo; no model variants promoted
```


## Acceptance Criteria Verification

| AC          | Status | Evidence                                                                                          |
| ----------- | ------ | ------------------------------------------------------------------------------------------------- |
| T01/AC01    | ✓      | `opencode_costs.py:27` default path; `opencode_costs.py:39–44` schema fields; tests fixture       |
| T01/AC02    | ✓      | `opencode_costs.py:17–18` `ESTIMATOR_REVISION` constant; journal records snapshot hashes          |
| T01/AC03    | ✓      | `opencode_costs.py:18` separate `ESTIMATOR_PROVENANCE`; `test_opencode_costs.py` provenance test  |
| T01/AC04    | ✓      | `opencode_costs.py:104` URI `mode=ro`; `test_store_is_read_only_and_does_not_change_bytes`        |
| T02/AC01    | ✓      | `test_store_loads_sessions_and_resolves_root`                                                      |
| T02/AC02    | ✓      | Same test; parent/root ID assertions                                                               |
| T02/AC03    | ✓      | `test_store_reports_missing_malformed_and_unreadable_databases`                                    |
| T02/AC04    | ✓      | `test_store_handles_missing_optional_columns`; `None` asserted, no invented zeros                 |
| T02/AC05    | ✓      | `test_store_is_read_only_and_does_not_change_bytes`; byte hash comparison                         |
| T03/AC01    | ✓      | `opencode_costs.py:209–216`, `238–240`; `test_report_rejects_dates_and_handles_empty_and_incomplete_data` |
| T03/AC02    | ✓      | `opencode_costs.py:246–251`; `test_report_filters_metrics_estimates_and_outliers`                 |
| T03/AC03    | ✓      | `opencode_costs.py:158–164` five token keys; `None` on absence                                    |
| T03/AC04    | ✓      | `opencode_costs.py:260–261` explicit denominator check; `cache_ratio_status`                      |
| T03/AC05    | ✓      | `opencode_costs.py:272–273` separate `recorded_total`, `estimated_total`                          |
| T03/AC06    | ✓      | `_estimate` returns status strings; `test_report_rejects_dates_and_handles_empty_and_incomplete_data` |
| T03/AC07    | ✓      | `opencode_costs.py:255` deterministic threshold; outlier tests                                    |
| T03/AC08    | ✓      | Empty-population test; `build_report` returns empty rows list                                     |
| T04/AC01    | ✓      | `cli/opencode.py:16–22` all options present; help integration test                                |
| T04/AC02    | ✓      | `opencode_costs.py:294–301` table renderer labels                                                 |
| T04/AC03    | ✓      | `test_costs_help_and_json_output`; `json.loads` asserted                                          |
| T04/AC04    | ✓      | `test_renderers_produce_table_json_and_csv`; CSV header asserted                                  |
| T04/AC05    | ✓      | `cli/opencode.py:28–30`; `test_costs_rejects_invalid_format_and_missing_parent`                   |
| T04/AC06    | ✓      | `cli/opencode.py:39–41`; `test_costs_reports_database_error`; exit 1 no traceback                 |
| T04/AC07    | ✓      | 30 focused tests cover all formats, filters, failures, and database paths                         |
| T05/AC01    | ✓      | Staging root `/Users/tucker.beck/agent-workflow-staging`; manifest confirms 89-file inventory      |
| T05/AC02    | ✓      | `run-feature/SKILL.md` present; no `run-implementation` in staged tree; validator passes           |
| T05/AC03    | ✓      | `run-feature`, `run-task`, `run-hack` present; validator checks gates, Git authority, escalation   |
| T05/AC04    | ✓      | Model variant inventory: 7 roles × (6 work + 5 personal) = 77 variants; validator checks all      |
| T05/AC05    | ✓      | Review and verification skills staged; validator checks them                                       |
| T05/AC06    | ✓      | `manifest.json:887–895` `approval_required`, `atomic_replacement`, `rollback_required`             |
| T05/AC07    | ✓      | `git diff -- .agents` empty; `.config/opencode/agents` unvaried definitions unchanged              |
| T06/AC01    | ✓      | `run-feature/SKILL.md:42–48` records parent worktree, branch, base; creates agent worktree first  |
| T06/AC02    | ✓      | `run-feature/SKILL.md:46–48` all artifacts in agent worktree; gate blocks report identity         |
| T06/AC03    | ✓      | `run-feature/SKILL.md:121–124` immediate pre-integration comparison; explicit human decision       |
| T06/AC04    | ✓      | `run-feature/SKILL.md:132–134` worktree removed on success; both preserved on decline/abandonment  |
| T06/AC05    | ✓      | `run-hack/SKILL.md:9` "no worktree", "no Git lifecycle"; validator confirms prohibitions           |
| T06/AC06    | ✓      | `run-feature/SKILL.md:175` model-specific variant dispatch; principal selects before each dispatch |
| T07/AC01    | ✓      | `validate_staged_agent_policies.py:183–192` lifecycle checks; actionable failures in tests         |
| T07/AC02    | ✓      | `test_validate_staged_agent_policies.py` covers feature, task, hack, stale-parent, variant fixtures |
| T07/AC03    | ✓      | Validator passes complete staged tree; no `run-implementation`; no Zen dispatch; principal ownership|
| T07/AC04    | ✓      | Validator reads staging root only; no source edits; `git diff -- .agents` empty                   |
| T08/AC01    | ✓      | `validate_staged_agent_policies.py:111` stale ref; `validate:97–98` inventory; `219–221` prohibitions |
| T08/AC02    | ✓      | `validate:88–98` inventory comparison                                                              |
| T08/AC03    | ✓      | `validate:116,152,170` Zen dispatch, principal ownership checks                                    |
| T08/AC04    | ✓      | `validate:226–228` promotion metadata checks                                                       |
| T08/AC05    | ✓      | Validator exits zero against complete staged tree; no source edits performed                       |
| T09/AC01    | ✓      | Ruff and pytest pass; 200 tests; ty pre-existing only                                              |
| T09/AC02    | ✓      | 30 focused tests across all reporting design criteria                                              |
| T09/AC03    | ✓      | Staged validator passes                                                                             |
| T09/AC04    | ✓      | Live `.agents` confirmed unchanged; `git diff -- .agents` empty                                    |
| T09/AC05    | ✓      | Estimator upstream revision unresolvable; recorded as explicit unknown; blocks promotion           |
| T10/AC01    | ✓      | `manifest.json:887–896` identifies staged root, validator, promotion target                        |
| T10/AC02    | ✓      | `manifest.json:888` `approval_required: true`; journal states test success ≠ approval             |
| T10/AC03    | ✓      | `manifest.json:890–893` atomic, rollback, restart; journal describes procedure                    |
| T10/AC04    | ✓      | No copy, rename, symlink, commit, push, or restart performed                                       |


## Scope Verification

| File                                                              | Justified By          | Status |
| ----------------------------------------------------------------- | --------------------- | ------ |
| `src/dot_tools/opencode_costs.py` (created)                       | Tasks 01–03           | ✓      |
| `src/dot_tools/cli/opencode.py` (created)                         | Task 04               | ✓      |
| `src/dot_tools/cli/main.py` (updated)                             | Task 04               | ✓      |
| `tests/test_opencode_costs.py` (created)                          | Tasks 01–03           | ✓      |
| `tests/test_cli_opencode_costs.py` (created)                      | Task 04               | ✓      |
| `tools/validate_staged_agent_policies.py` (created)               | Tasks 06–07 / T08     | ✓      |
| `tests/test_validate_staged_agent_policies.py` (created)          | Tasks 06–07 / T08     | ✓      |
| `/Users/tucker.beck/agent-workflow-staging/**` (staged tree)      | Tasks 05–06 / T08–10  | ✓      |
| `.artifacts/20260715--tune-agent-workflows/implementation-journal.md` | Task 09 (QA record) | ✓    |


## Prior Review Resolution

Prior reviews: `execution-review--whole-plan--01.md` (S01–S03) and `execution-review--whole-plan--02.md`.

All previously raised findings resolved. Iteration 02 confirmed resolution of S01–S03 from iteration 01.
This iteration adds the worktree lifecycle work (Tasks 06–07 extended staging), which was not present in prior reviews.

No unresolved findings carried forward.


## Findings

### Summary

| Finding | Title                                                      | Outcome |
| ------- | ---------------------------------------------------------- | ------- |
| S01     | `run-feature` squash step references wrong branch variable |         |
| T01     | `run-feature` step 5 completion report omits worktree path |         |
| T02     | Validator `_UNSAFE_MUTATION` pattern is brittle            |         |


### Significant

#### S01: `run-feature` squash step references wrong branch variable

##### Where

`/Users/tucker.beck/agent-workflow-staging/.agents/skills/run-feature/SKILL.md:128–130`


##### Issue

The squash command block reads:

```shell
git switch {parent-branch}
git merge --squash {parent-branch}--agents-build
git commit -m "<approved message>"
```

The merge source should be `{agent-branch}` (i.e. the `--agents-build` branch that was created in
the worktree setup), not the interpolated literal `{parent-branch}--agents-build`. If the parent
branch name already contains an `--agents-build` suffix or the agent branch was named differently,
this would silently merge the wrong ref. The rest of the document uses "agent branch" and "agent
worktree" consistently; the squash step uses a reconstructed name instead of the recorded variable.


##### Impact

A human following this instruction could merge the wrong local branch, silently squashing incomplete
or unrelated work.


##### Fix

Replace the merge source with `{agent-branch}` to use the exact recorded branch name:

```shell
git switch {parent-branch}
git merge --squash {agent-branch}
git commit -m "<approved message>"
```


##### Outcome


----

### Trivial

#### T01: `run-feature` step 5 completion report omits agent worktree path

##### Where

`/Users/tucker.beck/agent-workflow-staging/.agents/skills/run-feature/SKILL.md:378–387`


##### Issue

The step 5 completion report block lists the project directory, artifacts, `--agents-build` branch
name, squash commit SHA, and PR URL, but does not include the agent worktree path. Every prior gate
block explicitly carries the agent worktree path and agent branch (per AC02 contract). The final
report is the only gate that drops it, which is inconsistent.


##### Fix

Add `- The agent worktree path` to the completion report list.


##### Outcome


----

#### T02: Validator `_UNSAFE_MUTATION` regex is brittle for multi-line matching

##### Where

`tools/validate_staged_agent_policies.py:75–79`


##### Issue

`_UNSAFE_MUTATION` uses `re.DOTALL` but the leading negative lookbehind `(?<!never )` only looks back
4 characters. A phrase like "The policy will never silently rebase" places "never " more than one
token before "silently", so the lookbehind would miss it and report a false positive. The current
staged text passes validation because the staged documents say "Never silently" at sentence starts
rather than "never silently" mid-sentence, but the pattern is fragile for future policy edits.


##### Fix

Replace the lookbehind with a broader negative lookahead or scan for the "never" qualifier within the
same sentence. Alternatively, document the known limitation in a comment so maintainers know the
boundary.


##### Outcome


----

## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**APPROVED** — with findings noted for follow-up.

All quality gates pass (ruff, 200 tests, 77.69% coverage, staged validator). All 53 acceptance
criteria are satisfied. Live `.agents` and `.config/opencode/agents` are confirmed unchanged. No
policy was promoted, committed, pushed, or restarted.

S01 (wrong branch variable in squash command) and T01–T02 should be addressed before the staged
policy is promoted, but they do not block approval of the code implementation and the overall
staged artifact. S01 is the only item that affects correctness of the promotion procedure itself
and should be resolved in the staged skill before the human approves promotion.
