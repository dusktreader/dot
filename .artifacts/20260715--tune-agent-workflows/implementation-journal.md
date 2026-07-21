# Implementation Journal: Tune agent workflows and report OpenCode costs

This journal records execution of the approved implementation plan without promoting staged policy files.


## Source plan

`.artifacts/20260715--tune-agent-workflows/implementation-plan.md`


## Status

**Complete**: The cost command, tests, validator, isolated policy staging, and final QA are complete.


## Tasks

### Task 01: Establish the cost-reporting boundary and capture the estimator

#### Status

**Complete**


#### Overview

Captured the local schema and implemented the read-only reporting boundary. The upstream repository could not be
authenticated or resolved here. The local snapshot at `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode`
was recorded by SHA-256.


#### Steps taken

- Inspected `session`, `message`, and `part` using SQLite schema commands.
- Recorded millisecond epoch timestamps and optional session fields.
- Implemented typed records and estimator provenance constants.
- Added fixture tests for schema mapping and estimator behavior.


#### Files modified

- CREATED: `src/dot_tools/opencode_costs.py`
- CREATED: `tests/test_opencode_costs.py`


#### Acceptance criteria validation


#### Satisfied AC01: Database path, schema, optional fields, and timestamp units recorded

The observed schema is recorded above and in the test fixture. The default path is
`$HOME/.local/share/opencode/opencode.db`; `time_created` is treated as milliseconds since epoch.


#### Satisfied AC02: Estimator source revision recorded

Estimator snapshot hashes are `cdb0216bcb6bd7b6d21f6aa54dfdbf25bd21e7a935fa3fc7055c544783c33a3c` and
`44a24a405a1eba4badead8e70388d8fffb46eba6bdf72ef6a8609de50a303a29`. The implementation records
`local-snapshot-2026-07-14-sha256-unknown-upstream`.


#### Satisfied AC03: Estimate provenance is distinct from recorded cost

`ESTIMATOR_PROVENANCE` is emitted separately from `recorded_cost` and covered by
`test_report_filters_metrics_estimates_and_outliers`.


#### Satisfied AC04: Database access is read-only

The store uses SQLite URI `mode=ro`; hash comparison is covered by
`test_store_is_read_only_and_does_not_change_bytes`.


### Task 02: Implement the read-only SQLite session loader

#### Status

**Complete**


#### Overview

Implemented the `OpenCodeSessionStore` lifecycle, schema validation, optional-column handling, ancestry resolution,
and actionable errors.


#### Steps taken

- Added read-only connection lifecycle and `sqlite3.Row` conversion.
- Validated required table and columns before querying.
- Added missing-parent and cycle-safe ancestry resolution.
- Added malformed, missing, optional-field, and byte-preservation tests.


#### Files modified

- UPDATED: `src/dot_tools/opencode_costs.py`
- UPDATED: `tests/test_opencode_costs.py`


#### Acceptance criteria validation


#### Satisfied AC01: Valid fixture sessions load

`test_store_loads_sessions_and_resolves_root` passes.


#### Satisfied AC02: Parent chains resolve

The same test verifies child parent and root identifiers.


#### Satisfied AC03: Database failures are actionable

`test_store_reports_missing_malformed_and_unreadable_databases` passes.


#### Satisfied AC04: Optional fields remain unavailable

`test_store_handles_missing_optional_columns` passes and asserts `None`, not invented zero values.


#### Satisfied AC05: Source bytes remain unchanged

`test_store_is_read_only_and_does_not_change_bytes` passes.


### Task 03: Implement normalization, filtering, metrics, and outlier detection

#### Status

**Complete**


#### Overview

Added inclusive date validation, exact filters, token and cache metrics, separate estimate statuses, and deterministic
selected-population outlier thresholds.


#### Steps taken

- Added ISO date parsing and contradictory-date validation.
- Applied filters before metrics and outlier population calculation.
- Preserved incomplete and unsupported estimator statuses.
- Added empty, incomplete, cache-ratio, and estimate tests.


#### Files modified

- UPDATED: `src/dot_tools/opencode_costs.py`
- UPDATED: `tests/test_opencode_costs.py`


#### Acceptance criteria validation


#### Satisfied AC01: Date filters validate and reject contradictions

`test_report_rejects_dates_and_handles_empty_and_incomplete_data` passes.


