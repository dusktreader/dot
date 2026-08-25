# Implementation Plan Review: Carve work-specific configuration into private work-dot repository

**Iteration 04**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md


## Overview

Focused review of Task 01's git workflow constraints and downstream viability. One significant
finding and one trivial finding.

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     1


## Prior Review Resolution

All prior review findings (iterations 01–03) were fully resolved or explicitly rejected. This
iteration is a focused re-review scoped to Task 01's git workflow and its interaction with later
tasks. No prior findings require re-examination.


## Findings

### Summary

| Finding | Title                                                                   | Outcome |
| ------- | ----------------------------------------------------------------------- | ------- |
| S01     | Task 08 step 10 directs an unauthorized push to the public `dot` remote |         |
| T01     | Task 15 AC05 implies push without qualifying which repositories         |         |


### Significant

#### S01: Task 08 step 10 directs an unauthorized push to the public `dot` remote


#### Where

Execution — Task 08 — Steps — line 768


#### Issue

Task 08 step 10 reads "Push to the public `dot` repository." This is a direct instruction to push
to a remote, with no qualifier such as "when the user approves" or "if the user explicitly requests
it." Task 01 establishes the pattern for this implementation: the main/master branch receives only
an `Initial Commit`, all scaffolding lands on a feature branch, and no push occurs until the user
decides. Task 08 applies to the existing `dot` repository, not `work-dot`, but the same guard
applies: the implementation agent must not push unless the user explicitly requests it. This step
contradicts the no-unauthorized-push principle that Task 01 enforces.

The git-safety instructions (`~/.agents/instructions/git-safety.md`) independently prohibit
pushing without explicit user request. The step as written would cause a reviewing agent to flag
any implementation that skipped it, and an executing agent to push prematurely.


#### Impact

An executor following the plan verbatim pushes work-specific-content removal changes to the public
`dot` remote without waiting for user approval. This is a one-way operation: once pushed, the
removal is publicly visible and cannot be undone without a force-push or a revert. It also breaks
the principle established in Task 01 that the user controls merge and push timing.


#### Suggestion

Replace step 10 with:

> 10\. Verify all changes are committed on the feature branch. Do not push. The user will push
> and merge when ready.

Additionally, add an AC to Task 08 confirming that no push occurs during this task — parallel to
Task 01 AC11, which constrains the remote to local-only configuration.


#### Outcome


----

### Trivial

#### T01: Task 15 AC05 implies push without qualifying which repositories


#### Where

Execution — Task 15 — Acceptance Criteria — AC05 — line 1164


#### Issue

AC05 reads "No uncommitted changes remain; all work is committed and pushed to the correct
repositories." The phrase "pushed to the correct repositories" is stated as a completion
criterion for the final validation task. This implicitly makes a push a required outcome of
Task 15, without making clear that the user must authorize any push to `dot` (public) or
`work-dot` (private). Given Task 01's explicit no-push-until-user-decides constraint, AC05
should distinguish between committed (required) and pushed (user-authorized).


#### Impact

Low: Task 15 is the final end-to-end validation task, and a push at that point is likely
intentional. However, leaving the AC ambiguous creates a gap between the no-push discipline
established in Task 01 and the completion criteria in Task 15. An executor or reviewer may
interpret this as permission to push without checking.


#### Suggestion

Revise AC05 to:

> AC05: No uncommitted changes remain; all implementation work is committed to the appropriate
> feature branches. Pushes to remote repositories occur only when the user explicitly approves
> them.


#### Outcome


----

## Notes

Task 01 itself is sound. The `Initial Commit` requirement (AC02–AC04), feature branch constraint
(AC05–AC06), main/master cleanliness (AC13), and no-push discipline (AC11 and Technical Notes)
are all clearly stated, testable, and consistent with each other. Later tasks 02–07, 09–14 do not
contain push instructions and are unaffected.

The single meaningful gap is Task 08 step 10, which actively directs a push. S01 is the only
finding that requires a plan change before execution of Task 08. T01 is a wording clarification
and does not block execution.
