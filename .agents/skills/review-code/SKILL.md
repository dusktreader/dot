---
name: review-code
description: Reviews code changes directly against quality standards. Use when no implementation plan or journal exists.
---

# Review Code Skill

Review a set of files against quality standards and produce a code review artifact. Use this skill for
standalone reviews where no implementation plan or journal is available.


## Prerequisites

Your prompt must include:

- List of files to review
- Path to the project directory where the artifact will be written

If not provided, ask before proceeding. Do not guess.


## Artifact

Write the review to `code-review--{N}.md` in the project directory. Use
`.agents/templates/code-review.md` as the template. Supply the path to your caller on completion.


## Scope

- Review code only. Do not modify source files.
- There is no implementation plan or journal. Do not attempt to verify acceptance criteria or map files
  to plan tasks.


## Process


### 0. Setup

Load relevant skills by category: testing, coding standards, language/type safety, and any technology
present in the files under review.


### 1. Read the files

Read each file in the review set directly. Understand the shape and purpose of the changes before
forming opinions.


### 2. Run verification commands (if available)

If project commands were provided, run them: tests, build, linter, type-checker, and coverage. Record
results in the artifact.

If not, record `skipped (no project commands provided)` for each entry.

If tests fail or the build is broken: write the review artifact noting the failure output and stop.
Return "Tests failing / Build broken. Fix before review."


### 3. Resolve prior findings (re-review only)

If a prior review artifact is provided, walk through every finding. For each, mark:

- ✓ Fully resolved — cite `file:line` evidence
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — this is a Critical finding in the current review


### 4. Review code and test quality

Apply all loaded skills. Also enforce these quality gates regardless of which skills are loaded:

| Standard                                                           | Severity    |
| ------------------------------------------------------------------ | ----------- |
| Error handling on all external calls (network, fs, db, process)    | Critical    |
| No type-safety violations without a justification comment          | Critical    |
| No swallowed exceptions or ignored return values                   | Critical    |
| New public functions have tests                                    | Critical    |
| Tests verify behavior, not mock interactions                       | Critical    |
| No test-only hooks or helpers in production files                  | Critical    |
| No input validation gaps or injection vectors                      | Critical    |
| Null/undefined inputs handled where applicable                     | Significant |
| Edge cases (empty, boundary, max) covered                          | Significant |
| New code paths covered by tests (when coverage tool available)     | Significant |
| Logic not placed in wiring/bootstrap files without justification   | Significant |
| No unused imports, functions, or branches                          | Trivial     |


### 5. Write the review artifact

Fill in all sections of the template. Store the artifact as described in `## Artifact`.