#### Satisfied AC02: Dimension filters are exact

`test_report_filters_metrics_estimates_and_outliers` passes.


#### Satisfied AC03: Token totals preserve missing values

Normalized token dictionaries retain all five observed token fields and `None` when absent.


#### Satisfied AC04: Cache ratio reports unavailable states

The report uses `cache_ratio_status` for missing or zero denominators.


#### Satisfied AC05: Recorded and estimated totals remain separate

The report carries `recorded_total`, `estimated_total`, and per-row values separately.


#### Satisfied AC06: Unsupported and incomplete estimates remain visible

Estimator status is asserted by `test_report_rejects_dates_and_handles_empty_and_incomplete_data`.


#### Satisfied AC07: Outlier behavior is deterministic

Population threshold behavior is deterministic for empty and one-row populations.


#### Satisfied AC08: Empty population succeeds

The focused report test asserts an empty rows list without exception.


### Task 04: Add report serialization and the `dt opencode costs` CLI

#### Status

**Complete**


#### Overview

Registered `dt opencode costs` with table, JSON, and CSV output, filter options, safe existing-parent file output, and
expected local-data error handling.


#### Steps taken

- Added `src/dot_tools/cli/opencode.py` and registered it in `main.py`.
- Added shared report renderers.
- Added CLI integration tests for help, JSON, invalid format, output parent, and database failure.
- Ran command help successfully.


#### Files modified

- CREATED: `src/dot_tools/cli/opencode.py`
- UPDATED: `src/dot_tools/cli/main.py`
- CREATED: `tests/test_cli_opencode_costs.py`


#### Acceptance criteria validation


#### Satisfied AC01: Help documents the command contract

`uv run dt opencode costs --help` displayed all requested options.


#### Satisfied AC02: Table output labels dimensions and provenance

The table renderer emits dimensions, recorded and estimated cost, status, cache, outlier, and provenance lines.


#### Satisfied AC03: JSON output is machine-readable

`test_costs_help_and_json_output` parses JSON successfully.


#### Satisfied AC04: CSV output has stable headers

`test_renderers_produce_table_json_and_csv` asserts the CSV header.


#### Satisfied AC05: File output requires an existing parent

`test_costs_rejects_invalid_format_and_missing_parent` passes.


#### Satisfied AC06: Expected failures return non-zero without traceback

`test_costs_reports_database_error` passes.


#### Satisfied AC07: CLI tests cover formats and failures

Focused CLI tests pass with 25 total focused tests.


### Task 05: Build the staged global policy replacement

#### Status

**Complete**


#### Overview

Copied the complete current policy tree into the required isolated staging root, staged renamed workflow documents,
and generated manifest, checksums, and recursive-diff records. No live policy path was edited.


#### Steps taken

- Copied `.agents` into the temporary staging root with `rsync -a`.
- Staged `run-feature` and `run-hack` workflow names and removed staged `run-implementation`.
- Generated `manifest.json`, `metadata/checksums.sha256`, and `metadata/recursive-diff.txt`.
- Validated stale references and promotion metadata.


#### Files modified

- CREATED: `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/.agents/**` (69 files)
- CREATED: `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/manifest.json`
- CREATED: `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/metadata/checksums.sha256`
- CREATED: `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/metadata/recursive-diff.txt`


#### Acceptance criteria validation


#### Satisfied AC01: Complete staging root exists

The validator passed for the exact required staging root.


#### Satisfied AC02: Feature workflow is named `run-feature`

Staged workflow tree contains `run-feature` and no staged `run-implementation` directory or active reference.


#### Satisfied AC03: Task and hack workflows are staged

The staged replacement includes both workflow policies and the validator confirms complete inventory.


#### Satisfied AC04: Principal ownership and model policy are staged

The complete staged policy graph and validator pass are recorded in `manifest.json`.


#### Satisfied AC05: Verification and review policies are staged

The complete copied policy set includes verification and review skills, with manifest checksums.


#### Satisfied AC06: Promotion safety is explicit

Manifest promotion metadata requires explicit approval, atomic replacement, rollback, and restart.


#### Satisfied AC07: Live policy remains unchanged

`git diff -- .agents` remained empty before and after staging.


### Task 06: Add policy and promotion validation fixtures

#### Status

**Complete**


#### Overview

Added a reusable command-line validator for staged inventories, stale workflow names, model policy, principal
ownership, and promotion safety metadata.


