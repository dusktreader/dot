# Implementation Plan: Tune agent workflows and report OpenCode costs

Implement the OpenCode cost-reporting command in `dot-tools` and prepare, validate, and review a complete replacement
set for the global agent workflow policies without changing the live `~/.agents` tree. The implementation separates
recorded OpenCode costs from local estimates, keeps database access read-only, and leaves policy promotion for a later
human-approved operation. Extend the staged policy with explicit isolated-worktree lifecycles for `run-bug-fix`,
`run-fix`, and `run-hotfix`, including model-specific specialist dispatch and recording at every applicable handoff.


## Goal

Add an `opencode` command group with `dt opencode costs`, backed by a read-only SQLite reporting pipeline. The command
will discover or accept the local database path, reconstruct session ancestry, apply date, directory, agent, and model
filters, calculate token and cache metrics plus outlier indicators, and render one normalized result as a table, JSON,
or CSV. It will use a pinned snapshot of the selected `opencode-token-costs` estimator and will expose unsupported or
incomplete estimates instead of presenting them as zero-cost data.

Replace the current global workflow policy graph in a timestamped staging tree at
`/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning`. Stage the renamed feature, task,
and hack workflows, worktree lifecycle guidance, decision/model policy, verification/review guidance, and
atomic-promotion instructions there. Preserve the completed cost-command implementation and existing staging work;
extend the staged policy set and its validation for the approved worktree design without editing source or live staging
files during this plan revision. Preserve the completed cost implementation and existing staged policy work while
adding the remaining branch-based workflow coverage.
Validate and independently review the staged tree, record the source and destination manifests, and stop before any
copy or rename into tracked `.agents` or live `~/.agents`. A later human-approved promotion will perform the tracked
change and restart OpenCode.


## Project Commands

### Install dependencies

Prerequisites:

- `uv` installed and available on `PATH`
- Python `>=3.13`, as declared in `pyproject.toml`

Command:

```shell
uv sync
```

Expected Output:

The project environment is synchronized and includes the declared runtime and development dependencies.


### Run focused cost-report tests

Command:

```shell
uv run pytest tests/test_opencode_costs.py tests/test_cli_main.py -v
```

Expected Output:

All cost-pipeline and CLI integration tests pass, including filtering, serialization, estimator provenance, malformed
database handling, and read-only behavior.


### Run the project test suite

Command:

```shell
uv run pytest
```

Expected Output:

All tests pass with the repository's configured coverage threshold.


### Run lint and type checks

Command:

```shell
uv run ruff check src tests
uv run ty check
```

Expected Output:

Ruff reports no violations and `ty` reports no type errors.


### Validate Markdown artifacts

Command:

```shell
node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260715--tune-agent-workflows/implementation-plan.md
```

Expected Output:

The validator completes without formatting errors.


### Run staged policy validator

Command:

```shell
uv run python tools/validate_staged_agent_policies.py \
  --staging-root /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning \
  --manifest /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/manifest.json
```

Expected Output:

The validator reports a successful complete policy set. It exits non-zero with actionable evidence for a missing
manifest entry, stale workflow reference, Zen model in a work-project dispatch rule, missing principal ownership, or
unsafe promotion instruction.


### Inspect the local OpenCode schema

Command:

```shell
sqlite3 "$HOME/.local/share/opencode/opencode.db" ".schema session"
sqlite3 "$HOME/.local/share/opencode/opencode.db" ".schema message"
sqlite3 "$HOME/.local/share/opencode/opencode.db" ".schema part"
```

Expected Output:

The current schema is captured in the implementation journal and tests. The inspection is read-only and does not
create, lock for writing, or modify the database.


### Exercise the cost command manually

Command:

```shell
uv run dt opencode costs --since 2026-01-01 --format table
uv run dt opencode costs --format json > /tmp/opencode-costs.json
uv run dt opencode costs --format csv --file /tmp/opencode-costs.csv
```

Expected Output:

The first command prints a human-readable report. The second emits valid JSON to standard output. The third writes
valid CSV only after `/tmp` already exists. No command changes the SQLite source.


### Verify the staged policy tree

Command:

```shell
test -d /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning
diff -ru --exclude='implementation-plan.md' /Users/tucker.beck/src/dusktreader/dot/.agents \
  /var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning/.agents
git diff -- .agents
```

Expected Output:

The staged tree contains the complete intended policy replacement and the repository has no changes under `.agents`.
The final command must show no live policy edits during this implementation.


## Project Standards

