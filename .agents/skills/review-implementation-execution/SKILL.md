---
name: review-implementation-execution
description: Reviews implementation execution (code changes) against a plan for quality, coverage, and plan alignment.
---

# Review Implementation Execution Skill

Read the implementation journal, inspect the modified files recorded in it, and run verification commands.


## When to use

Use this skill to review code changes *against an implementation plan and journal* — verifying
AC coverage, plan alignment, scope creep, and code quality.

This skill is a sub-skill called by orchestrators:
- `run-implementation` — after stage 3 (execute) produces an implementation journal
- `run-bug-fix` — after the fix is executed
- `run-fix` — after the scoped fix is executed

Do not confuse with `review-code`, which reviews files against quality standards without a
plan or journal. Use `review-implementation-execution` when a plan exists to verify against —
use `review-code` when there is no plan.


## Prerequisites

Your prompt must include:

- Path to the implementation journal
- Scope: `task-NN` (e.g. `task-03`) or `whole-plan`
- Iteration number (1 for first review, 2+ for re-reviews)
- For re-reviews: path to the prior review artifact

If any of these are missing, ask before proceeding. Do not guess.


## Artifact

Write the review to `execution-review--{scope-id}--{N}.md` in the same directory as the journal. Read
`.agents/artifacts/execution-review/description.md` for the canonical section definitions, and render
`.agents/artifacts/execution-review/template.md.j2` to produce the initial file. Replace all dummy
content — every line drawn from the retro encabulator — with real content for this review. The rendered
file must contain no placeholder text when submitted. Supply the path to your caller on completion.


## Scope

- Review code only. Do not modify the journal, the plan, or any source files.
- **task-NN**: review only the files recorded in the specified task's journal entry.
- **whole-plan**: review all files recorded across all task entries in the journal.
- **re-review**: verify every prior finding is resolved, then check for new issues introduced by fixes.
- Do not comment on code outside the reviewed files except to provide context for a finding within them.


## Process


### 1. Read context

Read the implementation journal. From it, locate and read the implementation plan referenced in the journal's
`## Source plan` section. If `Project Commands` or `Project Standards` is missing from the plan, report a
Critical finding and stop.

Locate and read the design plan referenced by the implementation plan for higher-level context.


### 2. Resolve prior findings (re-review only)

Walk through every finding from the prior review artifact. For each, mark:

- ✓ Fully resolved — cite `file:line` evidence
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — this is a Critical finding in the current review


### 3. Identify files under review

From the journal's `## Files modified` section(s), collect the list of files changed for the scope being
reviewed. Read each file directly. Do not rely solely on the journal's description of what changed.


### 4. Run verification commands

Consult the project's working guides or the plan's `Project Commands` section to find the
correct commands for running all quality checks. Run all of them: type checker, linter, and
tests.

Do not invent commands not documented in the project. If no coverage command is documented,
record `skipped (no project-documented command)` in the verification evidence.

If any quality check fails (type errors, lint errors, test failures): stop, write the review
artifact noting the full failure output, and return "Quality checks failing. Fix before
review." Do not continue the review past this point.


### 4. Verify acceptance criteria

Read the task's `Acceptance Criteria` section from the plan. Cross-reference with the implementor's AC
validation in the journal, but verify each AC independently against the actual code.

For each AC:

- Mark ✓ Fully satisfied / ⚠ Partially satisfied / ✗ Not satisfied
- Cite `file:line` evidence and the test name that exercises it

A Critical finding for any of:
- An AC marked ✗
- An AC with no test that exercises it
- A task with no Acceptance Criteria section — stop and escalate to the orchestrator


### 5. Check for scope creep

For each file listed in the journal as modified, identify which plan task justifies the change. Unjustified
changes to unrelated subsystems, security-sensitive code, or public APIs are Critical findings. Other
unjustified changes are Significant findings.


### 6. Review code and test quality

Enforce these quality gates:

| Standard                                                           | Severity      |
| ------------------------------------------------------------------ | ------------- |
| Error handling on all external calls (network, fs, db, process)    | Critical      |
| No type-safety violations without a justification comment          | Critical      |
| No swallowed exceptions or ignored return values                   | Critical      |
| New public functions have tests                                    | Critical      |
| Tests verify behavior, not mock interactions                       | Critical      |
| No test-only hooks or helpers in production files                  | Critical      |
| No input validation gaps or injection vectors                      | Critical      |
| Null/undefined inputs handled where applicable                     | Significant   |
| Edge cases (empty, boundary, max) covered                          | Significant   |
| New code paths covered by tests (when coverage tool available)     | Significant   |
| Logic not placed in wiring/bootstrap files without justification   | Significant   |
| No unused imports, functions, or branches                          | Trivial       |


### 7. Write the review artifact

Fill in all sections of the template. Store the artifact as described in `## Artifact`.
