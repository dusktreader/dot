# Build Feature Procedure

Apply the shared design, implementation-planning, execution, and QA procedure to build a single feature. This procedure
does not own a branch, worktree, commits, cleanup, or publication.


## Invocation context

The caller must provide all context explicitly:

- `execution_mode`: `standalone` or `epic`
- `entry_stage`: `design` or `implementation-planning`
- `exit_stage`: `design` or `qa`; must follow the entry stage and applicable mode
- `feature_artifact_dir`: the directory containing this feature's detailed artifacts
- `feature_id`: a stable `FNN` identifier for an epic feature, or explicit `None` for an unnumbered standalone feature
- `parent_epic_artifact`: the exact `epic-plan.md` path for an epic feature, or explicit `None` for a standalone feature
- Current branch and worktree selected by the caller
- For epic implementation-planning entry: the immutable approved design path, its final blocker-check pass, and evidence
  that the human approved this exact feature design as part of the current slice design set

Reject ambiguous or inferred context. Standalone calls must use `entry_stage=design` and `exit_stage=qa`. Epic design
calls must use `entry_stage=design` and `exit_stage=design`; epic implementation calls must use
`entry_stage=implementation-planning` and `exit_stage=qa`. Epic implementation calls must not proceed without all
required approval evidence listed above.

Enter at the requested `entry_stage`. Return control after the requested `exit_stage` completes. Epic design entry
returns after the feature passes **Design agent review**, so the coordinator can assemble and approve the complete slice
design set. Standalone design entry continues through design approval, implementation planning, execution, and QA. Epic
implementation-planning entry begins with the approved design evidence and continues through QA before returning
control.


## Ownership and invariants

The procedure owns feature-scoped lifecycle states and records. It never creates or removes a branch or worktree,
changes the human's worktree, commits or publishes, or creates a pull request. The caller owns approved-stage commits
and final handoff.

Use the feature artifact directory for all detailed records. Create these artifacts as their lifecycle phases begin.
Approved design and implementation plans are immutable after approval. Record all later implementation, code-review, and
QA changes in `plan-deviations.md`, whether human-directed or agent-initiated, and whether or not they depart from plan.

| Artifact                              | Description                                           |
| ------------------------------------- | ----------------------------------------------------- |
| `design-plan.md`                      | Feature design                                        |
| `design-review--NN.md`                | Individual design reviews                             |
| `implementation-plan.md`              | Feature implementation plan                           |
| `implementation-review--NN.md`        | Implementation-plan reviews                           |
| `execution-journal.md`                | Record of work implemented against the plan           |
| `plan-deviations.md`                  | Post-plan implementation, code-review, and QA changes |
| `execution-review--{scope-id}--NN.md` | Execution reviews                                     |

Use `execution-journal.md` to record what was implemented for each plan task and how its acceptance criteria were
addressed. For an epic feature, repeat its `FNN` identifier in plan and review titles, the execution journal, deviation
journal, and relevant metadata. Link the parent epic and feature ID in feature records. A standalone feature may use the
same artifact set without an epic ID.

Never edit approved plans or reviews during execution, code review, or QA.


## Lifecycle phases and states

| Phase                   | State                                   | Transition                                                                          |
| ----------------------- | --------------------------------------- | ----------------------------------------------------------------------------------- |
| Design                  | Design authoring                        | Resolve Unknowns; continue to Design agent review                                   |
| Design                  | Design agent review                     | Standalone: Design human feedback; epic design entry: return at `exit_stage=design` |
| Design                  | Design human feedback                   | Approval: Design final blocker check; revisions: agent review                       |
| Design                  | Design final blocker check              | PASS: Implementation-plan authoring; BLOCKED: discuss and recheck                   |
| Implementation planning | Implementation-plan authoring           | Resolve Unknowns; continue to Implementation-plan agent review                      |
| Implementation planning | Implementation-plan agent review        | Approved: human feedback; findings: revise and re-review                            |
| Implementation planning | Implementation-plan human feedback      | Approval: final blocker check; revisions: agent review                              |
| Implementation planning | Implementation-plan final blocker check | PASS: Execution; BLOCKED: discuss and recheck                                       |
| Execution               | Execution                               | Tasks and focused tests complete: Execution agent review                            |
| Execution               | Execution agent review                  | Approved: human feedback; findings: fix and re-review                               |
| Execution               | Execution human feedback                | Changes: agent review; accepted: Execution final blocker check                      |
| Execution               | Execution final blocker check           | PASS: QA authoring; BLOCKED: resolve and re-review                                  |
| QA                      | QA authoring                            | Human approves QA: QA completion                                                    |
| QA                      | QA completion                           | Return QA result at `exit_stage=qa` to caller or epic coordinator                   |


