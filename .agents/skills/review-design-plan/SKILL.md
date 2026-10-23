---
name: review-design-plan
description: Instructions for reviewing design plans artifacts. Use when specifically requested.
---

# Review Design Plan Skill

Read the provided design plan artifact and critique it in a structured review artifact.


## When to use

Use this skill to critique a design plan artifact for structural completeness,
AC quality, architectural clarity, and markdown conformance.

This skill is a sub-skill called by the shared feature lifecycle, invoked
by `run-feature` in standalone mode and `run-epic` in epic mode.

Do not confuse with `review-implementation-plan`, which reviews a lower-level implementation plan. Use
this skill only for design plan artifacts — those describing WHAT and WHY, not HOW.


## Prerequisites

Your prompt must include:

- Path to the design plan
- Iteration number (N = 01 for first review, 02+ for re-reviews)
- Optional review mode: `full` (default) or `final-blocker-check`
- For re-reviews: path to the prior review artifact
- In `final-blocker-check` mode: path to the initial full review; for
  blocker rechecks, also provide the prior blocker-check artifact

If not provided, ask before proceeding. Do not guess.


## Scope

- You are reviewing a **design plan** artifact. Not code.
- Do NOT run tests, builds, or linters.
- Do NOT modify the document.
- You MAY use read-only project skills for wider context.

The default review mode is `full`. In `final-blocker-check` mode, read the initial full review and examine the exact
human-approved revision. On blocker rechecks, verify the prior blocker-check findings first; do not reopen earlier
non-blocking suggestions. Do not repeat the full checklist below; use it only to test for blockers. Report only Critical
or Significant flaws that could materially break the design outcome, invalidate acceptance criteria, or introduce
substantial architectural, safety, or data-integrity risk. Ignore wording and formatting. If no blocker exists,
explicitly approve the design for the next stage and write `Gate result: PASS` in
Notes; otherwise write `Gate result: BLOCKED` and identify the blocking findings.


## Steps

Track your progress through these steps:


### 0. Setup

Load the `create-design-plan` skill for process context. Read `.agents/artifacts/design-plan/description.md`
for the canonical section definitions. Load any other relevant skills for context.


### 1. Resolve prior findings (re-review only)

If a prior review artifact is provided, read it completely. For each prior
finding, check whether the design plan has been updated to address it:

- ✓ Fully resolved — note the change in the plan
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — carry this forward as a Critical finding in the current review

In `final-blocker-check` mode, carry forward only unresolved findings that meet the blocker
threshold. Prior Trivial findings and non-blocking suggestions remain non-blocking.


### 2. Evaluate structural completeness

The document MUST match the structure defined in `.agents/artifacts/design-plan/description.md`.

Call out missing sections, incomplete information, violations of scope, or deviation from the expected structure.


### 3. Gauge acceptance criteria quality

For each AC:

- Make sure they are numbered correctly (`AC01`, `AC02`, ...)
- Verify that they are observable and testable
- Cover important success and failure modes: happy path, variations, edge cases, AND important failure cases

Flag any AC that is vague, subjective, redundant, or is not actually AC (e.g. an implementation detail).


### 4. Format markdown

In `full` mode, run `dt format markdown` before reviewing the document. Do not pass `--check` or spend review tokens
manually fixing formatting that the formatter handles. In `final-blocker-check` mode, do not format or modify the
human-approved document; review that exact revision and ignore formatting-only issues.


### 5. Determine architectural clarity

Ensure that the architecture fully describes the solution. Make sure needed components are identified and that
unnecessary detail is excluded. Verify that the architecture matches the Goal and AC.


### 6. Flag ambiguity

Flag instances of:

- Hedged language in requirements: "might", "should probably", "if applicable"
- Undefined nouns or jargon used without definition
- Passive constructions hiding the actor ("data is processed" — by what?)


### 7. Ensure unknowns relevance

Ensure that the listed ambiguities are legitimate. Call out noise in this section. Make sure there is a clear resolution
possible for each item. Call out any missing ambiguities that need to be addressed.


### 8. Categorize findings

Each finding should be given a severity level:

- **Critical**: structure violation (missing/extra sections), untestable ACs, hallucinated project elements.
- **Significant**: missing modes in AC, ambiguity that would block implementation planning, fuzzy scope.
- **Trivial**: incorrect grammar, awkward wording, markdown formatting violations, minor disagreement.

----

## Artifact

Write the review to `design-review--{N}.md` in the same directory as the design plan. Read
`.agents/artifacts/design-review/description.md` for the canonical section definitions, and render
`.agents/artifacts/design-review/template.md.j2` to produce the initial file. Replace all dummy content — every line
drawn from the retro encabulator — with real content for this review. The rendered file must contain
no placeholder text when submitted. Supply the path to your caller on completion.
