# Design Plan Review: Tune agent workflows and report OpenCode costs

**Iteration 03**


## Source Artifact

.artifacts/20260715--tune-agent-workflows/design-plan.md


## Overview

The review surfaced findings:

- **Critical**:    0
- **Significant**: 2
- **Trivial**:     1


## Prior Review Resolution

- **S01** ✓: AC02 now states "It never pushes or creates a pull request" — prohibition is unconditional.
- **T01** ✓: AC09 now states "The principal recommends a model from this menu, may escalate independently, and asks
  Tucker only for a genuinely unresolved material workflow or cost tradeoff" — direct and unambiguous.


## Findings

### Summary

| Finding | Title                                                                 | Outcome                                                                                                                           |
| ------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| S01     | Squash-only integration not stated; AC17 staleness check is gap-prone | Accepted: feature and task integration is exclusively a squash merge into the ready-to-PR parent branch.                          |
| S02     | Agent worktree teardown lifecycle is unspecified                      | Accepted: successful squash removes the worktree while retaining its local audit branch; declined and abandoned runs retain both. |
| T01     | AC16 fires before worktree exists on early-abort gates                | Accepted: only gates after worktree creation report its path and branch.                                                          |


### Significant

#### S01: Squash-only integration not stated; AC17 staleness check is gap-prone

**Where**

Acceptance Criteria — AC17, lines 166–170; Architecture, lines 175–188


**Issue**

AC17 scopes its staleness check to "a feature or task squash integration." The plan never
states that squash is the only integration mode — no AC or architecture sentence rules out a
rebase integration path. If any integration path other than squash is permissible, AC17's
protection does not apply to it, and a stale agent branch could be silently integrated via
that alternative path. Conversely, if squash is the sole integration mode, that constraint
belongs as an explicit statement in the architecture or its own AC, not as a silent assumption
embedded inside AC17's scope restriction.


**Impact**

An implementer reading this plan will not know whether to build a single squash-merge path or
to guard multiple integration paths. If the staleness check is accidentally omitted for a
permitted rebase path, the core safety property of AC17 is violated without any AC being
technically broken.


**Suggestion**

Either add a sentence to the Architecture section stating that feature and task integration is
exclusively a squash merge of the agent branch into the parent, or add an AC covering the
integration mode constraint directly. Then AC17's reference to "squash integration" becomes
unambiguous.


**Outcome**

Accepted and applied. Feature and task workflows now state that they exclusively squash merge their agent branch into
their ready-to-PR parent branch. AC17 and the architecture constrain stale-work reconciliation to rebase or regeneration
before that squash merge.

----

#### S02: Agent worktree teardown lifecycle is unspecified

**Where**

Architecture — lines 175–188; Acceptance Criteria — AC01, AC02, AC16, AC17


**Issue**

The architecture describes worktree creation (before any artifact or code change) and the
integration point (squash merge), but does not address what happens to the agent worktree
after integration completes, after integration is explicitly declined, or after an abandoned
or failed run. AC16 and AC17 imply the worktree persists through all human gates, but no AC
or architecture statement governs removal.


**Impact**

The implementation plan will have to invent teardown behavior from scratch. This introduces
divergence risk: one implementer removes the worktree on integration success only; another
prompts the human; another leaves it permanently. Leaked worktrees accumulate silently if
the teardown path is never specified. This is not an edge case — every successful run
produces a worktree that must eventually be removed.


**Suggestion**

Add a sentence to the Architecture section stating the teardown model. For example: "After
a successful squash integration the agent worktree is removed. If integration is declined or
the run is abandoned, the worktree is left in place and the human is informed of its path and
how to remove it manually." If automatic teardown on failure is intended, state that as well.


**Outcome**

Accepted and applied. Agent worktrees and branches persist through human gates; successful squash merges remove only
the worktree while preserving the local audit branch. Declined and abandoned runs retain both until explicit human
removal.

----

### Trivial

#### T01: AC16 may fire before worktree exists on early-abort gates

**Where**

Acceptance Criteria — AC16, lines 159–162; AC01, lines 32–35


**Issue**

AC16 requires every human gate in a feature or task run to report the agent worktree path.
AC01 states the worktree is created before any workflow artifact. If a workflow raises an
early-abort human gate before worktree creation completes — for example, on a precondition
failure — AC16 would require reporting a path that does not yet exist. The current text does
not acknowledge this ordering constraint.


**Impact**

Minimal — the happy path has no exposure. However, an implementer may add an early-abort
gate before worktree setup and be uncertain whether to satisfy AC16 with a placeholder or
defer reporting.


**Suggestion**

Add a qualifying clause to AC16: "Every human gate after the agent worktree is established
reports its path and branch." This makes the ordering dependency explicit without weakening
the inspection guarantee.


**Outcome**

Accepted and applied. AC16 now limits workspace reporting to human gates after the agent worktree is established.

----

## Notes

- S01, S02, and T01 are resolved by the explicit human decisions recorded in their outcomes.
- The Unknowns section has been removed from the plan. This is acceptable — all prior
  unknowns were resolved and the section has no remaining items. No action required.
