# PR Review

A structured log of PR review comments and how each was addressed. Produced during the
PR review workflow, one document per review cycle. Tracks every comment from triage through
resolution.


## Template Variables

| Variable        | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `pr_title`      | Title of the pull request being reviewed                                 |
| `pr_url`        | URL of the pull request                                                  |
| `n`             | Zero-padded cycle number (`01` for first review, `02`+ for re-reviews)   |
| `parent_branch` | The parent feature branch the PR was created from                        |


## Sections


### Header Fields

- **PR**: the URL of the pull request
- **Cycle**: the review cycle number (1 for the first review, incrementing for each
  subsequent cycle)
- **Branch**: the agents-review branch used for this cycle
  (`{parent-branch}--agents-review-{N}`)


### Triage

A table with one row per PR comment. Columns:

- **#**: sequential comment number, matching the Comments section below
- **File**: the file the comment applies to
- **Line**: the line number
- **Source**: `human` (reviewer) or `bot` (automated check)
- **Severity**: `critical` | `significant` | `trivial`
- **Disposition**: how the comment will be handled (see below)
- **Outcome**: filled in after fixes are applied — one sentence describing what was done

Severity levels:
- **critical**: incorrect behavior, data loss, crash, security hole — must be addressed
- **significant**: design concern, performance, API contract — must be addressed
- **trivial**: style, naming, nit — addressed at the principal's discretion

Disposition values:
- **auto-fix**: clear, unambiguous fix applied without human input
- **discuss**: a decision is required from the human before acting
- **won't-fix**: out of scope or already addressed; a rationale reply will be posted


### Comments

One `### Comment N` subsection per PR comment, numbered to match the Triage table.

Each comment contains:

- **File**: `path/to/file.ts:line`
- **Source**: `human` or `bot`
- **Severity**: the severity level
- **Disposition**: the disposition

#### Issue

A quote or faithful paraphrase of the review comment. Specific about what the reviewer
identified.

#### Decision

What was decided and by whom:
- For auto-fix: "Applied directly — fix is unambiguous."
- For discuss: the human's decision, recorded verbatim.
- For won't-fix: the rationale for not fixing.

#### Fix

Description of the change made, with `file:line` references. For won't-fix: explanation
of why no change was made.

#### Outcome

Filled in after the fix is committed. Format:
`Addressed in {short-sha} — {one sentence describing the change}.`
or: `Won't fix — {brief rationale}.`