- [`AGENTS.md`](../../AGENTS.md)
- [`dot.md`](../../.dot_agents/dot.md)
- [`pyproject.toml`](../../pyproject.toml)
- [`src/dot_tools/cli/main.py`](../../src/dot_tools/cli/main.py)
- [`tests/test_cli_main.py`](../../tests/test_cli_main.py)
- [`etc/install.yaml`](../../etc/install.yaml)
- [`~/.agents/instructions/markdown.md`](file:///Users/tucker.beck/.agents/instructions/markdown.md)
- [`~/.agents/instructions/editing.md`](file:///Users/tucker.beck/.agents/instructions/editing.md)
- [`~/.agents/instructions/python.md`](file:///Users/tucker.beck/.agents/instructions/python.md)


## Relevant Skills

- `execute-implementation-plan`
- `execute-implementation-task`
- `review-implementation-execution`
- `review-code`
- `review-implementation-plan`
- `investigate-codebase`
- `write-docs`


## Execution

### 01: Establish the cost-reporting boundary and capture the estimator

Define the cost-reporting module boundary and capture the exact local OpenCode schema and estimator source revision
before implementing calculations. Model the database adapter on `jot_down.tasks.store.Store`: a path-owning,
SQLite-backed store class with a connection lifecycle, `sqlite3.Row` row factory, context-manager support, typed row
conversion, and module-specific error translation. Keep the database adapter, normalized records, estimator,
filtering, aggregation, and renderers separable so each layer can be tested without a live database.


#### Acceptance Criteria

- AC01: The implementation identifies the database path resolution rule, current SQLite schema, relevant optional
  fields, and timestamp units in the journal.
- AC02: The selected `opencode-token-costs/estimate_opencode_costs.py` and `pricing.csv` source revision is pinned by
  immutable revision identifier and recorded with the implementation.
- AC03: The estimator adaptation preserves its pricing semantics and has a distinct provenance label from
  OpenCode-recorded cost.
- AC04: No implementation step writes to or migrates the OpenCode database.


#### Steps

1. Inspect the local OpenCode database using the documented SQLite commands and record the `session`, `message`, and
   `part` schemas, including the `session.cost`, token, `agent`, `model`, `directory`, `parent_id`, and timestamp
   columns.
2. Locate the selected estimator source and pricing data. Pin the source revision, preserve the required pricing data
   in a repository-owned module or data file, and record licensing or attribution requirements if present.
3. Resolve the database path to `$HOME/.local/share/opencode/opencode.db`. Do not add a database-path CLI option in
   this version because the approved command contract enumerates its options. Keep the default scoped to the local
   OpenCode database and do not contact external services.
4. Define typed internal records for raw sessions, normalized report rows, cost provenance, estimate status, and report
   metadata. Keep malformed optional values representable as visible status fields.
5. Add unit tests for schema mapping and estimator fixtures before implementing the remaining pipeline. Run the focused
   tests and confirm the new tests fail for the missing implementation.


#### Technical Notes

Use the observed database schema as a compatibility baseline, not as permission to assume it will remain fixed. Read
only through SQLite connections and avoid `CREATE`, `INSERT`, `UPDATE`, `DELETE`, pragmas that alter state, or implicit
write transactions. Treat absent optional columns and malformed JSON metadata as unavailable data with an actionable
status, unless the required identity or timestamp fields make the row unusable.

Confirm the module placement against the current package layout before Task 04. The existing package uses flat domain
modules alongside the `cli` package, so `src/dot_tools/opencode_costs.py` is the expected placement unless inspection
reveals a more specific established pattern.


### 02: Implement the read-only SQLite session loader

Create the database adapter that opens the selected path read-only, validates the minimum schema, loads session rows,
and exposes enough ancestry data to build root session trees. It must distinguish absent, locked, unreadable, and
malformed databases and must never mutate the source.


#### Acceptance Criteria

- AC01: A valid fixture database loads sessions with project directory, root ancestry, agent, model, dates, tokens,
  recorded cost, and optional metadata.
- AC02: Child sessions resolve to their root session identifier and retain their parent relationship.
- AC03: Missing, locked, unreadable, and malformed database cases exit non-zero through an actionable typed error that
  names the path and failure reason.
- AC04: A database containing missing optional columns or malformed optional metadata remains reportable with visible
  unavailable fields rather than invented zero values.
- AC05: Tests prove the loader performs no write operation and leaves the fixture database bytes unchanged.


#### Steps

1. Write failing fixture-based tests for valid sessions, parent chains, missing database, malformed SQLite file, and
   unavailable optional fields.
2. Implement an `OpenCodeSessionStore` using the structural pattern in `jot_down.tasks.store.Store`: retain the
   database path, open a connection in its initializer, set `sqlite3.Row`, provide `close`, `__enter__`, and `__exit__`,
   and centralize row conversion. Open with SQLite URI read-only mode and an explicit short timeout. Convert operating
   system and SQLite exceptions into module-specific actionable errors without leaking SQL internals unnecessarily.
3. Validate required tables and columns before querying. Build queries from the validated schema so supported schema
   evolution can omit optional columns safely.
4. Load sessions using parameterized SQL. Parse timestamps consistently and retain raw values needed for diagnostics.
5. Resolve ancestry in memory with cycle and missing-parent protection. Mark broken ancestry as a report status instead
   of looping or silently assigning an incorrect root.
6. Run the focused loader tests, then inspect fixture hashes before and after command execution.


### 03: Implement normalization, filtering, metrics, and outlier detection

Build the reporting view over loaded sessions. Apply all requested filters, calculate token totals and cache ratio,
separate recorded and estimated costs, and identify outliers against the selected population without treating an
unsupported estimate as zero.


#### Acceptance Criteria

- AC01: `--since` and `--until` filter by the documented date semantics and reject invalid or contradictory values with
  an actionable CLI error.
- AC02: `--directory`, `--agent`, and `--model` filter exact normalized report dimensions without changing source data.
- AC03: Token totals include input, output, reasoning, cache-read, and cache-write values according to the observed
  schema, with missing values visible as unavailable where they cannot be safely inferred.
- AC04: Cache ratio uses the documented denominator and reports an explicit unavailable status when the denominator is
  zero or required values are missing.
- AC05: Recorded OpenCode cost and local estimate are separate fields with separate totals and provenance labels.
- AC06: Unsupported models, incomplete token data, estimator limitations, and missing pricing remain visible and are not
  converted to zero-dollar estimates.
- AC07: Outlier indicators are calculated against the filtered population, have deterministic behavior for empty and
  one-row populations, and identify the metric and threshold used.
- AC08: An empty filtered population returns a successful, clearly labeled empty report rather than an exception.


#### Steps

1. Write failing unit tests for every filter, token aggregation, cache-ratio boundary, estimator status, and outlier
   population case.
2. Implement date parsing and normalization in one place. Use timezone-aware handling for database timestamps and
   document whether CLI dates are inclusive.
3. Implement exact-match filters over normalized fields. Apply filters before calculating population totals and
   outlier thresholds.
4. Implement the estimator adapter against the pinned source semantics. Preserve estimate version, model match status,
   and unsupported/incomplete reasons on each row.
5. Implement cache ratio and token metrics with explicit zero and missing-value handling.
6. Implement deterministic outlier detection using a documented robust rule or threshold derived from the selected
   population. Include the indicator and supporting value in the normalized output.
7. Run the focused tests and confirm all calculations are covered without requiring the live database.


### 04: Add report serialization and the `dt opencode costs` CLI

Add an `opencode` Typer command group and register a `costs` subcommand in `src/dot_tools/cli/main.py`. Render the same
normalized report model as table, JSON, or CSV, with standard output by default and safe file output when the parent
directory already exists.


#### Acceptance Criteria

- AC01: `dt opencode costs --help` documents `--since`, `--until`, `--directory`, `--agent`, `--model`, `--format`, and
  `--file`, with table as the default format.
- AC02: Table output clearly labels recorded cost, local estimate, provenance, tokens, cache ratio, project directory,
  root session tree, agent, model, date, and outlier indicators.
- AC03: JSON output is valid machine-readable data containing report metadata, filters, totals, provenance, and rows.
- AC04: CSV output has stable headers and one row per normalized session/report dimension with estimate status visible.
- AC05: Standard output is used when `--file` is absent; `--file` writes only when its parent directory exists and
  reports an actionable error otherwise.
- AC06: Database and validation errors return non-zero without tracebacks in normal CLI use, identify the relevant path
  or option, and do not create or modify the source database.
- AC07: CLI tests exercise valid reports, each format, every filter, empty results, invalid options, missing output
  parent, and database failure paths.


#### Steps

1. Write failing `CliRunner` tests in `tests/test_cli_opencode_costs.py` for help, default table output, JSON, CSV,
   filters, `--file`, empty results, and failures. Add or extend `tests/test_cli_main.py` only for top-level command
   registration if that is the established test boundary.
2. Create `src/dot_tools/cli/opencode.py` with a Typer group and `costs` command. Keep command parsing and exit
   behavior in the CLI layer; delegate loading and reporting to the cost modules.
3. Register the group with `cli.add_typer(opencode_cli, name="opencode")` in `src/dot_tools/cli/main.py`.
4. Implement table, JSON, and CSV renderers over the same report object. Do not duplicate calculation logic per format.
5. Validate the output path before opening it. Refuse to create parent directories and write through a temporary file
   only if needed to avoid partial output on renderer failure.
6. Implement user-facing error handling consistent with existing `typerdrive` wrappers. Keep diagnostic detail in the
   message while avoiding a traceback for expected local-data failures.
7. Run the focused CLI tests, then exercise the command against a copied fixture database and the real database in
   read-only mode.


#### Technical Notes

Prefer a new `src/dot_tools/opencode_costs.py` (or equivalent domain module) plus `src/dot_tools/cli/opencode.py` over
placing database and pricing logic in `cli/main.py`. Follow existing Typer registration patterns in `main.py` and
existing test conventions in `tests/test_cli_main.py`.


### 05: Build the staged global policy replacement

Create the complete policy replacement in the required temporary staging area. Do not edit `.agents`, `~/.agents`,
`.config/opencode/agents`, or any other live policy path while executing this task.


#### Acceptance Criteria

- AC01: The staging root is exactly
  `/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning` and contains a complete `.agents`
  replacement tree rather than a partial patch.
- AC02: `run-feature` is the sole full-feature workflow name, all former `run-implementation` references are migrated,
  and the retired name is not presented as an available alternative.
- AC03: The staged `run-feature`, `run-task`, and `run-hack` policies satisfy design plan AC01 (feature workflow), AC02
  (task controls), AC03 (hack authority), and AC04 (evidence-led escalation), including gates, Git authority, final QA
  ownership, and escalation signals.
- AC04: Staged principal, executor, investigator, planner, reviewer, workflow, and review policies assign risk and model
  decisions to the principal and enforce the work-project versus personal-project model menus.
- AC05: Staged verification and review policies enforce focused implementation checks, one final QA pass, diff-first
  findings-focused review, and criterion-changing re-review only.
- AC06: Staged promotion guidance requires complete-set validation, explicit approval, atomic promotion, rollback on
  failure, and OpenCode restart.
- AC07: No live or tracked `.agents` file changes occur during implementation; the staged tree and manifest are the only
  policy outputs.


#### Steps

1. Create the staging root and copy the current policy source into a staging-only `.agents` tree. Preserve file modes,
   symlink intent, and relative paths. Do not use a command that writes through the `~/.agents` symlink.
2. Inventory every policy file under `.agents/agents`, `.agents/skills`, and `.agents/instructions` that participates in
   workflow dispatch, review, execution, planning, model selection, or promotion. Include the inventory in a staged
   manifest with source path, staged path, and intended disposition.
3. Rename or create staged workflow documents for `run-feature`, `run-task`, and `run-hack`. Update orchestrator,
   sub-skill, agent, and cross-reference text as a graph migration, not a directory-only rename. Keep `run-hack` direct
   on the current branch with no Git lifecycle or agent worktree.
4. Add the worktree lifecycle guidance described in Task 06 to the staged feature and task workflows and every policy
   that dispatches or reviews them. Ensure the guidance is explicit before any artifact or code creation, not merely an
   integration note.
5. Update staged principal and specialist policies so specialists report facts and evidence, while the principal owns
   risk classification, model selection, escalation, and human gates. Encode the exact provider/model menus from AC09.
6. Update staged execution and review skills to implement focused verification, one final QA owner, diff-first review,
   compact findings, and criterion-changing re-review rules.
7. Add or update staged promotion instructions that explicitly prohibit live edits during staging and require a complete
   staged-set diff, independent review, explicit approval, atomic replacement, rollback, and restart.
8. Search the staged tree for stale `run-implementation` references, contradictory human-gate language, prohibited Zen
   model use in work dispatches, and instructions that edit live policy files before approval. Resolve every hit or list
   an intentional historical reference in the manifest.
9. Generate a staged file checksum manifest and a human-readable recursive diff against the current policy source.
10. Run staged policy validation and review commands from Tasks 10 and 12. Confirm `git diff -- .agents` remains empty.


#### Technical Notes

The repository currently symlinks `~/.agents` to this checkout's `.agents`, so editing either path edits tracked live
policy. Treat the temporary staging root as disposable and outside the repository. Do not add the staged tree to the
repository as part of this implementation. Promotion is a separate operation after explicit human approval and must
copy the full approved set atomically, then restart OpenCode.

The validator is `tools/validate_staged_agent_policies.py`. It accepts `--staging-root` and `--manifest`, reads only
within that root, and returns one actionable failure per violation. It validates the manifest's complete file inventory;
rejects active `run-implementation` references except listed historical references; rejects `opencode/` model IDs in
the staged work-project dispatch policy; requires text assigning risk classification and escalation to the principal;
and rejects instructions that permit edits to live policy paths before explicit approval or omit atomic promotion,
rollback, and restart requirements. Extend it with worktree lifecycle assertions and fixture tests as specified in Task
07. Fixture tests exercise each rule with a minimal staged tree.

Staged OpenCode variants are the complete model-specific specialist definitions under
`.config/opencode/agents`. They contain seven specialist roles in each approved dispatch context: work GPT variants,
work Claude variants, and personal variants. Each variant has fixed model frontmatter and refers to one canonical
`.agents/agents` role description. The staged principal agent is the sole human-facing agent and is not a variant.


### 06: Stage the approved worktree-enabled feature and task guidance

Amend the existing staged `run-feature` and `run-task` guidance to make isolation, gates, integration, and cleanup
observable and enforceable. Preserve the completed cost command, existing staged files, manifest, and promotion handoff;
change only the staged policy copies needed to implement this design.


#### Acceptance Criteria

- AC01: Before creating any artifact or changing code, `run-feature` and `run-task` record the current parent worktree,
  parent branch, and parent base, then create an agent worktree and agent branch from that parent state.
- AC02: All feature and task artifacts and code are created inside the agent worktree. Every subsequent human gate
  reports the agent worktree path and agent branch. The original human worktree remains the integration authority.
- AC03: Feature and task integration stop for stale-parent detection immediately before exclusive squash integration. A
  changed parent stops the run and presents the human with an explicit decision. The policy never silently
  rebases, merges, discards, overwrites, or changes human work.
- AC04: Successful integration removes the agent worktree but preserves the local agent branch for audit. Declined or
  abandoned runs preserve both worktree and branch until the human explicitly removes them.
- AC05: `run-hack` remains direct on the current branch, creates no worktree or branch, and performs no Git lifecycle.
- AC06: Feature and task worktree, gate, integration, and cleanup guidance contains no model-selection language. It
  consumes the shared principal model-selection policy without redefining a model menu or project-class rule.


#### Steps

1. Inspect the staged OpenCode variant layout and identify every `run-feature` and `run-task` document, orchestrator,
   sub-skill, principal, executor, and review instruction that can create artifacts, change code, gate execution, or
   integrate and clean up a run.
2. Amend the staged workflow entry points to establish the agent worktree and branch before plan artifacts, journals,
   design artifacts, implementation artifacts, or code are created. Record the parent branch and immutable base used for
   creation, and keep the human in the original worktree.
3. Amend artifact and execution guidance so all agent-produced artifacts and code are written in the agent worktree. Add
   the worktree path, agent branch, parent branch, and recorded base to every gate prompt and handoff that follows
   creation.
4. Specify exclusive squash integration into the ready-to-PR parent branch only after final QA, independent review, and
   explicit human approval. Require a parent worktree/branch/base comparison immediately before squash integration.
5. Specify the stale-parent stop state and human decision boundary. If regeneration is approved, discard the agent
   worktree and local audit branch only as an explicit operation. Restart from the updated parent and record it.
6. Specify cleanup by outcome: remove only the agent worktree after a successful squash. Preserve the local branch for
   audit. Preserve both worktree and branch after decline or abandonment until the human explicitly removes them.
7. Keep hack guidance direct and Git-free. Update principal guidance to choose workflow, model, escalation, and risk
   classification from objective evidence and project class, including all staged OpenCode variants.
8. Regenerate only the staged manifest, checksums, and recursive diff after policy edits. Do not edit tracked `.agents`,
   `~/.agents`, source files, or the completed cost implementation.


#### Technical Notes

Distinguish the parent worktree from the agent worktree and the agent branch from the parent branch. “Create a branch”
without naming the worktree is insufficient. The agent workspace must exist before any artifact is emitted.

Use “exclusive squash integration” consistently. The workflow may not push or create a pull request. Preserve the local
agent branch after successful integration for audit, and make cleanup after decline or abandonment human-owned.


### 07: Stage the isolated run-bug-fix lifecycle and specialist dispatch

Add `run-bug-fix` to the staged branch-based workflow contract. Preserve investigation, bug-report creation, approved
implementation planning, one final QA pass, independent review, explicit review approval, and exclusive squash
integration. Apply the shared worktree, stale-parent, cleanup, and model-variant rules without changing the completed
cost implementation or live policy tree.


#### Acceptance Criteria

- AC01: The staged workflow records parent worktree, parent branch, and immutable parent base, then creates the agent
  worktree and branch before investigation or any bug-report artifact.
- AC02: The bug report, implementation plan, journal, code, QA corrections, and review context are created in the agent
  worktree, and every later gate identifies the agent worktree path and branch.
- AC03: Investigator, planner, executor, QA-fix, and reviewer dispatches select fixed model-specific specialist variants
  from the approved project-class menu and record the exact variant in the journal or review context.
- AC04: Final QA occurs once before review, review approval remains human-gated, and integration uses only exclusive
  squash into the ready-to-PR parent branch without push or pull-request creation.
- AC05: Parent drift before squash stops the run and offers only an explicit human reconciliation decision. The policy
  never silently rebases, merges, discards, overwrites, or changes human work.
- AC06: Successful squash removes only the agent worktree and preserves the agent branch for audit. Decline or
  abandonment preserves both until explicit human cleanup.


#### Steps

1. Add failing staged-policy fixtures for missing pre-investigation worktree creation, misplaced bug artifacts, gates
   without identity, generic specialist dispatch, missing variant recording, non-exclusive integration, stale-parent
   mutation, and incorrect success or decline cleanup.
2. Update staged `run-bug-fix` entry points, orchestration guidance, and dispatch instructions to establish and record
   the isolated workspace before investigation. Include the parent base and identity in every handoff.
3. Add the bug-report-to-implementation-plan artifact attachment and approval sequence. Keep all artifacts in the agent
   worktree and retain the implementation journal as the dispatch-recording location.
4. Add model-specific variant selection for each applicable handoff and require the reviewer context to record the
   selected reviewer variant, project class, and model ID.
5. Add exclusive squash, stale-parent reconciliation, and outcome-specific cleanup language. State that reconciliation
   may discard the agent worktree and audit branch only after explicit human approval and must restart from the updated
   parent.
6. Run the focused validator fixtures and confirm the complete staged tree passes without modifying source, staged
   files outside the intended staging root, or tracked `.agents`.


#### Technical Notes

Use the same lifecycle vocabulary as `run-feature` and `run-task`. The bug report is an investigation artifact, not a
permission to bypass the implementation-plan approval gate. QA-fix is a constrained executor handoff, not a second QA
owner.


### 08: Stage the attached run-fix lifecycle and specialist dispatch

Add `run-fix` as a branch-based follow-up workflow that reads the existing implementation project's context and places
new fix artifacts at that project's established path inside the agent worktree. Preserve scoped-fix approvals,
independent review, stale-parent reconciliation, auditable cleanup, and the shared model-specific dispatch policy.


#### Acceptance Criteria

- AC01: The workflow records the current parent worktree, parent branch, and parent base, then creates the agent
  worktree and branch before reading or writing fix artifacts or changing code.
- AC02: The workflow locates the existing implementation project and attaches its bug report, fix plan, journal updates,
  and review evidence at the established project path in the agent worktree. It never creates or modifies fix artifacts
  in the human worktree.
- AC02b: When the existing implementation project cannot be located, its artifact directory is ambiguous, or the
  expected agent-worktree project path cannot be established, the workflow stops and reports the specific resolution
  failure to the human without creating or modifying any artifact or code.
- AC03: Investigator, planner, executor, QA-fix, and reviewer handoffs use model-specific variants selected from the
  approved work or personal menu, and record exact variant, provider/model ID, and handoff purpose in the journal or
  review context.
- AC04: Every gate identifies the agent worktree and branch. Final QA, independent review, explicit approval, and
  exclusive squash integration remain required for the scoped fix.
- AC05: Stale parent state stops integration. Reconciliation requires an explicit human decision and cannot silently
  rebase, merge, discard, overwrite, or alter human work.
- AC06: Successful integration removes the agent worktree but retains its branch. Declined or abandoned runs retain both
  until the human explicitly requests cleanup.


#### Steps

1. Write failing fixtures for missing project-context lookup, fix artifacts written outside the agent worktree, wrong
   project-path attachment, generic dispatch, absent variant recording, stale-parent handling, and each cleanup outcome.
2. Update staged `run-fix` workflow and its orchestrator to capture the parent identity and create the agent worktree
   before attaching to the existing implementation project.
3. Define the artifact attachment rule using the existing project's established artifact directory and preserve the
   parent project's context in the agent journal. Reject ambiguous or missing project context rather than guessing.
4. Add variant-specific investigator, planner, executor, QA-fix, and reviewer handoffs with exact recording
   requirements.
5. Add gate identity, final QA, independent review, explicit approval, exclusive squash, stale-parent stop, and cleanup
   instructions. Make human cleanup the only cleanup path for decline or abandonment.
6. Run the run-fix fixtures and complete staged validator. Confirm no source, live, or tracked policy file changes.


#### Technical Notes

The existing implementation project is the attachment authority, but the current human worktree is not. Resolve its
path from the agent-worktree view of the project and fail closed when the expected artifact path cannot be established.


### 09: Stage the isolated run-hotfix lifecycle and preserved gate model

Add isolation to `run-hotfix` without turning it into `run-task`. Preserve its brief investigation, principal-authored
minimal plan, direct execution, single lightweight review, and existing approval thresholds. The agent worktree and
branch are the only lifecycle additions.


#### Acceptance Criteria

- AC01: The workflow records parent worktree, parent branch, and parent base, then creates the agent worktree and branch
  before investigation, the minimal plan, or code changes.
- AC02: Investigation notes, principal-authored minimal plan, code, QA-fix changes, and lightweight review context stay
  in the agent worktree, and each existing hotfix gate identifies the agent path and branch.
- AC03: Investigator, executor, QA-fix, and reviewer handoffs use model-specific variants from the approved
  project-class menu and record the exact variant in the hotfix journal or review context. No specialist planner
  dispatch is added.
- AC04: The hotfix retains its current streamlined approval thresholds and does not gain a task-style plan approval,
  independent review, or extra human gate solely because isolation was added.
- AC05: Before squash, stale-parent detection stops the run and requires an explicit human reconciliation decision. No
  silent rebase, merge, discard, overwrite, or human-work mutation is permitted.
- AC06: Successful squash removes the agent worktree and preserves the agent branch. Declined or abandoned hotfixes
  preserve both until explicit human cleanup.


#### Steps

1. Write failing hotfix fixtures for pre-artifact worktree creation, gate identity, accidental task-style gates,
   generic dispatch, missing variant recording, stale-parent behavior, and cleanup outcomes.
2. Update staged `run-hotfix` guidance to establish the isolated workspace first while retaining the principal-authored
   minimal plan and existing approval thresholds.
3. Add model-specific investigator, executor, QA-fix, and reviewer dispatch instructions and record each selected
   variant. Explicitly prohibit adding a planner handoff unless the principal changes workflow class.
4. Add exclusive squash, stale-parent reconciliation, and outcome-specific cleanup language shared with other
   branch-based workflows.
5. Run hotfix fixtures, the full staged validator, and a targeted search proving no task-style approval or review gate
   was introduced. Confirm tracked `.agents` remains unchanged.


#### Technical Notes

Urgency changes the approval threshold, not the safety boundary. The hotfix gate model remains the approved streamlined
flow: brief investigation, principal-authored minimal plan, direct execution, one lightweight review, and existing
approval thresholds.


### 10: Validate the staged worktree lifecycle and policy graph

Extend the existing staged-policy validator and fixture suite so the new workflow contract cannot regress. Preserve the
completed cost and staging validation.


#### Acceptance Criteria

- AC01: Validator failures identify missing pre-artifact worktree creation, missing artifact placement, missing gate
  identity, non-exclusive integration, stale-parent handling, unsafe silent mutation, or incorrect cleanup behavior.
- AC02: Validator tests cover feature, task, hack, stale-parent, successful-cleanup, declined-run, and abandoned-run
  lifecycle fixtures. Separate model-policy fixtures cover every staged OpenCode variant and its fixed dispatch context.
- AC03: The complete staged tree passes validation with no stale `run-implementation` references, no work-project Zen
  dispatch, and explicit principal ownership of risk, escalation, model, and human-gate decisions.
- AC04: Validation reads only the staging root and manifest, does not modify source or staged policy files, and confirms
  tracked `.agents` remains unchanged.


#### Steps

1. Write failing validator fixtures for each lifecycle invariant, including an artifact before worktree creation, a gate
   without path/branch identity, a merge or rebase instruction, silent stale-parent handling, automatic cleanup after
   decline, and cleanup that deletes the audit branch after success.
2. Extend `tools/validate_staged_agent_policies.py` with path-scoped checks for the three workflows and principal/model
   policy checks across every staged OpenCode variant.
3. Run the fixture suite and confirm actionable failures, then validate the complete staged tree with the canonical
   command. Compare tracked `.agents` checksums before and after validation. Separately confirm that validation leaves
   the staged tree and unrelated source files unchanged.
4. Record validator results, staged OpenCode variants, lifecycle coverage, and unresolved human choices in the journal
   without modifying the completed cost-command files.


### 11: Add policy and promotion validation fixtures

Create automated checks that validate the staged policy set without importing or activating it. Keep these checks
outside production runtime code and make them runnable against any staging root so the later promotion can reuse them.


#### Acceptance Criteria

- AC01: Validation fails when a staged workflow reference points to a missing file or stale retired workflow.
- AC02: Validation detects duplicate or missing policy files relative to the staged manifest.
- AC03: Validation detects work-project dispatches using a Zen model and detects missing principal ownership of risk or
  escalation decisions.
- AC04: Validation detects policy text that permits live edits before explicit approval or omits atomic promotion and
  restart requirements.
- AC05: Validation passes for the complete staged tree and does not modify any source or live policy file.


#### Steps

1. Write failing tests for staged policy inventory, stale-reference checks, model-menu checks, promotion-safety checks,
   and no-live-edit behavior.
2. Implement a small validation script or test helper under the repository's test/tooling area that accepts the staging
   root and manifest paths as arguments. Keep path handling explicit and reject paths outside the requested staging
   root for write operations.
3. Run the validator against intentionally broken temporary fixtures and assert actionable failures.
4. Run it against the real staged tree and assert success. Compare tracked `.agents` checksums before and after.
5. Document the exact validator command in the staged manifest and implementation journal.


### 12: Run independent review of code and staged policy

Complete verification for the Python implementation and perform a separate diff-first review of the staged policy
replacement. Resolve findings before presenting the implementation, but do not promote the policy set.


#### Acceptance Criteria

- AC01: Ruff, type checking, focused tests, and the full pytest suite pass.
- AC02: Cost-report tests cover every design acceptance criterion, including malformed and unavailable local data,
  estimator provenance, read-only behavior, and all output formats.
- AC03: The staged policy tree passes its validator and contains no unexplained stale references or contradictions.
- AC04: A review records file-level findings and confirms the live `.agents` tree is unchanged.
- AC05: Any unresolved finding that requires a human choice is recorded as an explicit unknown and blocks promotion, not
  silently resolved by implementation.


#### Steps

1. Run `uv run ruff check src tests`, `uv run ty check`, and `uv run pytest`.
2. Run the staged policy validator and the recursive staged diff/checksum commands.
3. Review the Python diff first, then expand into surrounding code only for specific concerns. Check external-call
   error handling, type safety, public-function tests, input validation, and source-database immutability.
4. Review the staged policy diff first, then inspect referenced policies only as needed. Verify all design acceptance
   criteria and the complete-set promotion contract.
5. Record findings and outcomes in the implementation journal or the repository's appropriate review artifact. Re-run
   relevant checks after every material correction.
6. Finish with a status report that names the staged root, estimator revision, validation commands, test results, and
   explicit confirmation that no live policy promotion occurred.


### 13: Preserve the human-gated promotion handoff

Prepare the exact later promotion procedure without executing it. The handoff must let a human approve or reject the
complete staged policy set independently from the cost-command implementation.


#### Acceptance Criteria

- AC01: The handoff identifies the staged root, source manifest, checksum manifest, recursive diff, validator output,
  and review artifact.
- AC02: The handoff states that promotion requires explicit human approval and that no approval is inferred from test
  success or artifact completion.
- AC03: The procedure describes atomic replacement, preservation or restoration of the prior complete live set on
  failure, verification after replacement, and OpenCode restart.
- AC04: This task performs no copy, rename, symlink replacement, commit, or restart affecting live `~/.agents`.


#### Steps

1. Write the handoff instructions into the staged manifest or implementation journal, including the exact approval
   checkpoint and the expected promotion target.
2. Include a pre-promotion command that verifies the staged tree and current live tree are distinct paths and that the
   live tree has not changed unexpectedly.
3. Specify an atomic promotion mechanism appropriate to the symlinked repository layout, with a backup and rollback
   path. Require validation of the promoted complete set before restarting OpenCode.
4. Do not run the promotion procedure. End implementation with the staged tree available for explicit later review.


## Unknowns

- Confirm the exact immutable revision and licensing requirements for Eric Butler's estimator source before copying or
  adapting its logic. Resolve this during Task 01 and record the outcome in the implementation journal.
- Confirm whether the installed OpenCode version exposes additional session-cost fields that should be preserved as
  optional dimensions. Resolve this from the schema inspection in Task 01; do not expand the command contract without
  evidence.
- Confirm the outlier rule and threshold during implementation using the design's requirement for selected-population
  indicators. Resolve it in the report contract and tests before Task 03 is marked complete.
- Confirm the exact Git worktree naming, parent-base recording, stale-parent comparison, and explicit regeneration
  command sequence supported by the staged OpenCode variants. Resolve it during Tasks 06–10 and record the result in the
  journal without permitting silent rebase, merge, discard, overwrite, or cleanup on decline or abandonment.


## Technical Notes

### Proposed file layout

Keep domain logic separate from CLI wiring. The likely implementation layout is:

- `src/dot_tools/cli/opencode.py`: Typer group and `costs` command
- `src/dot_tools/opencode_costs.py`: `OpenCodeSessionStore` following the `jot_down.tasks.store.Store` lifecycle
  pattern, plus normalized records, filters, metrics, estimator integration, and report model
- `tests/test_opencode_costs.py`: loader, estimator, filters, metrics, and renderer tests
- `tests/test_cli_opencode_costs.py`: `CliRunner` command and exit/output tests
- `tests/fixtures/opencode/`: small SQLite databases and estimator fixtures, if the existing fixture conventions permit

Adjust names only if repository inspection or established package conventions require it. Update `pyproject.toml` only
if the selected estimator requires a new dependency; prefer the standard library and vendored pricing data to avoid
network access or runtime dependency drift.


### Cost and provenance contract

Every report row and total must make these values distinguishable:

- OpenCode-recorded cost, copied from the session record when present
- Local estimate, calculated by the pinned estimator when model and token data support it
- Estimate status, including unsupported model, missing pricing, incomplete tokens, and estimator limitations
- Estimator source and revision metadata
- Token totals and cache ratio
- Project directory, root session tree, agent, model, date, and outlier indicator

Never add recorded and estimated costs into one unlabeled total. If a combined convenience total is provided, label it
as a derived value and preserve both source totals beside it.


### SQLite store convention

Follow the established `jot_down.tasks.store.Store` pattern for the local SQLite boundary rather than using free
connection helpers. `OpenCodeSessionStore` owns a `Path` and a connection, uses `sqlite3.Row`, implements `close`,
`__enter__`, and `__exit__`, and converts rows in one dedicated method. Unlike the writable jot-down store, it opens
only SQLite URI read-only connections, performs no schema creation or migration, and exposes only read operations.
Expected database failures are translated at this boundary into actionable domain errors for the CLI.


### Promotion safety contract

The live policy path is `/Users/tucker.beck/.agents`, which resolves to the repository's tracked `.agents` directory.
During implementation, all policy edits occur only below
`/var/folders/qm/_x9k_d454n56v96tbqs10wr40000gp/T/opencode/agent-workflow-tuning`. The executor must verify
`git diff -- .agents` is empty before and after staging. A later human-approved promotion must replace the complete
tracked policy set atomically, retain a rollback copy, validate the promoted set, and restart OpenCode. Test success
never counts as promotion approval.


### Completion evidence

The implementation journal must list every modified repository file, every staged policy file and checksum manifest,
the pinned estimator revision, schema observations, exact commands and outputs, all test fixtures, review findings, and
the explicit statement that live policy promotion was not performed.
