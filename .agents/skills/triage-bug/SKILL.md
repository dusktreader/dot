# Triage Bug Skill

Investigate a reported defect, establish root cause and impact, and ask the human whether to authorize remediation.
Triage does not modify product code. If remediation is authorized, the workflow continues through the shared `apply-fix`
procedure.


## When to use

Use when the root cause, affected scope, or appropriate remedy is unclear and needs investigation. Use `run-fix` when
the defect and desired change are already understood and the human requests a fix. Use `run-task` for bounded non-bug
changes and `external-review` for PR review feedback.


## Prerequisites

The prompt must include a bug description. Include reproduction steps when known. If the description is missing, ask
before proceeding; do not guess.


## Workflow phases and states

| Phase         | State                     | Transition                                                      |
| ------------- | ------------------------- | --------------------------------------------------------------- |
| Setup         | Worktree setup            | Select worktree for investigation and possible fix              |
| Setup         | Triage artifact setup     | Create shared triage/fix artifact directory                     |
| Investigation | Bug investigation         | Gather root cause, impact, approach, and unresolved questions   |
| Investigation | Diagnosis confirmation    | Correct diagnosis or confirm it before asking about remediation |
| Investigation | Remediation authorization | Authorize planning and a proposed fix, request inquiry, or stop |
| Fix           | Apply fix                 | Begin planning only with explicit human authorization           |
| Handoff       | Triage/fix complete       | Report investigation and any authorized fix artifacts           |


## Setup phase

### Worktree setup

Invoke `.agents/procedures/use-worktree.md` with branch type `fix`, a concise bug summary, and ticket if provided. Work
only in the returned worktree.


### Triage artifact setup

Invoke `.agents/procedures/use-artifact-dir.md` in the selected worktree with the same bug summary, `branch_type=fix`,
and ticket used for `use-worktree`. Store `bug-report.md` in the returned shared case directory. If remediation is
authorized, use this same directory as `fix_artifact_dir`; do not create a second directory.


## Investigation phase

### Bug investigation

Dispatch the shared `engineer-investigator` role with `.agents/procedures/investigate-codebase.md`, the bug description,
known reproduction steps, and the shared case artifact directory. Ask the investigator to determine observed and
expected behavior, reproducibility, confirmed or inferred root cause, affected code paths, blast radius, a high-level
proposed approach, and unresolved questions. The investigator is read-only and must not write files or run
state-changing commands.

Synthesize the findings into `bug-report.md`. Read `.agents/artifacts/bug-report/description.md` and render
`.agents/artifacts/bug-report/template.md.j2`. Replace all sample content with evidence-based findings and leave no
placeholders. Record investigator profile, tier, project class, and handoff purpose in the report context.

If root cause or material scope remains unclear, dispatch the investigator with a focused follow-up and update the
report. Distinguish confirmed observations from inferences.


### Diagnosis confirmation

Present `bug-report.md` and ask the human to correct or explicitly confirm the diagnosis. Stop and wait for that
response. Root-cause confirmation does not authorize planning or code changes.

- If the human corrects the diagnosis or requests more investigation, update the report and repeat investigation as
  needed, then ask for confirmation again.
- If the human confirms the diagnosis, record the exact report revision and continue to **Remediation authorization**.
- If the human does not confirm the diagnosis, do not proceed to remediation authorization.


### Remediation authorization

After diagnosis confirmation, separately ask whether the human authorizes planning and a proposed fix. Stop and wait for
explicit authorization. This authorization permits plan creation and review only. The human then reviews and approves
the exact fix plan before its final blocker check; execution resumes only if that check passes.

- If the human declines remediation or requests inquiry instead, record that outcome and stop or continue investigating
  only as requested.
- If the human explicitly authorizes remediation, record the authorization evidence and continue to **Fix phase**.
- If the human's response is ambiguous or silent, do not plan or modify product code.


## Fix phase

Invoke `.agents/procedures/apply-fix.md` once with `fix_origin=triage`, `entry_stage=plan`, `exit_stage=qa`, the exact
`bug-report.md` path within the shared triage artifact directory, that same directory as `fix_artifact_dir`, and the
selected worktree/branch. Remediation authorization is secured here, before invoking the procedure. The procedure keeps
the report read-only and stores all fix artifacts alongside it.


## Handoff phase

Report the shared case artifact directory, diagnosis confidence, affected scope, authorization status, selected
branch/worktree, and QA result if remediation proceeded. Leave the worktree and branch intact. The artifacts provide
sufficient context; suggest a new session for follow-on work. The human decides what to do next. Do not push, publish,
create a pull request, merge, or squash.