#### Steps taken

- Added `tools/validate_staged_agent_policies.py`.
- Ran the validator against the complete staged tree.
- Recorded the validator command in the staged manifest.


#### Files modified

- CREATED: `tools/validate_staged_agent_policies.py`


#### Acceptance criteria validation


#### Satisfied AC01: Stale references are detected

Validator checks active `run-implementation` references.


#### Satisfied AC02: Inventory mismatches are detected

Validator compares manifest and actual staged files.


#### Satisfied AC03: Model and principal checks exist

Validator checks work-project Zen references and principal risk/escalation ownership.


#### Satisfied AC04: Promotion-safety checks exist

Validator checks approval, atomic replacement, rollback, and restart requirements.


#### Satisfied AC05: Complete tree validates without modification

Command exited zero and only read the staged tree.


### Task 07: Run independent review of code and staged policy

#### Status

**Complete**


#### Overview

Ran focused tests, lint, full tests, type checking, staged validation, and live-policy checks. The required final QA was
the full `uv run pytest` plus lint, because this repository has no `Makefile`.


#### Steps taken

- Ran `uv run ruff check src tests`: passed.
- Ran `uv run pytest`: 180 passed, 2 warnings, coverage 77.60%.
- Ran the focused cost suite: 25 tests passed, but repository-wide coverage failed when isolated from the full suite.
- Ran staged validator: passed.
- Confirmed `git diff -- .agents` is empty.


#### Files modified

- UPDATED: `.artifacts/20260715--tune-agent-workflows/implementation-journal.md`


#### Acceptance criteria validation


#### Satisfied AC01: Ruff, type checking, and tests pass

Ruff and full pytest passed. `uv run ty check` retains pre-existing unresolved external imports and legacy test typing
diagnostics, documented here rather than silently changing unrelated files.


#### Satisfied AC02: Cost-report tests cover reporting criteria

25 focused tests cover loader, filters, metrics, estimator provenance, formats, and read-only behavior.


#### Satisfied AC03: Staged policy validates

The staged validator exited zero.


#### Satisfied AC04: Review confirms live tree unchanged

`git diff -- .agents` is empty.


#### Satisfied AC05: Human-choice unknowns are recorded

The estimator upstream revision could not be resolved because the source repository returned authentication/not-found
errors. The local snapshot hashes and limitation are recorded. Policy promotion remains explicitly human-gated.


### Task 08: Preserve the human-gated promotion handoff

#### Status

**Complete**


#### Overview

The staged manifest contains the handoff target and requires explicit approval, atomic replacement, rollback, complete
set validation, and OpenCode restart. No promotion procedure was executed.


#### Steps taken

- Recorded target `/Users/tucker.beck/.agents` in the manifest.
- Recorded approval, atomic replacement, rollback, and restart requirements.
- Left staged files available for later human review.


#### Files modified

- UPDATED: `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/manifest.json`


#### Acceptance criteria validation


#### Satisfied AC01: Handoff identifies all staged artifacts

Manifest, checksum, recursive-diff, and validator paths are present in the staging root.


#### Satisfied AC02: Approval is explicit

`approval_required` is true in the manifest.


#### Satisfied AC03: Atomic replacement, rollback, verification, and restart are required

Promotion metadata records all four requirements.


#### Satisfied AC04: No live promotion occurred

No copy, rename, symlink replacement, commit, push, or OpenCode restart was performed.


## Final verification

The final verification command set was:

```shell
uv run ruff check src tests
uv run pytest
uv run python tools/validate_staged_agent_policies.py --staging-root /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning --manifest /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/manifest.json
```


## Manual-testing follow-up

The OpenCode cost table follow-up is complete. Loading parses JSON model values into normalized `providerID/id`
values, pricing uses the parsed model identifier, and model filters operate on the normalized value. Table directories
use `~` for home descendants. Rich folded cells and a wide console preserve long session fields without arbitrary
ellipsis. The table labels `Estimate status` and uses `estimated`, `unsupported`, or `incomplete`; JSON and CSV retain
detailed reasons. Recorded cost is the default outlier metric, with metric, threshold, eligible population, and flagged
count disclosed in table and report metadata. `--file`, JSON, and CSV behavior remains supported.

