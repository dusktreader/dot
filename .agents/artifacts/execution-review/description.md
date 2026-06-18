# Execution Review

A structured review of code produced by executing an implementation plan. Verifies that the
implementation satisfies the plan's acceptance criteria, stays within scope, and meets code
quality standards. Produced by a reviewer agent.


## Template Variables

| Variable  | Description                                        |
| --------- | -------------------------------------------------- |
| `title`   | Title of the implementation plan being reviewed    |


## Sections


### Source Artifacts

Paths to:
- The implementation journal being reviewed
- The implementation plan the journal references (located via the journal's Source Plan field)


### Scope

The scope of this review run: `task-NN` (a single task), `whole-plan` (all tasks), or
`re-review` (re-checking after fixes). Followed by the iteration number.


### Issue Summary

A count of findings at each severity level: Critical, Significant, Trivial.


### Verification Evidence

Output of all quality gate commands: tests, build, linter, and coverage. Each line records
the command run and its result. If a command is not documented in the project, record
`skipped (no project-documented command)`.


### Acceptance Criteria Verification

A table with one row per AC in scope. Columns: AC ID, Status (✓ / ⚠ / ✗), Evidence
(`file:line` reference and/or test name that exercises the AC).

For `task-NN` scope: one row per AC in that task.
For `whole-plan` scope: rows grouped by task.
Omit for re-reviews if AC status is unchanged from the prior review.


### Scope Verification

A table with one row per file listed in the journal as modified. Columns: File path,
Justification (which plan task and step justify the change), Status (✓ / ⚠ / ✗).

Unjustified changes to unrelated subsystems, security-sensitive code, or public APIs are
Critical findings. Other unjustified changes are Significant findings.


### Prior Review Resolution

Present only for re-reviews. For each finding from the prior review, records whether it was
resolved (✓), partially resolved (⚠), or not resolved (✗), with `file:line` evidence or
an explanation. Omit entirely for the first review.


### Findings

Same structure as design-review and implementation-review findings sections, with one
difference: the field for suggested fix is named **Fix** (a specific action needed) rather
than **Suggestion**.

Finding IDs: `C##` Critical, `S##` Significant, `T##` Trivial.

The Summary table Outcome column is filled in by the orchestrator after discussing findings
with the human.


### Skills Applied

A list of skills loaded during the review, noting whether each was project-local or a global
fallback.


### Decision

`APPROVED` or `BLOCKED — CHANGES REQUIRED`.

If blocked: list the finding IDs that must be resolved before re-review.
If approved: confirm that all quality gates passed and all ACs are satisfied.
