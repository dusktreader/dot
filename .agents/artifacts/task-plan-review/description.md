# Task Plan Review

A structured critique of a focused task plan, produced by an independent reviewer before human approval. The
`review-task-plan` procedure uses this artifact definition.


## Template variables

| Variable | Description                                                                |
| -------- | -------------------------------------------------------------------------- |
| `title`  | Title of the task plan being reviewed                                      |
| `n`      | Zero-padded iteration number (`01` for first review, `02`+ for re-reviews) |


## Sections

### Source artifact

Path to the task plan being reviewed.


### Overview

A count of findings at each severity level: Critical, Significant, Trivial.


### Prior review resolution

Present only for re-reviews. Record whether each prior finding was resolved, partially resolved, or unresolved, with a
brief explanation. Omit entirely for the first review.


### Findings

#### Summary

A table with one row per finding: ID, title, and outcome. Leave outcome empty for the caller to complete after resolving
the finding.


#### Severity sections

Include one subsection for each severity level that has findings: Critical, Significant, Trivial. Each finding uses a
single-letter ID prefix: `C##`, `S##`, or `T##`.

Each finding contains:

- **Where**: the plan section and approximate line number
- **Issue**: what is wrong
- **Impact**: the consequence if the finding remains unresolved
- **Suggestion**: a concrete correction, when one is clear
- **Outcome**: completed by the caller after discussing or resolving the finding


### Notes

Record contextual observations, related findings, or questions requiring human input that do not fit a formal finding.
