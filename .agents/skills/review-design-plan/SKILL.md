---
name: review-design-plan
description: Instructions for reviewing design plans artifacts. Use when specifically requested.
---

# Review Design Plan Skill

Read the provided design plan artifact and critique it in a structured review artifact.


## Prerequisites

Your prompt must include:

- Path to the design plan
- Iteration number (N = 01 for first review, 02+ for re-reviews)
- For re-reviews: path to the prior review artifact

If not provided, ask before proceeding. Do not guess.


## Scope

- You are reviewing a **design plan** artifact. Not code.
- Do NOT run tests, builds, or linters.
- Do NOT modify the document.
- You MAY use read-only project skills for wider context.


## Steps

Track your progress through these steps:


### 0. Setup

Load the `create-design-plan` skill to understand the expected artifact structure. Load any other relevant
skills for context.


### 1. Resolve prior findings (re-review only)

If a prior review artifact is provided, read it completely. For each prior finding, check whether the design
plan has been updated to address it:

- ✓ Fully resolved — note the change in the plan
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — carry this forward as a Critical finding in the current review


### 2. Evaluate structural completeness

The document MUST match the `.agents/templates/design-plan.md` template.

Call out missing sections, incomplete information, violations of scope, or deviation from the template.


### 3. Gauge acceptance criteria quality

For each AC:

- Make sure they are numbered correctly (`AC01`, `AC02`, ...)
- Verify that they are observable and testable
- Cover important success and failure modes: happy path, variations, edge cases, AND important failure cases

Flag any AC that is vague, subjective, redundant, or is not actually AC (e.g. an implementation detail).


### 4. Determine architectural clarity

Ensure that the architecture fully describes the solution. Make sure needed components are identified and that
unnecessary detail is excluded. Verify that the architecture matches the Goal and AC.


### 5. Flag ambiguity

Flag instances of:

- Hedged language in requirements: "might", "should probably", "if applicable"
- Undefined nouns or jargon used without definition
- Passive constructions hiding the actor ("data is processed" — by what?)


### 6. Ensure unknowns relevance

Ensure that the listed ambiguities are legitimate. Call out noise in this section. Make sure there is a clear
resolution possible for each item. Call out any missing ambiguities that need to be addressed.


### 7. Categorize findings

Each finding should be given a severity level:

- **Critical**: structure violation (missing/extra sections), untestable ACs, hallucinated project elements.
- **Significant**: missing modes in AC, ambiguity that would block implementation planning, fuzzy scope.
- **Trivial**: incorrect grammar, awkward wording, organizational improvements, minor disagreement.

----

## Artifact

Write the review to `design-review--{N}.md` in the same directory as the design plan. Use
`.agents/templates/design-review.md` as the template. Supply the path to your caller on completion.