### Design phase

#### Design authoring

Dispatch the shared `architect-planner` role with `.agents/procedures/create-design-plan.md`, feature requirements,
explicit context, and feature directory. Describe outcomes and acceptance criteria, not implementation details. Use the
feature ID in the title and link the parent epic when supplied. Read `.agents/artifacts/design-plan/description.md` and
render its template. Replace all template values with project-specific content.

If the design contains Unknowns, invoke `.agents/procedures/resolve-unknowns-with-human.md` with the design path,
decision context, and resume state **Design agent review**. When the design is complete and essential Unknowns are
resolved, proceed to **Design agent review**.


#### Design agent review

Dispatch the shared `architect-reviewer` role with `.agents/procedures/review-design-plan.md`, the design plan path,
`review_mode=full`, iteration, and output review path. Resolve findings and repeat review after material revisions until
the reviewer approves the design.

For standalone mode, an approved review advances to **Design human feedback**. For epic design entry, do not request
per-feature human approval. Return control to the coordinator at `exit_stage=design` after individual design review; the
coordinator assembles and approves the complete design set and runs a final blocker check for each design. A material
epic design change invalidates the affected set approval.


#### Design human feedback

For standalone mode, invoke `.agents/procedures/discuss-plan-with-human.md` with the revised design path, the
individual-design approval purpose, and next state **Design final blocker check**. If feedback requests revisions,
update the design and return to **Design agent review**. If feedback leaves Unknowns unresolved, invoke
`.agents/procedures/resolve-unknowns-with-human.md` and resume at **Design agent review**. Once the exact design
revision is approved and no Unknowns remain, proceed to **Design final blocker check**.

For epic design entry, the coordinator owns human review of the complete design set; this procedure does not invoke
individual plan discussions with the human.


#### Design final blocker check

Dispatch the `architect-reviewer` subagent with `.agents/procedures/review-design-plan.md`, the exact human-approved
design revision, `review_mode=final-blocker-check`, the initial full review, prior blocker-check artifact when
rechecking, and a review artifact path.


If blocked, invoke `.agents/procedures/discuss-plan-with-human.md` to present the findings and obtain approval of a
revised candidate, then redispatch the `architect-reviewer` with the prior blocker-check result. A pass makes the
approved design immutable and advances to **Implementation-plan authoring**. This check is not a second full review.


### Implementation-planning phase

#### Implementation-plan authoring

Dispatch the shared `engineer-planner` role with `.agents/procedures/create-implementation-plan.md`, the approved design
path, explicit context, and feature directory. The procedure owns authoring the feature-scoped plan from the canonical
artifact definition and template.

If the draft contains Unknowns, invoke `.agents/procedures/resolve-unknowns-with-human.md` with the implementation-plan
path, decision context, and resume state **Implementation-plan agent review**. Once resolved, proceed to
**Implementation-plan agent review**.


#### Implementation-plan agent review

Dispatch the shared `architect-reviewer` role with `.agents/procedures/review-implementation-plan.md`, the plan path,
`review_mode=full`, iteration, and output review path. Resolve findings and repeat review after material revisions until
the reviewer approves the plan. Then proceed to **Implementation-plan human feedback**.


#### Implementation-plan human feedback

Invoke `.agents/procedures/discuss-plan-with-human.md` with the revised implementation-plan path, the individual-plan
approval purpose, and next state **Implementation-plan final blocker check**. If feedback requests revisions, update the
plan and return to **Implementation-plan agent review**. If feedback leaves Unknowns unresolved, invoke
`.agents/procedures/resolve-unknowns-with-human.md` and resume at **Implementation-plan agent review**. Once the exact
plan revision is approved and all Unknowns are resolved, proceed to **Implementation-plan final blocker check**.