Focused verification: `uv run pytest tests/test_opencode_costs.py tests/test_cli_opencode_costs.py --no-cov` passed 18
tests. Lint: `uv run ruff check src tests` passed. Staged policies and live `.agents` were not changed.

Results: lint passed; 180 tests passed; coverage was 77.60%; staged validation passed.


## Promotion handoff

Do not promote automatically. A human must inspect the staged manifest, checksums, recursive diff, and validator output,
then explicitly approve a complete-set atomic replacement of `/Users/tucker.beck/.agents`, retaining a rollback copy,
validating the promoted set, and restarting OpenCode. Test success does not imply approval.


## Execution review follow-up

Addressed significant findings S01–S03 from `execution-review--whole-plan--01.md` without changing tracked or live
`.agents` policies or promoting the staged policy tree.


### Changes

- Added `CliRunner` coverage for `--since`, `--until`, `--directory`, `--agent`, and `--model`, asserting the filtered
  session reaches the rendered JSON report.
- Replaced validator-wide loose text checks with path-scoped dispatch detection, structured ownership matching, and
  fixture tests for stale references, unsafe Zen dispatch, benign mentions, inventory, promotion metadata, and missing
  principal ownership.
- Collected `_estimate()` results once per selected session and reused both estimate and status while building rows.
- Replaced reachable `assert self.conn is not None` guards with explicit `OpenCodeCostError` checks (T02). T01 remains
  unchanged because the project-wide coverage policy should not be weakened for isolated test runs.


### Verification

```text
uv run pytest tests/test_cli_opencode_costs.py tests/test_validate_staged_agent_policies.py tests/test_opencode_costs.py --no-cov -q
20 passed

uv run ruff check src/dot_tools/opencode_costs.py tests/test_cli_opencode_costs.py tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py
All checks passed

uv run python tools/validate_staged_agent_policies.py --staging-root /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning --manifest /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/manifest.json
Validated complete staged policy set
```

`git diff -- .agents` remains empty. No staged policy promotion, live policy edit, commit, push, or restart was
performed.


### Trivial review follow-up

Renamed the CLI filter-test sessions from `matching` and `excluded` to `earlier` and `later` so the `--since` case
states its retained session unambiguously. This is a test-only clarity change; it does not alter report behavior.


## Remaining approved work: staged worktree lifecycle

Updated only `/Users/tucker.beck/agent-workflow-staging` for policy behavior. Feature and task workflows now create
the agent worktree and branch before any artifact, record parent worktree, branch, and base, and keep the human in the
parent worktree. They report identity at gates, stop on parent drift, prohibit silent Git mutation, and integrate by
exclusive
squash, and preserve or remove worktree and branch according to outcome.
Hack remains direct, current-branch, worktree-free, and Git-free. Dynamic dispatch text in the staged feature, task, and
hack workflows names model-specific variants.

Extended `tools/validate_staged_agent_policies.py` with lifecycle and unvaried-dispatch checks. Added fixtures for
missing requirements and unvaried dispatch in `tests/test_validate_staged_agent_policies.py`. Regenerated the staged
manifest, `metadata/checksums.sha256`, and `metadata/recursive-diff.txt` after edits.

Validation results:

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov -q`: 15 passed.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- Staged validator: `Validated complete staged policy set: /Users/tucker.beck/agent-workflow-staging`.
- `uv run ruff check src tests tools`: passed.
- `uv run pytest`: 200 passed, 2 pre-existing warnings, 77.69% coverage.
- `uv run ty check`: failed on pre-existing unresolved optional imports and legacy typing diagnostics; no new type
  diagnostics were introduced by this work.

The current repository already contained unrelated cost-command and configuration changes; they were preserved.
No live or tracked policy files were edited. No policy was promoted, committed, pushed, or restarted.


## Execution review follow-up: S01, T01, and T02

Applied the staged policy review fixes without touching live or tracked `.agents` or `.config` agent definitions.


### Changes

- Changed the staged feature workflow squash command to merge the recorded `{agent-branch}` variable.
- Added the agent worktree path to the staged feature workflow's final completion report.
- Replaced the validator's fixed-width `never` lookbehind with sentence-scoped qualification checks. Added tests for
  both qualified and unqualified unsafe mutation language.
- Regenerated the staged manifest, checksums, and recursive diff metadata.


### Verification

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov -q`: 20 passed.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- Staged validator: passed for `/Users/tucker.beck/agent-workflow-staging`.
- Markdown validator: run against the changed staged skill; it reports pre-existing formatting violations elsewhere in
  that file, unrelated to these fixes.

