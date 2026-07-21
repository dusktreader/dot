# Design Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 07**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/design-plan.md


## Overview

The review confirms that the design plan continues to satisfy all required properties. The
model-specific dispatch policy now explicitly covers `run-bug-fix` and `run-fix`, with the shared
branch-based requirement extending the same rule to every applicable handoff in newly
worktree-enabled workflows. No new findings were raised.

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     0


## Prior Review Resolution

- **All prior findings** ✓: Review 06 closed with zero findings. No prior items carry forward.


## Findings

### Summary

| Finding | Title | Outcome |
| ------- | ----- | ------- |

No findings.

----

## Notes

**run-bug-fix lifecycle (AC03):** The lifecycle is explicit and complete. AC03 specifies
investigation → bug report → human-approved implementation plan → isolated-worktree execution →
one documented final QA pass → independent agent code review → human approval → exclusive squash
merge into the ready-to-PR parent branch. It explicitly adopts the stale-parent reconciliation
(AC18) and worktree-and-branch cleanup (AC19) rules shared by every branch-based workflow. No
gaps or ambiguities remain.

**Expanded worktree coverage (AC17):** AC17 names all five branch-based workflows —
`run-feature`, `run-task`, `run-bug-fix`, `run-fix`, and `run-hotfix` — as required to create an
isolated agent worktree and branch before producing any artifact or code. The Architecture section
also enumerates this set explicitly and states that hack runs retain their direct, no-lifecycle
behavior. Coverage is complete.

**Hotfix gates (AC21):** AC21 preserves the streamlined hotfix controls without change. It
confirms that `run-hotfix` uses an agent worktree, and then explicitly states that isolation adds
no new approval or review gate. The brief investigation, principal-authored minimal plan, direct
execution, single lightweight review, and existing approval thresholds all remain unchanged. No
inadvertent gate was introduced.

**Model-specific specialist dispatch (AC03, AC10, AC20, and AC21):** `run-bug-fix` and
`run-fix` now require a principal-selected model-specific specialist at every investigator,
planner, executor, QA-fix, and reviewer handoff. AC10 makes this a shared branch-based rule,
with GitHub Copilot variants required for work projects and approved personal variants required
for personal projects. The implementation journal or relevant review context records the exact
selected variant. The shared rule also covers applicable handoffs in `run-feature`, `run-task`,
and `run-hotfix`, without adding a planner handoff where the hotfix design deliberately retains a
principal-authored minimal plan.

The design plan is approved for implementation planning.
