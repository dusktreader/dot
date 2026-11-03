# Create Task Plan Procedure

Delegate authoring of a focused task plan for a bounded engineering task.


## Required inputs

The caller must provide:

- Clear task description and desired outcome
- Path to the project artifact directory
- Output path for `task-plan.md`

If any input is missing or ambiguous, ask the caller before dispatching.


## Authoring

Dispatch the shared `engineer-task-planner` role with this procedure, the task description, and the artifact directory.

The planner investigates the codebase before writing. It verifies relevant code paths, project conventions, existing
tests, and documented build, test, and quality commands. It stops and reports evidence if the requested work is out of
scope, duplicates existing behavior, or appears unsafe.

Read `.agents/artifacts/task-plan/description.md` for canonical section definitions and render
`.agents/artifacts/task-plan/template.md.j2` as `task-plan.md` in the artifact directory. Replace all sample content
with project-specific content. If essential decisions remain unknown, record them clearly for the caller and stop plan
authoring for human resolution. Do not present unresolved essential Unknowns as execution-ready planning.

Keep the plan focused on the goal, exact project commands, relevant standards, actionable steps, and observable
acceptance criteria. Follow test-driven design for code changes. Do not include design-plan sections or expand the task
into a full implementation plan.

Before submission, read and follow `~/.agents/instructions/markdown.md` and run `dt format markdown` on the plan. Return
the plan path and any material investigation findings to the caller.

Do not review or approve the plan, modify product code, commit, or advance the workflow.