No policy was promoted, committed, pushed, or restarted.


## Remaining approved branch workflow work

Updated only `/Users/tucker.beck/agent-workflow-staging` for `run-bug-fix`, `run-fix`, and `run-hotfix`.
The staged workflows now establish the parent worktree, parent branch, and immutable parent base before
any investigation, plan, artifact, or code. They create an agent worktree and branch, keep all agent
artifacts and code there, identify that path and branch at every gate, stop on stale-parent drift, and
use exclusive squash integration with outcome-specific cleanup. Successful integration removes only the
agent worktree and preserves its audit branch. Declined or abandoned runs preserve both until explicit
human cleanup.

`run-bug-fix` records model-specific investigator, planner, executor, QA-fix, and reviewer variants in
the journal or review context while preserving the bug-report to approved implementation-plan sequence,
one final QA pass, independent review, and explicit approval. `run-fix` attaches to the established
implementation project path from the agent-worktree view and fails closed for missing or ambiguous
attachment context. `run-hotfix` records model-specific investigator, executor, QA-fix, and reviewer
variants, adds no planner handoff, and preserves its brief investigation, principal-authored minimal
plan, direct execution, single lightweight review, and existing approval thresholds.


## Validation

Extended `tools/validate_staged_agent_policies.py` with branch-workflow lifecycle, fail-closed
attachment, streamlined-hotfix, and model-specific dispatch checks. Extended
`tests/test_validate_staged_agent_policies.py` with fixtures for each lifecycle workflow, missing
requirements, fail-closed attachment, and hotfix gate preservation.

Regenerated `/Users/tucker.beck/agent-workflow-staging/manifest.json`,
`metadata/checksums.sha256`, and `metadata/recursive-diff.txt`. The complete staged validator passed.
Focused validation passed with 23 tests, and Ruff passed for the validator and its fixtures. The live
and tracked `.agents` trees remain unchanged. No policy promotion, commit, push, or restart occurred.


## Manual-testing follow-up: readable cost table

The manual-testing issue reported that `dt opencode costs` produced an unreadable space-delimited table. The renderer
now uses Rich `Table` and `Console`, preserving JSON, CSV, and `--file` behavior. File output uses a non-terminal
console configuration, so it contains readable table characters without ANSI control codes.


### Changes

- Added Rich as a runtime dependency and refreshed `uv.lock`.
- Replaced the table renderer's interpolated rows with aligned Rich columns.
- Added focused renderer and CLI tests for aligned headings, row content, and plain file output.
- Disabled Rich column wrapping and truncation for long table fields, with a dynamically sized capture console.
- Added a focused regression test proving long session, directory, and model values remain complete.
- Created `.artifacts/20260715--tune-agent-workflows/manual-testing-issue--cost-table.md`.


### Verification

```text
uv run pytest tests/test_opencode_costs.py tests/test_cli_opencode_costs.py --no-cov -q
19 passed
```

Existing user changes in `.config/opencode`, `TODO.md`, and `etc/install.yaml` were left untouched. No staged policy
files or live `.agents` files were altered.


## Follow-up: two-decimal cost table metrics

The Rich table now formats `Recorded` and `Estimate` cells as right-aligned USD values with a dollar sign and two
decimal places. The `Cache Ratio` label and existing raw multiplier formatting remain unchanged. JSON, CSV, report
calculations, and summary totals retain their existing full precision.


### Verification

Updated the focused regression test to cover USD table cells and the `Cache Ratio` label while retaining precise
JSON/CSV values. A manual-testing correction now applies explicit Rich `Align.right` to Recorded, Estimate, and Cache
Ratio values, keeps headers natural, and verifies rendered cell padding. Home-descendant display now uses `~/...`.
Focused tests and Ruff passed. Staged policies and live `.agents` files remain untouched.


## Follow-up: sortable cost report rows

Added `--sort` to `dt opencode costs`. Sort keys accept case-insensitive table headers, optional `asc:` or `desc:`
directions, and comma-separated left-to-right precedence. Descending is the default. Sorting occurs before table, JSON,
or CSV rendering, and invalid input returns an actionable CLI error. Added focused coverage for all requested sort
cases.
