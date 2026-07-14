# Implementation Plan Review: Carve work-specific configuration into private work-dot repository

**Iteration 05**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/implementation-plan.md


## Overview

Focused review against the six consistency constraints listed in the review brief:
application-owned `creds fetch`, no Typerdrive secret facility claims, nested credentials model,
JiraInfo migration coverage, API gate enforcement, and command syntax assumptions. Prior findings
from iteration 04 are fully resolved. Two new findings surfaced.

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     1


## Prior Review Resolution

- **S01** ✓: Task 08 step 10 now reads "Verify all changes are committed on the feature branch.
  Do not push. The user will push and merge when ready." AC10 added to Task 08 confirming no push
  occurs.
- **T01** ✓: Task 15 AC05 revised to "Pushes to remote repositories occur only when the user
  explicitly authorizes them."


## Findings


### Summary

| Finding | Title                                                                         | Outcome |
| ------- | ----------------------------------------------------------------------------- | ------- |
| S01     | Task 05 ACs do not constrain `creds fetch` key lookup to the credentials sub-model | |
| T01     | Task 08 AC07 cross-references wrong task number                               | |


### Significant


#### S01: Task 05 ACs do not constrain `creds fetch` key lookup to the credentials sub-model

##### Where

Execution — Task 05 — Acceptance Criteria — AC02, AC03 — approximately lines 560–562


##### Issue

Task 05 AC02 says `dt creds fetch <key>` "prints the named secret value to stdout" and AC03 says
it exits non-zero "if the key does not exist in `Settings`." Both ACs name `Settings` as the target
without restricting lookup to the nested `credentials` sub-model required by design plan AC17. Step 2
of the same task compounds this: it says "Retrieves the attribute from `Settings` by name using
`getattr` or nested access as appropriate," leaving the implementor free to resolve `key` against
any attribute of the top-level `Settings` object — including non-credential fields such as a
hypothetical `theme` or `default_branch`.

The intent, enforced in Task 04 AC02 and the design plan, is that credential fields live exclusively
inside a nested `credentials` sub-model and that `creds fetch` addresses that sub-model, not the
top-level settings tree.


##### Impact

An implementor following these ACs literally could satisfy every criterion by resolving `key` as
`getattr(settings, key)` across all of `Settings`, exposing non-credential settings through the
`creds fetch` interface. The resulting implementation would technically pass Task 05's ACs while
violating design plan AC17's structural requirement. The discrepancy would only become visible during
the execution review, after the code is already written.


##### Suggestion

Revise AC02 and AC03 to name the nested credentials sub-model explicitly:

> AC02: `dt creds fetch <key>` prints the value of the named field within `Settings.credentials`
> to stdout with no surrounding formatting.

> AC03: `dt creds fetch <key>` exits non-zero (code 1) and prints a diagnostic message to stderr
> if `<key>` does not name a field in `Settings.credentials` (not in top-level `Settings`).

Revise step 2 accordingly:

> Retrieves the value by resolving `key` against `settings.credentials` (the nested credentials
> sub-model), not against top-level `Settings` fields. Raises an error if `key` is not an attribute
> of the credentials sub-model.

The symmetric Task 04 ACs (AC03, AC04) use "the named field within `WorkSettings.credentials`" —
align Task 05 to the same language.


##### Outcome


----


### Trivial


#### T01: Task 08 AC07 cross-references wrong task number

##### Where

Execution — Task 08 — Acceptance Criteria — AC07 — line 806


##### Issue

AC07 reads: "…except for the conditional include that points to the work overlay file, which is
added in task 08." The conditional include for the work overlay is added in Task 09
("Add conditional Git include for work overlay in dot"), not Task 08. Task 08 is the work-content
removal pass. Directing a reader to "task 08" for the conditional include is a misdirection that
would cause confusion during execution review.


##### Suggestion

Replace "task 08" with "Task 09":

> AC07: Git config in `.gitconfig` or `.gitconfig.dusktreader` no longer references any work paths
> or work-specific includes (except for the conditional include that points to the work overlay
> file, which is added in Task 09).


##### Outcome


----


## Notes

All six focused constraints from the review brief are clear in the plan:

- **Application-owned `creds fetch`**: The Terminology section (lines 33–38) and both Task 04 and
  Task 05 Technical Notes consistently identify `creds` as application-defined and explicitly state
  Typerdrive provides no built-in `creds` facility. No issues.
- **No Typerdrive secret facility claims**: The Goal, Terminology, and the Technical Notes at lines
  1459–1461 all disclaim any Typerdrive credentials API. The Typerdrive integration section at the
  end of Technical Notes (lines 1446–1461) names only standard Typerdrive capabilities. No issues.
- **Nested credentials model**: Task 04 AC02 and Task 06 AC01–AC02 correctly enforce the nested
  `credentials` sub-model requirement. S01 above identifies a gap in Task 05's parallel enforcement.
- **JiraInfo migration coverage**: Task 13 steps 9 and 10 (lines 1157–1166) and Technical Notes
  (lines 1178–1187) explicitly address the transition of existing `Settings`/`JiraInfo` inline
  fields to the nested credentials model. Coverage is thorough.
- **API gate**: The Unknowns section and Task 04's Technical Notes both state that Tasks 05, 06, 13,
  and 14 must use only verified syntax from Task 04 steps 1–2. The sequential task ordering (04 →
  05 → 06) operationalizes this gate. No issues.
- **Command syntax assumptions**: The plan consistently avoids claiming specific bind syntax. Exact
  syntax is deferred to Task 04 research throughout, including in the Terminology section and in all
  downstream task notes. No issues.

S01 is the only change required before execution of Task 05. T01 is a one-word correction and does
not block execution.
