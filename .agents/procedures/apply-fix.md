# Apply Fix Procedure

Coordinate a bounded fix from planning through QA. The caller owns the worktree, dedicated fix artifact directory,
approved-stage commits, and handoff. Use `docs` for the approved fix plan and `fix` for approved execution and QA
changes.


## Invocation context

The caller must provide all values explicitly:

- `fix_origin`: `standalone` or `triage`
- `entry_stage`: `plan`, `execution`, or `qa`
- `exit_stage`: `plan`, `execution`, or `qa`; it must be at or after the entry stage
- `fix_artifact_dir`: dedicated directory for this fix's artifacts
- `fix_context`: direct human-provided fix request or triage findings
- Selected branch and worktree
- For triage origin: `bug-report.md` within `fix_artifact_dir`
- For `execution` entry: exact fix-plan path, human approval evidence tied to that revision, and final blocker-check
  pass
- For `qa` entry: exact approved fix plan, execution review, human acceptance, and execution blocker-check pass
- Whether essential plan Unknowns were resolved and approved by the human

Reject missing or ambiguous workflow inputs. Never infer approval of Unknowns or a plan revision.

Run from `entry_stage` through `exit_stage`. At approved plan and execution boundaries, yield to the caller for the
caller-owned stage commit, then resume the same invocation. Do not require a new invocation to cross those boundaries.
Return from the procedure only after `exit_stage`. Do not create or remove branches or worktrees, commit, publish,
create a pull request, or perform handoff.


## Artifact topology

Use only `fix_artifact_dir` for fix-specific records:

| Artifact                              | Description                             |
| ------------------------------------- | --------------------------------------- |
| `implementation-plan.md`              | Narrow, executor-ready fix plan         |
| `implementation-review--NN.md`        | Fix plan review                         |
| `execution-journal.md`                | Record of fix implementation            |
| `plan-deviations.md`                  | Post-plan implementation and QA changes |
| `execution-review--whole-plan--NN.md` | Independent review of the fix execution |

For triage-origin fixes, `bug-report.md` lives in `fix_artifact_dir` and remains read-only. Do not modify source
reports, project plans, journals, or reviews supplied as context.


## Lifecycle phases and states

| Phase                | State                         | Transition                                                      |
| -------------------- | ----------------------------- | --------------------------------------------------------------- |
| Fix planning         | Fix plan authoring            | Resolve Unknowns; continue to agent review                      |
| Fix planning         | Fix plan agent review         | Findings: revise and re-review; approval opens human feedback   |
| Fix planning         | Fix plan human feedback       | Revisions: agent review; approval opens blocker check           |
| Fix planning         | Fix plan final blocker check  | BLOCKED: return through review and feedback; PASS: execution    |
| Fix execution/review | Fix execution                 | Focused checks pass: execution agent review                     |
| Fix execution/review | Execution agent review        | Findings: fix and re-review; approval opens human feedback      |
| Fix execution/review | Execution human feedback      | Changes: agent review; accepted: execution blocker check        |
| Fix execution/review | Execution final blocker check | BLOCKED: resolve and re-review; PASS: QA                        |
| QA                   | QA authoring                  | Requested changes: verify with human; approval opens completion |
| QA                   | QA completion                 | Return QA evidence and artifacts to caller                      |


### Fix planning phase

#### Fix plan authoring

At `entry_stage=plan`, dispatch the shared `engineer-planner` role with
`.agents/procedures/create-implementation-plan.md`, `fix_context`, `fix_artifact_dir`, output path
`implementation-plan.md`, and project context. For triage origin, include `bug-report.md` from `fix_artifact_dir`.
Instruct the planner to investigate relevant existing code, tests, standards, and commands, then author a narrowly
scoped fix plan using the canonical implementation-plan artifact definition and template. Record planner routing
metadata.

When the plan contains essential Unknowns, pause and return their text and the draft path to the caller. The caller
resolves them with the human and resumes planning. Do not proceed to review until the caller confirms the Unknowns are
resolved. Never invent answers.


#### Fix plan agent review

