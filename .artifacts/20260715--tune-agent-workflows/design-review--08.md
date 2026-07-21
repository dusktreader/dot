# Design Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 08**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/design-plan.md


## Overview

Re-review focused on shared and explicit model-specific dispatch requirements for `run-bug-fix`,
`run-fix`, and every branch-based workflow. The design plan satisfies all requirements in scope.
No new findings were raised.

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     0


## Prior Review Resolution

- **All prior findings** ✓: Review 07 closed with zero findings. No prior items carry forward.


## Findings

### Summary

| Finding | Title | Outcome |
| ------- | ----- | ------- |

No findings.

----

## Notes

**Shared dispatch rule (AC10, second paragraph):** The shared requirement is stated once and
precisely: every branch-based workflow applies model-specific specialist-variant selection at
every applicable investigator, planner, executor, QA-fix, and reviewer handoff; the exact
selected variant is recorded in the implementation journal or review context; GitHub Copilot
variants are required for work projects and approved personal variants for personal projects.
The Architecture section restates this rule in its own words without contradiction, which
confirms it is a first-class policy rather than a per-workflow afterthought.

**run-bug-fix dispatch coverage (AC03):** AC03 enumerates the five handoff roles explicitly
— investigator, planner, executor, QA-fix, and reviewer — and cross-references AC10 by name.
The lifecycle ordering (investigation → bug report → human-approved implementation plan →
isolated-worktree execution → one documented final QA pass → independent agent code review →
human approval → exclusive squash merge) maps one-to-one against those roles. No handoff is
left without a dispatch instruction.

**run-fix dispatch coverage (AC20):** AC20 enumerates the same five handoff roles and
cross-references AC10 by name, matching the pattern established by AC03. The fix-artifact
scoping rule (fix artifacts written at the existing project's path within the agent worktree)
is orthogonal to dispatch and does not introduce a gap.

**run-hotfix dispatch coverage (AC21):** AC21 correctly limits the enumeration to applicable
handoffs — investigator, executor, QA-fix, and reviewer — omitting planner because the hotfix
design retains a principal-authored minimal plan rather than a specialist planner. This
omission is intentional and internally consistent.

**Branch-based workflow set coverage (AC17):** The complete set of branch-based workflows —
`run-feature`, `run-task`, `run-bug-fix`, `run-fix`, and `run-hotfix` — is named consistently
in AC17, AC03, AC20, AC21, and the Architecture section. No workflow is cited in one location
and omitted in another.

**run-hack explicitly excluded:** AC04 states that `run-hack` creates no branch, has no Git
lifecycle, and does not create or use an agent worktree. It is therefore outside the
branch-based dispatch rule. AC10 and the Architecture section both describe the shared rule as
applying to branch-based workflows, which excludes hack consistently.

The design plan is approved for implementation planning.
