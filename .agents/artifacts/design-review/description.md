# Design Plan Review

A structured critique of a design plan artifact. Produced by a reviewer agent, then consumed
by the orchestrator to drive a conversation with the human before the plan is approved.


## Template Variables

| Variable  | Description                                                                |
| --------- | -------------------------------------------------------------------------- |
| `title`   | Title of the design plan being reviewed                                    |
| `n`       | Zero-padded iteration number (`01` for first review, `02`+ for re-reviews) |


## Sections


### Source Artifact

Path to the design plan being reviewed.


### Overview

A count of findings at each severity level: Critical, Significant, Trivial.


### Prior Review Resolution

Present only for re-reviews (iteration N > 01). For each finding from the prior review,
records whether it was resolved (✓), partially resolved (⚠), or not resolved (✗), with a
brief note.

Omit entirely for the first review.


### Findings


#### Summary

A table with one row per finding. Columns: Finding ID, Title, Outcome. The Outcome column
is left empty by the reviewer and filled in by the orchestrator after discussing each finding
with the human.

Outcome entries are one sentence describing how the finding was addressed — not a status word
like "Fully addressed".


#### Severity sections

One `### ` subsection per severity level that has findings: Critical, Significant, Trivial.
Omit levels with no findings.

Within each level, one `#### ` subsection per finding. Finding IDs use a single-letter
prefix: `C##` for Critical, `S##` for Significant, `T##` for Trivial.

Each finding contains:

- **Where**: the section and approximate line number in the reviewed artifact.
- **Issue**: a clear description of what is wrong.
- **Impact**: the concrete consequence if this finding is not addressed — on downstream
  work, correctness, or quality.
- **Suggestion**: a concrete rewrite or fix the reviewer could accept verbatim. Omit if
  no specific fix is obvious.
- **Outcome**: filled in by the orchestrator. Describes whether the finding was accepted
  and applied, partially applied, deferred, or overridden, and why.

Heading formatting rules:
- Each field is an `##### ` heading.
- Every heading is preceded by two blank lines, except the first field directly under
  the finding heading (no prior content).
- Every heading is followed by one blank line before its content.


### Notes

Contextual notes for the orchestrator. For example: relationships between findings
("resolving C01 likely resolves S03"), findings that require human input to resolve,
or observations that did not rise to a formal finding.
