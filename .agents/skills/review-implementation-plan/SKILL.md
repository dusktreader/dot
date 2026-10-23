---
name: review-implementation-plan
description: Instructions for reviewing implementation plans artifacts. Use when specifically requested.
---

# Review Implementation Plan Skill

Read the provided implementation plan artifact and critique it in a structured review artifact.


## When to use

Use this skill to critique an implementation plan artifact for structural
completeness, AC quality, task ordering, and markdown conformance.

This skill is a sub-skill called by orchestrators:
- `run-feature-lifecycle` — implementation-planning stage in standalone and epic modes
- `run-bug-fix` — after the bug fix plan is produced
- `run-fix` — after the scoped fix plan is produced

Do not confuse with `review-design-plan`, which reviews the higher-level design artifact. Use this skill
only for implementation plan artifacts — those describing HOW to build something.


## Prerequisites

Your prompt must include:

- Path to the implementation plan
- Iteration number (N = 01 for first review, 02+ for re-reviews)
- Optional review mode: `full` (default) or `final-blocker-check`
- For re-reviews: path to the prior review artifact
- In `final-blocker-check` mode: path to the initial full review; for
  blocker rechecks, also provide the prior blocker-check artifact

If not provided, ask before proceeding. Do not guess.


## Scope

- You are reviewing an **implementation plan** artifact. Not code.
- Do NOT run tests, builds, or linters.
- Do NOT modify the document.

The default review mode is `full`. In `final-blocker-check` mode, read the initial full review and examine the exact
human-approved revision. On blocker rechecks, verify the prior blocker-check findings first; do not reopen earlier
non-blocking suggestions. Do not repeat the full checklist below; use it only to test for blockers. Report only Critical
or Significant flaws that could make execution infeasible, contradict the approved design, omit critical acceptance or
verification work, or introduce substantial security, data-integrity, or operational risk. Ignore wording and
formatting. If no blocker exists, explicitly approve the plan for execution and write `Gate result: PASS` in
Notes; otherwise write `Gate result: BLOCKED` and identify the blocking findings.


## Steps

Track your progress through these steps:


### 0. Setup

Load the `create-implementation-plan` skill for process context. Read
`.agents/artifacts/implementation-plan/description.md` for the canonical section definitions.
Locate the design plan referenced in the implementation plan for higher-level context.


### 1. Resolve prior findings (re-review only)

If a prior review artifact is provided, read it completely. For each prior finding,
check whether the implementation plan has been updated to address it:

- ✓ Fully resolved — note the change in the plan
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — carry this forward as a Critical finding in the current review

In `final-blocker-check` mode, carry forward only unresolved findings that meet the blocker
threshold. Prior Trivial findings and non-blocking suggestions remain non-blocking.


### 2. Evaluate structural completeness

The document MUST match the structure defined in `.agents/artifacts/implementation-plan/description.md`.

Call out missing sections, incomplete information, violations of scope, or deviation from the expected structure.


### 3. Find missing standards

Review the `## Project Standards` section. Ensure that all relevant
standards are enumerated. Flag missing or hallucinated standards.


### 4. Check agent skills

Review the `## Relevant Skills` section. Ensure that all listed skills actually exist. Flag hallucinated skills.


### 5. Format markdown

In `full` mode, run `dt format markdown` before reviewing the document. Do not pass `--check` or spend review tokens
manually fixing formatting that the formatter handles. In `final-blocker-check` mode, do not format or modify the
human-approved plan; review that exact revision and ignore formatting-only issues.


### 6. Evaluate execution tasks

Step through the `## Execution` section. For each task, review:


#### Acceptance criteria

For each AC:

- Make sure they are numbered correctly (`AC01`, `AC02`, ...)
- Verify that they are observable and testable
- Cover important success and failure modes: happy path, variations, edge cases, AND important failure cases

Flag any AC that is vague, subjective, redundant, or is not actually AC (e.g. an implementation detail).


#### Steps

For each step:

- Make sure the step is scoped correctly: neither too broad nor too fine-grained
- Ensure that it is correct
- Check order: make sure the step is not out of order and follows sequentially with the others

----

### 7. Ensure unknowns relevance

Ensure that the listed ambiguities are legitimate. Call out noise in this section. Make sure there is a clear resolution
possible for each item. Call out any missing ambiguities that need to be addressed.


### 8. Categorize findings

Each finding should be given a severity level:

- **Critical**: structure violation (missing/extra sections), untestable ACs, hallucinated project elements.
- **Significant**: missing modes in AC, ambiguity that would block implementation, fuzzy scope.
- **Trivial**: incorrect grammar, awkward wording, markdown formatting violations, minor disagreement.

----

## Artifact

Write the review to `implementation-review--{N}.md` in the same directory as the implementation plan. Read
`.agents/artifacts/implementation-review/description.md` for the canonical section definitions, and render
`.agents/artifacts/implementation-review/template.md.j2` to produce the initial file. Replace all dummy content — every
line drawn from the retro encabulator — with real content for this review. The rendered file must contain
no placeholder text when submitted. Supply the path to your caller on completion.
