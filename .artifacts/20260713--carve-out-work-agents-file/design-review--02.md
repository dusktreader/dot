# Design Plan Review: Carve work-specific configuration into a private work-dot repository

**Iteration 02**


## Source Artifact

.artifacts/20260713--carve-out-work-agents-file/design-plan.md


## Overview

The review surfaced the following findings:

- **Critical**:    0
- **Significant**: 1
- **Trivial**:     2


## Prior Review Resolution

- **S01** ✓: AC19 now states `wdt configure` is fully non-interactive, seeds missing entries with
  empty placeholder values, prints a stderr notice for each missing or empty secret, never blocks for
  input, and exits successfully even when every secret remains empty.
- **S02** ✓: AC04 and the Configuration invocation flow section both specify that on `wdt configure`
  non-zero exit, `dt configure` reprints stdout and stderr under a labeled prefix and exits non-zero;
  when `wdt` is absent from PATH, `dt configure` exits successfully with no work-related output.
- **S03** ✓: AC17a was added as a standalone criterion mirroring AC17 for `wdt`, pinning the stdout
  contract, stderr error message, exit codes, and the general parity rule across all `wdt secrets`
  sub-commands.
- **S04** ✓: AC02, AC03, and the Configuration invocation flow section were rewritten so `wdt
  configure` is genuinely standalone: it creates its own required directories, arranges for the work
  shell rc to be sourced by the login shell on its own, does not read or write any `dot`-owned asset,
  and does not check for base-layer presence.
- **T01** ✓: Two blank lines now precede `## Unknowns`.
- **T02** ✓: Two blank lines now precede `## Technical Notes`.
- **T03** ✓: The migration table cell for "Hardcoded work Jira identity in client code" now reads
  "Deleted from `dot`; moved to `work-dot`".


## Findings

### Summary

| Finding | Title                                                    | Outcome  |
| ------- | -------------------------------------------------------- | -------- |
| S01     | AC17a uses a non-standard identifier                     | Resolved |
| T01     | AC19 seeds-then-notices phrasing is slightly confusing   | Resolved |
| T02     | Testing strategy stub-`wdt` behavior left underspecified | Resolved |


### Significant

#### S01: AC17a uses a non-standard identifier

##### Where

Acceptance Criteria — AC17a heading, line 159


##### Issue

The acceptance criteria numbering scheme uses the pattern `AC##` (zero-padded two-digit integer).
The new criterion introduced in iteration 02 is labelled `AC17a` rather than `AC18`, which breaks
the scheme. All subsequent criteria (`AC18`–`AC21`) would need to be renumbered, but the current
document leaves them at their existing numbers alongside a lettered outlier, making the sequence
`AC17`, `AC17a`, `AC18` — not a valid sequential list.


##### Impact

The non-standard identifier makes the criterion harder to reference unambiguously in an
implementation plan, in test names, and in review comments. Any tooling that validates or
cross-references AC identifiers by pattern will miss this entry.


##### Suggestion

Renumber `AC17a` as `AC18` and shift the subsequent criteria (`AC18`–`AC21`) to `AC19`–`AC22`.
Update all internal cross-references (the architecture section does not reference AC numbers
directly, so the impact should be limited to the AC section itself).


##### Outcome

Resolved. `AC17a` renumbered to `AC18`; the previous `AC18`–`AC21` shifted to `AC19`–`AC22`. The
cross-reference in the new `AC18` body still points to `AC17` (unchanged), and no other section of
the design plan references the shifted AC numbers.


----

### Trivial

#### T01: AC19 seeds-then-notices phrasing is slightly confusing

##### Where

Acceptance Criteria — AC19, lines 176–181


##### Issue

AC19 states that `wdt configure` "seeds any missing work secret entries with empty placeholder
values" and then "For each missing or empty secret, it prints a notice to stderr." On first run,
every secret is missing; `wdt configure` seeds them all with empty values, then immediately
notices each of them because they are now empty. The two clauses are logically consistent but the
reader must reason through the sequence to confirm they do not contradict each other.


##### Impact

Minimal — the behavior is unambiguous to a careful reader. A casual reader may wonder whether the
notice fires before or after seeding and whether the freshly-seeded placeholder counts as "empty."


##### Suggestion

Tighten the phrasing to make the sequence explicit. For example: "On first run, it creates an entry
for every expected work secret, initialized to an empty value, and prints a notice to stderr for
each one naming the secret and directing the operator to populate it via the `wdt secrets`
interface."


##### Outcome

Resolved. `AC20` (formerly `AC19`) now describes the sequence explicitly: `wdt configure` first
seeds missing entries with empty placeholders, then walks the resulting entries and emits a
per-secret stderr notice for any value that is empty or still a placeholder. The reader no longer
has to reconcile the seeding and notice clauses.


----

#### T02: Testing strategy stub-`wdt` behavior left underspecified

##### Where

Architecture — Testing and validation strategy, lines 318–319


##### Issue

The integration test description mentions exercising `dt configure` "with a stub `wdt` on PATH"
but does not state what the stub does — whether it returns zero (success path), non-zero (failure
path), or both. Without this detail, the test description does not fully capture the two branches
defined in AC04.


##### Impact

Minimal — a competent implementer will write both branches regardless. The gap is in the design
document's completeness, not in any behavioral contract.


##### Suggestion

Expand the stub description to: "with a stub `wdt` on PATH that exits zero (expected: `dt
configure` succeeds and reports work-step success) and with a stub that exits non-zero (expected:
`dt configure` reprints labeled output and exits non-zero)."


##### Outcome

Resolved. The Testing and validation strategy section now describes three integration modes:
`wdt` absent from PATH, a stub `wdt` that exits zero (expected: `dt configure` reports work-step
success and exits zero), and a stub `wdt` that exits non-zero (expected: `dt configure` reprints
the labeled output and exits non-zero). Both branches of AC04 are now covered explicitly
alongside the PATH-absent case.


----

## Notes

S01 is a structural finding with a clear mechanical fix. Renumbering five criteria is low-risk given
that the criteria are not yet referenced by any implementation plan. The fix should be applied before
the plan is approved.

T01 and T02 are cosmetic. Neither blocks implementation planning; both can be deferred or folded into
a copy-edit pass at the author's discretion.

The plan is otherwise in excellent shape. All seven prior findings are fully resolved, no new
behavioral gaps were found, and the architectural decisions remain well-motivated and internally
consistent.
