---
name: run-feature-lifecycle
description: Internal shared feature lifecycle for standalone and epic-coordinated workflows.
---

# Run Feature Lifecycle

Apply the shared design, implementation-planning, execution, review, and QA controls to one feature. This is an internal
contract invoked by `run-feature` or `run-epic`; it does not own a branch, worktree, commits, cleanup, or publication.


## Invocation context

The caller must provide all context explicitly:

- `execution_mode`: `standalone` or `epic`
- `entry_stage`: `design` or `implementation-planning`
- `feature_artifact_dir`: the directory containing this feature's detailed artifacts
- `feature_id`: a stable `FNN` identifier for an epic feature, or explicit `None` for an unnumbered standalone feature
- `parent_epic_artifact`: the exact `epic-plan.md` path for an epic feature, or explicit `None` for a standalone feature
- Current regular branch and worktree selected by the caller
- For epic implementation-planning entry: the immutable approved design path, its final blocker-check pass, and evidence
  that the human approved this exact feature design as part of the current slice design set

Reject ambiguous or inferred context. An epic implementation-planning entry must not proceed without every
approval record above. The caller owns its worktree, branch, and commit policies.


## Ownership and invariants

The lifecycle owns only feature-scoped stage gates and records. It never creates or removes a branch or worktree, never
changes the human's worktree, never commits or publishes, and never creates a pull
request. The caller owns each approved-stage commit and the final handoff.

Use the feature artifact directory for all detailed records. For an epic feature, repeat its `FNN` identifier in the
plan title, review titles, journal, deviation record, QA journal, and relevant metadata. Link the parent epic and
feature ID in the feature records. A standalone feature may use the same artifact set without an epic ID.

An approved design plan and implementation plan are immutable once feature execution
begins. Do not edit approved plans or reviews during execution, code review, or QA.


## Lifecycle state machine

| State                              | Transition                                                                    |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| Design authoring                   | Initial design review                                                         |
| Design agent review                | Findings return to authoring; approval opens human feedback                   |
| Design human feedback              | Human approves exact candidate; opens final blocker check                     |
| Design final blocker check         | Major blockers return to human feedback; a pass opens implementation planning |
| Implementation authoring           | Initial implementation-plan review                                            |
| Implementation agent review        | Findings return to authoring; approval opens human feedback                   |
| Implementation human feedback      | Human approves exact candidate; opens final blocker check                     |
| Implementation final blocker check | Major blockers return to human feedback; a pass opens execution               |
| Execution                          | Agent execution review                                                        |
| Agent execution review             | Findings return to execution; approval opens human code review or QA          |
| Human code review                  | Feedback is incorporated before final code review; decline proceeds to QA     |
| Final agent code review            | Findings return to execution review; approval opens QA                        |
| QA                                 | User-directed changes return to QA; explicit approval closes the feature      |

The standalone entry begins at design authoring. Epic design entry performs individual design authoring and initial
agent review while the coordinator assembles the slice design set. The coordinator's approval of the complete exact set
is the single human gate for those designs. The coordinator supplies that approval evidence for each feature's final
blocker check. Only individually checked, immutable designs included
in the approved set may enter epic implementation planning.


## Final blocker checks

After initial agent findings have been resolved and the human has reviewed the plan, dispatch the final reviewer in
`final-blocker-check` mode. Pass the exact human-approved revision and the initial review artifact. On a blocker
recheck, also pass the prior blocker-check artifact and ask the reviewer to verify those blockers first. Check only
major flaws that could invalidate the plan or break the outcome: contradictions with requirements, missing critical
acceptance or verification work, infeasible sequencing, or material architectural, security, or data-integrity risks. Do
not block on wording, formatting, or other non-blocking suggestions. Require the
reviewer to record `Gate result: PASS` or `Gate result: BLOCKED` in Notes.

The human approval before this check is the single human gate. If the reviewer finds a blocker, return the evidence to
the human for review and update. Obtain approval of the revised candidate before rerunning the blocker check. Once it
passes, proceed without another human approval and treat that exact plan
revision as immutable. A clean final check is not a second full review.


## Design stages

Dispatch the shared `architect-planner` role with `create-design-plan`, the feature requirements, explicit context, and
feature directory. The design describes outcomes and acceptance criteria, not implementation
details. Use the feature ID in the title and link the parent epic when supplied.

Dispatch the shared `architect-reviewer` role with `review-design-plan` in full mode for the initial structured
adversarial review. Resolve findings and record outcomes. Re-review
material changes. The reviewer does not edit the plan.

For standalone mode, stop for human review and explicit approval of the exact revised design. Resolve Unknowns one at a
time with the human and remove each resolved item from the Unknowns section. `feedback complete` alone is not approval.
Then run the final blocker check described above. For epic mode, do not request a separate per-feature human approval;
the coordinator obtains approval of the complete exact slice design set before each design's final blocker check.

For epic mode, if a final blocker requires a material design change, invalidate the affected set approval. Pause
dependent implementation until the affected design has passed its blocker
check and the complete affected set receives renewed human approval.


## Implementation-planning stages

Dispatch the shared `engineer-planner` role with `create-implementation-plan` and the approved design path. Keep the
implementation plan feature-scoped, with testable acceptance criteria and commands from the project. Dispatch the shared
`architect-reviewer` role with `review-implementation-plan` in
full mode; resolve findings and re-review material changes.

Stop for human review and explicit approval of the exact revised implementation plan. Then run the final blocker check
against that revision and the initial review. If it passes, the plan becomes immutable and execution may begin without a
second human approval. The caller commits the approved stage according to its own contract.


## Execution and review stages

Before execution, read `.agents/artifacts/plan-deviations/description.md` and render its template as
`plan-deviations.md` in the feature directory. Record no deviations until a human-directed implementation change departs
from an approved plan. Record the request, affected plan reference,
resulting change, reason when provided, and verification.

Dispatch the shared `engineer-executor` role with `execute-implementation-plan`, the approved plan, feature ID, parent
epic path, and feature directory. Use test-driven design for code: write a failing test, confirm
failure, implement, then confirm it passes. Keep approved plans and reviews immutable.

Dispatch the shared `engineer-reviewer` role with `review-implementation-execution` for an initial execution review.
Resolve findings; re-review material fixes. If the human opts into code review, incorporate feedback and obtain explicit
`feedback complete` before final agent code review. Do not reconcile or edit approved plans. If the human declines
code review, proceed to QA. Final code review approval also proceeds directly to QA.

For an epic feature, record every material departure in the feature deviation artifact. If it changes slice scope,
dependencies, sequencing, success criteria, or another feature, also require an epic-wide deviation record. Pause
affected unfinished dependent work until the epic impact assessment and any required renewed approval are complete.


## QA and completion

Stop after agent review and any optional human code review. Tell the human the feature is ready for QA and wait for
user-directed testing feedback. Before the first QA change, render `.agents/artifacts/qa-journal/template.md.j2` as
`qa-journal.md` in the feature directory. Record each request, reason, files changed, and focused verification. Do not
modify plan or review artifacts during QA. After each change, run focused verification and wait for the human to verify
it. Explicit human QA approval closes the feature; silence, questions, or reported issues do not.

For epic mode, return the QA result and artifact paths to the coordinator. The coordinator must obtain explicit human
verification of the completed feature before starting the next feature, then obtain integrated slice verification after
all feature QA gates pass. The lifecycle does not mark an epic or slice accepted.
