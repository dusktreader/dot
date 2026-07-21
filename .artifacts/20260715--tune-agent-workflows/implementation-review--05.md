# Implementation Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 05**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/implementation-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     1


## Prior Review Resolution

- **T01** ✗: Task 06 AC06 is unchanged from iteration 04. It still reads "Staged guidance selects model-specific
  specialist variants from the defined staged OpenCode variant inventory, assigns model choice, escalation, risk
  classification, and approval decisions to the principal, and prevents a work-project dispatch from selecting a Zen
  model." No worktree-specific observable has been added. The suggested replacement was not applied. Carried forward as
  T01 below.


## Findings


### Summary

| Finding | Title                                                                    | Outcome |
| ------- | ------------------------------------------------------------------------ | ------- |
| S01     | Task 08 AC02 covers happy path only; missing-project-context AC absent   |         |
| T01     | Task 06 AC06 still overlaps Task 05 AC04 without a worktree-specific observable |         |


### Significant

#### S01: Task 08 AC02 covers happy path only; missing-project-context AC absent

##### Where

Execution — Task 08 — Acceptance Criteria — approximately line 555.


##### Issue

AC02 asserts the happy path: the workflow locates the existing implementation project and attaches artifacts at its
established path. The failure mode — when the project cannot be located, the artifact directory is ambiguous, or the
expected path cannot be established — appears only in Step 3 prose ("Reject ambiguous or missing project context
rather than guessing") and in Technical Notes ("fail closed when the expected artifact path cannot be established").
No AC requires this observable behavior, so the executor has no testable criterion for the closed-failure path and the
reviewer has no criterion to verify.

This gap matters specifically for `run-fix` because it is the one branch-based workflow that depends on finding
external context before worktree setup can proceed meaningfully. A missing or ambiguous project path is a
high-probability failure mode, not an edge case.


##### Impact

An executor implementing Task 08 can pass all AC without implementing closed-failure behavior. A reviewer checking
AC01–AC06 at completion will find no basis to flag a missing-project-path guard as an omission. The gap surfaces at
runtime rather than at review time.


##### Suggestion

Add an AC between the current AC02 and AC03:

> AC02b: When the existing implementation project cannot be located, its artifact directory is ambiguous, or the
> expected agent-worktree project path cannot be established, the workflow stops and reports the specific resolution
> failure to the human without creating or modifying any artifact or code.

Renumber subsequent ACs or use the `AC02b` label to preserve existing references.


##### Outcome


----


### Trivial

#### T01: Task 06 AC06 still overlaps Task 05 AC04 without a worktree-specific observable

##### Where

Execution — Task 06 — Acceptance Criteria — AC06 — approximately line 458.


##### Issue

AC06 asserts principal ownership of model choice, escalation, risk classification, approval decisions, and Zen
exclusion for work-project dispatch. Task 05 AC04 already asserts: "Staged principal, executor, investigator,
planner, reviewer, workflow, and review policies assign risk and model decisions to the principal and enforce the
work-project versus personal-project model menus." The two criteria are substantively identical. Task 06's subject
is the worktree-enabled feature and task guidance; AC06 adds no observable behavior specific to worktree creation,
integration gates, or cleanup.


##### Impact

An executor completing Task 06 has no worktree-scoped criterion to verify for AC06. The coverage gap may cause a
reviewer to accept Task 06 as done without verifying any worktree-lifecycle-specific observable tied to model
dispatch.


##### Suggestion

Replace AC06 with a worktree-specific observable:

> AC06: Worktree creation, gate prompts, integration steps, and cleanup instructions in the staged `run-feature` and
> `run-task` guidance contain no model-selection language, deferring model choice entirely to the principal dispatch
> policy documented in Task 05 AC04.


##### Outcome


----


## Notes

S01 does not block Tasks 07 or 09 but should be resolved before Task 08 execution begins. The fix is a one-line AC
addition. T01 is a third-iteration carry-forward and can be applied in the same revision. Resolving both in the next
plan pass is strongly recommended. All Critical findings from prior iterations remain resolved; the plan is otherwise
approvable for Tasks 01–07 and 09–13 in parallel with the T08 AC addition.