#### Implementation-plan final blocker check

Dispatch the `architect-reviewer` subagent with `.agents/procedures/review-implementation-plan.md`, the exact
human-approved implementation-plan revision, `review_mode=final-blocker-check`, the initial full review, prior
blocker-check artifact when rechecking, and a review artifact path. Apply the plan blocker criteria described in
**Design final blocker check**. The procedure returns its gate result, evidence, findings, and review artifact to this
workflow.

If blocked, invoke `.agents/procedures/discuss-plan-with-human.md` to present findings and obtain approval of a revised
plan, then redispatch the `architect-reviewer` with the prior blocker-check result. A pass makes the plan immutable and
advances to **Execution authoring** without another human approval. The caller commits the approved implementation-plan
stage.


### Execution phase

#### Execution authoring

Before execution, read `.agents/artifacts/plan-deviations/description.md` and render its template as
`plan-deviations.md` in the feature directory, recording the approved source plans. Record all implementation,
code-review, and QA changes there, whether human-directed or agent-initiated and whether or not they depart from the
approved plan. Include source, request or trigger, plan alignment, resulting change, reason when provided, and
verification.

Before dispatch, read `.agents/artifacts/execution-journal/description.md` and render
`.agents/artifacts/execution-journal/template.md.j2` as `execution-journal.md` in the feature directory. Then dispatch
the shared `engineer-executor` role with `.agents/procedures/execute-implementation-plan.md`,
`plan_type=implementation`, the approved plan, design plan, journal path, feature ID, parent epic path, and feature
directory.

When every plan task is complete and focused tests pass, proceed to **Execution agent review**. If work is blocked,
report the blocker to the caller and stop in this state.


#### Execution agent review

Dispatch the shared `engineer-reviewer` role with `.agents/procedures/review-implementation-execution.md`,
`plan_type=implementation`, `execution-journal.md`, the approved plan, `plan-deviations.md`, review artifact path and
iteration, and worktree/branch context. Keep plans and journals read-only to the reviewer.

Resolve findings in the implementation and record implemented changes in `plan-deviations.md`. Run focused checks and
request review again until the reviewer approves. Approval advances to **Execution human feedback**; it does not replace
human review. Findings return to **Execution authoring** for fixes.


#### Execution human feedback

Invoke `.agents/procedures/review-execution-with-human.md` with the execution-review artifact, execution journal,
focused verification, feature directory, worktree/branch, current state, and resume states for requested changes or
acceptance. Follow its protocol. If the human requests changes, implement approved requests in **Execution authoring**,
record them in `plan-deviations.md`, and return to **Execution agent review**. If the human accepts the reviewed
implementation, proceed to **Execution final blocker check**.


#### Execution final blocker check

Dispatch the `engineer-reviewer` subagent with `.agents/procedures/check-for-blockers.md` and `check_stage=execution`,
providing the approved implementation plan, `execution-journal.md`, execution-review artifact, `plan-deviations.md`, and
verification results. The procedure returns its gate result, evidence, and findings to this workflow.

If blocked, resolve the reported issues in **Execution authoring** and return to **Execution agent review**. A pass
advances to **QA authoring**; the caller owns commit and handoff for the approved execution stage.


### QA phase

#### QA authoring

Invoke `.agents/procedures/qa-implementation.md` with plan type `implementation`, the feature artifacts, and worktree
and branch context. For epic mode, specify the coordinator's separate human-verification requirement. Continue to **QA
completion** after the procedure returns explicit QA approval.


#### QA completion

For standalone mode, return the QA result and artifact paths to the caller at `exit_stage=qa`. The caller commits and
handles handoff. For epic mode, return the QA result and paths to `execution-journal.md` and `plan-deviations.md` to the
epic coordinator. The coordinator obtains explicit human verification of the completed feature before starting the next
feature and integrated slice verification after all feature QA gates pass. The lifecycle does not mark an epic or slice
accepted.
