# Run Task Skill

Coordinate a bounded task with a human-approved plan, focused execution, implementation review, and user-directed QA.
Use this workflow when the scope is clear and a full design cycle would be excessive.


## When to use

Use this skill for a well-scoped minor change where the human already knows what they want and a separate design
document adds no value. Examples include small features, localized refactors, configuration or tooling changes, style
fixes, tests for existing behavior, and documentation updates.

Use `run-feature` when the change requires unresolved design decisions, coordinates multiple subsystems, has uncertain
scope, or introduces a major module, package, or data structure. Use `triage-bug` when a bug's cause or scope is
unclear, `run-fix` when a defect is understood and explicitly authorized for fixing, and `external-review` for PR review
comments.


## Prerequisites

The prompt must include a clear description of the task. If it is missing, ask before proceeding.


## Artifact topology

After worktree setup, invoke `.agents/procedures/use-artifact-dir.md` with the same task summary, branch type, and
ticket used for `use-worktree`. Store all task artifacts in the returned directory. Use the `task-plan-review` artifact
definition for plan reviews and the shared execution-journal, execution-review, and plan-deviations artifacts for the
remaining records:

| Artifact                              | Description                                          |
| ------------------------------------- | ---------------------------------------------------- |
| `task-plan.md`                        | Minimal task plan                                    |
| `task-plan-review--NN.md`             | Independent task-plan review                         |
| `execution-journal.md`                | Work implemented against the task plan               |
| `execution-review--whole-plan--NN.md` | Implementation review                                |
| `plan-deviations.md`                  | All post-plan implementation, review, and QA changes |


## Lifecycle phases and states

| Phase                | State                         | Transition                                                      |
| -------------------- | ----------------------------- | --------------------------------------------------------------- |
| Setup                | Worktree setup                | Select task worktree and record the branch                      |
| Task planning        | Task plan authoring           | Resolve essential Unknowns; continue to agent review            |
| Task planning        | Task plan agent review        | Findings: revise and re-review; approval opens human review     |
| Task planning        | Task plan human review        | Revisions: agent review; approval opens blocker check           |
| Task planning        | Task plan final blocker check | BLOCKED: discuss and recheck; PASS: commit and execute          |
| Execution and review | Execution                     | Task and focused tests complete: execution agent review         |
| Execution and review | Execution agent review        | Findings: fix and re-review; approval opens human feedback      |
| Execution and review | Execution human feedback      | Changes: agent review; accepted: execution blocker check        |
| Execution and review | Execution final blocker check | BLOCKED: resolve and re-review; PASS: commit and QA             |
| QA                   | QA authoring                  | Requested changes: verify with human; approval opens completion |
| QA                   | QA completion                 | Report result and artifacts; task is complete                   |


### Setup phase

#### Worktree setup

Invoke `.agents/procedures/use-worktree.md` with the task summary, ticket if provided, and a suitable branch type. Keep
task artifacts and code changes in the returned worktree. Do not create branches or worktrees directly or modify the
project root.


### Task planning phase

#### Task plan authoring

Dispatch the shared `engineer-task-planner` role with `.agents/procedures/create-task-plan.md`, the task description,
and artifact directory. The procedure directs the planner to investigate and author `task-plan.md` using the canonical
task-plan artifact definition and template. If essential Unknowns arise, invoke
`.agents/procedures/resolve-unknowns-with-human.md` to resolve them with the human, then resume plan authoring or review
as appropriate.


#### Task plan agent review

Dispatch the shared `architect-reviewer` role with `.agents/procedures/review-task-plan.md`, the task-plan path, review
iteration, output review path, and any prior review artifact. Resolve findings in the plan and repeat review after
material revisions. A satisfactory review opens the human review gate; it does not approve the plan for the human.


#### Task plan human review

Invoke `.agents/procedures/discuss-plan-with-human.md` with the task-plan path, plan type `task`, review purpose
`task-plan approval`, task-plan review artifact, current state, resume state **Task plan final blocker check**, and a
single-plan gate. If the human requests revisions, update the plan and return through agent review. Questions and
silence are not approval.


#### Task plan final blocker check

Dispatch the `architect-reviewer` role with `.agents/procedures/check-for-blockers.md` and `check_stage=plan`, providing
the exact human-approved task-plan revision and task-plan review artifact. If blocked, invoke
`.agents/procedures/discuss-plan-with-human.md` to present findings and obtain approval of a revised plan, then rerun
the blocker check with the prior result. After a pass, commit the approved plan using a `docs` commit and proceed to
execution.


#### Execution

Before execution, read `.agents/artifacts/execution-journal/description.md` and render
`.agents/artifacts/execution-journal/template.md.j2` as `execution-journal.md` in the task artifact directory. Record
the approved task plan as the journal's source plan and use one task entry for the coherent task or one per independent
sub-task in the plan. Read `.agents/artifacts/plan-deviations/description.md` and render its template as
`plan-deviations.md`, recording the approved task plan as the source and `None` for the design plan.

Dispatch the shared `engineer-executor` role with `.agents/procedures/execute-implementation-plan.md`, `plan_type=task`,
the exact approved task plan, task artifact directory, and the `plan-deviations.md` path. Keep the approved task plan
immutable. Record all later implementation, review, and QA changes in `plan-deviations.md`, including source, plan
alignment, change, reason when provided, and verification.

When execution is complete, proceed to execution agent review.


#### Execution agent review

Dispatch the shared `engineer-reviewer` role with `.agents/procedures/review-implementation-execution.md`,
`plan_type=task`, the approved task plan, `execution-journal.md`, `plan-deviations.md`, worktree and branch context, and
the review artifact path and iteration. Repeat review until the execution is approved by the reviewer; resolve findings
in execution and record implemented changes in `plan-deviations.md`. Then proceed to **Execution human feedback**.


#### Execution human feedback

Invoke `.agents/procedures/review-execution-with-human.md` with the execution-review artifact, journal, focused
verification, task artifact directory, worktree and branch, current state, and resume states. If the human requests
changes, implement them in execution, record them in `plan-deviations.md`, and return through execution review. On
acceptance, proceed to the final blocker check.


#### Execution final blocker check

Dispatch the shared `engineer-reviewer` role with `.agents/procedures/check-for-blockers.md` and
`check_stage=execution`, providing the approved task plan, execution journal, execution-review artifact, deviations, and
verification results. If blocked, resolve findings and return through execution review and human feedback as needed.
After a pass, commit the approved execution stage and proceed to QA.


### QA phase

#### QA authoring

Invoke `.agents/procedures/qa-implementation.md` with plan type `task`, the task artifacts, and worktree and branch
context. Continue to **QA completion** after it returns explicit QA approval.


#### QA completion

After QA approval, report the project directory, task branch, review outcome, QA status, and paths to the final
artifacts. These artifacts are sufficient context for subsequent work. Suggest that the human start a new session for
any follow-on work; leave the worktree and branch intact. The task workflow is complete.
