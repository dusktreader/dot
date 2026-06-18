# Code Review

A structured review of code changes against quality standards, produced without reference to
an implementation plan or journal. Used when there is no plan to verify against — the review
is purely a code quality assessment.


## Template Variables

| Variable  | Description                                                              |
| --------- | ------------------------------------------------------------------------ |
| `title`   | Short descriptive title for the review (e.g. the PR title or branch name)|
| `n`       | Zero-padded iteration number (`01` for first review, `02`+ for re-reviews) |


## Sections


### Source

A bulleted list of every file included in the review.


### Verification Evidence

Output of all quality gate commands run: tests, build, linter, and coverage. Each line
records the command and its result. Record `skipped` for any command not run, with a reason.


### Issue Summary

A count of findings at each severity level: Critical, Significant, Trivial.


### Prior Review Resolution

Present only for re-reviews (iteration N > 01). For each finding from the prior review,
records whether it was resolved (✓), partially resolved (⚠), or not resolved (✗), with a
brief note. Omit entirely for the first review.


### Findings

Same structure as execution-review findings, including the Summary table and severity
subsections with Finding IDs (`C##`, `S##`, `T##`).

Each finding contains: Where (`file:line`), Issue, Impact, Fix, Outcome.

The Summary table Outcome column is filled in by the orchestrator.


### Skills Applied

A list of skills loaded during the review, noting whether each was project-local or a global
fallback.


### Decision

`APPROVED` or `BLOCKED — CHANGES REQUIRED`.

If blocked: list the finding IDs that must be resolved before re-review.
If approved: confirm that all quality gates passed.
