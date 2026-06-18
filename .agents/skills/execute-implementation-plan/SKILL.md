---
name: execute-implementation-plan
description: Instructions for executing implementation plans. Use when specifically requested.
---

# Execute Implementation Plan Skill

Read the provided implementation plan artifact and execute every task in it to completion.
Record progress in an implementation journal.


## When to use

Use this skill to execute an approved implementation plan end-to-end. It is the execution
stage in multiple orchestrator workflows.

This skill is a sub-skill called by orchestrators:
- `run-implementation` — stage 3 (execute)
- `run-bug-fix` — execute stage
- `run-fix` — execute stage
- `run-hotfix` — execute stage

Do not confuse with `execute-implementation-task`, which executes a single named task rather
than the full plan. Use this skill when the full plan must be completed in one pass.


## Prerequisites

Your prompt must include:

- Path to the implementation plan

If not provided, ask before proceeding. Do not guess.


## Artifact

Write the journal to `{project-dir}/implementation-journal.md`, where `{project-dir}` is the
directory containing the implementation plan. Read `.agents/artifacts/implementation-journal/description.md`
for the canonical section definitions, and render `.agents/artifacts/implementation-journal/template.md.j2`
to produce the initial file. Replace all dummy content — every line drawn from the retro encabulator —
with real content for this project. The rendered file must contain no placeholder text when submitted.
Supply the path to your caller on completion.


## Scope

The work is complete only when **every task in the plan** has been executed and all acceptance
criteria are met. Do not stop partway through the plan to report progress. Do not stop because
a batch of tasks feels like a natural checkpoint. The plan is the unit of work — finish it.

The only valid reasons to stop early are:
- A task is genuinely blocked by missing information that cannot be found in the codebase
- A quality gate fails and cannot be fixed without human input

In either case, report the specific blocker clearly and stop. Otherwise, keep going.

Each listed task must be completed such that the acceptance criteria are fully met.

All code that is produced must have unit test coverage. If a section should not be tested
(generic setup/boilerplate) or cannot be directly tested (external calls that would be
onerous to mock), exclude it via inline exclusion markers for the coverage tool. 100%
coverage for all new or modified code should be the goal.

You are writing code, not providing commentary on the plan artifact. If you have doubts about
the plan, report that feedback to the caller before you start. Do NOT modify ANY planning
documents.


## Process


### 1. Understand the plan

- Read the complete implementation plan document.
- Read the corresponding design plan document.
- Review the project commands. If they are missing from the plan, STOP and report back.


### 2. Execute every task

Work through every task in order, from first to last, without stopping. For each task:

- Read the task carefully, paying close attention to the acceptance criteria.
- Follow test-driven design:
  - Write the failing test.
  - Run it and verify it fails.
  - Implement the code.
  - Run the test and verify it passes.
- Run linters and type checks after each task.
- Write a journal entry describing what was done and the outcome.
- Move immediately to the next task.

Do not pause between tasks. Do not batch tasks into groups and report partway through.
Continue until every task is done.


### 3. Final verification

After all tasks are complete, run the full project quality gate:

```shell
make qa
```

All of the following must pass with zero errors:

- Type checking
- Linting
- All tests

If any quality check fails, fix the issue before reporting back. Do not report the work as
complete while quality checks are failing.


### 4. Report back

Report back to the orchestrator only after all tasks are complete and all quality checks
pass. Summarize results, note any challenges or surprises, and include the final `make qa`
output.