Dispatch the shared `architect-reviewer` role with `.agents/procedures/review-implementation-plan.md`, the plan path,
`review_mode=full`, iteration, and output path `implementation-review--NN.md`. Resolve findings and repeat review after
material revisions until the reviewer approves. Apply trivial findings directly. Use judgment on significant or critical
findings; flag ambiguities requiring human input. Record finding outcomes in the review artifact.


#### Fix plan human feedback

After agent approval, invoke `.agents/procedures/discuss-plan-with-human.md` with the exact fix plan path, plan type
`implementation`, fix-plan approval purpose, full-review artifact, current state, resume state **Fix plan final blocker
check**, and a single-plan gate. If revisions are requested, revise the plan and return through agent review before
presenting it again. Questions, silence, triage authorization, and approval of an earlier revision do not approve the
current plan for blocker checking.


#### Fix plan final blocker check

After human approval of the exact current plan revision, dispatch the shared `engineer-reviewer` role with
`.agents/procedures/check-for-blockers.md`, `check_stage=plan`, the human-approved plan, the initial full review, prior
blocker result when rechecking, and blocker artifact path. If blocked, resolve findings. Any plan revision returns
through agent review and human feedback before rechecking with the prior result.

On `Gate result: PASS`, yield for the caller-owned plan commit. If `exit_stage=plan`, return after that commit.
Otherwise, continue this invocation into execution after the caller commits. Do not request another plan approval after
the blocker check. Never re-invoke the procedure just to resume; never infer approval or gate results.


### Fix execution and review phase

#### Fix execution

When the invocation reaches execution, whether directly or from planning, read
`.agents/artifacts/execution-journal/description.md`, `.agents/artifacts/execution-journal/template.md.j2`,
`.agents/artifacts/plan-deviations/description.md`, and `.agents/artifacts/plan-deviations/template.md.j2`. Render
`execution-journal.md` and `plan-deviations.md` in `fix_artifact_dir`, recording the approved fix plan as the source
plan and `None` for the design plan unless the caller supplies an applicable design plan.

Dispatch the shared `engineer-executor` role with `.agents/procedures/execute-implementation-plan.md`,
`plan_type=implementation`, the exact approved fix plan, supplied fix context, execution journal, deviation journal, and
branch/worktree context. The executor completes all plan tasks, runs focused documented checks, and records work, files
changed, acceptance evidence, and verification. Use the same role for constrained review fixes; record implemented plan
departures in `plan-deviations.md`.


#### Execution agent review

Dispatch the shared `engineer-reviewer` role with `.agents/procedures/review-implementation-execution.md`,
`plan_type=implementation`, the approved fix plan, execution journal, deviation journal, output path
`execution-review--whole-plan--NN.md`, iteration, and branch/routing context. Resolve findings, record implemented
changes in `plan-deviations.md`, and re-review after material changes. Keep triage reports and other source artifacts
read-only.


#### Execution human feedback

Invoke `.agents/procedures/review-execution-with-human.md` with the execution-review artifact, execution journal,
focused verification, `fix_artifact_dir`, worktree/branch, deviation journal, current state, and resume states. If
changes are requested, implement against the approved fix plan, record them in `plan-deviations.md`, and return through
execution review. On acceptance, proceed to **Execution final blocker check**.


#### Execution final blocker check

Dispatch the shared `engineer-reviewer` role with `.agents/procedures/check-for-blockers.md`, `check_stage=execution`,
approved fix plan, execution journal, deviation journal, execution-review artifact, and verification results. If
blocked, resolve issues and return through execution review and human feedback. On pass, return execution and blocker
evidence to the caller for the execution-stage commit. If `exit_stage=execution`, return after that commit. If
`exit_stage=qa`, continue this invocation into QA after the caller commits.


### QA phase

#### QA authoring

At the QA stage, invoke `.agents/procedures/qa-implementation.md` with plan type `implementation`, approved fix plan,
execution journal, deviation journal, worktree/branch, and return state **QA completion**.


#### QA completion

Return explicit QA approval evidence, QA changes, and artifact paths to the caller at `exit_stage=qa`. The caller owns
QA commits and later handoff.
