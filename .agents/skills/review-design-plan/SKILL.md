---
name: review-design-plan
description: Instructions for reviewing design plans artifacts. Use when specifically requested.
---

# Review Design Plan Skill

Read the provided design plan artifact and critique it in a structured review artifact.


## When to use

Use this skill to critique a design plan artifact for structural completeness, AC quality,
architectural clarity, and markdown conformance.

This skill is a sub-skill called by orchestrators:
- `run-implementation` — after stage 1 (design) produces a design plan

Do not confuse with `review-implementation-plan`, which reviews a lower-level implementation
plan. Use this skill only for design plan artifacts — those describing WHAT and WHY, not HOW.


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

Load the `create-design-plan` skill for process context. Read `.agents/artifacts/design-plan/description.md`
for the canonical section definitions. Load any other relevant skills for context.


### 1. Resolve prior findings (re-review only)

If a prior review artifact is provided, read it completely. For each prior finding, check whether the design
plan has been updated to address it:

- ✓ Fully resolved — note the change in the plan
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — carry this forward as a Critical finding in the current review


### 2. Evaluate structural completeness

The document MUST match the structure defined in `.agents/artifacts/design-plan/description.md`.

Call out missing sections, incomplete information, violations of scope, or deviation from the expected structure.


### 3. Gauge acceptance criteria quality

For each AC:

- Make sure they are numbered correctly (`AC01`, `AC02`, ...)
- Verify that they are observable and testable
- Cover important success and failure modes: happy path, variations, edge cases, AND important failure cases

Flag any AC that is vague, subjective, redundant, or is not actually AC (e.g. an implementation detail).


### 4. Check markdown formatting

Verify the document conforms to the markdown style guide (`~/.agents/instructions/markdown.md`
and the project's `.agents/docs/standards/markdown.md` if present). Flag violations as findings:

- Lines exceeding 120 characters (outside code blocks and tables)
- Bold-subject quasi-headings used for multi-sentence content instead of proper `###`/`####`
  subsections
- Missing two blank lines before a heading (unless the parent heading has no content)
- List items using `*` or `+` instead of `-`
- Fenced code blocks without a language hint


### 5. Determine architectural clarity

Ensure that the architecture fully describes the solution. Make sure needed components are identified and that
unnecessary detail is excluded. Verify that the architecture matches the Goal and AC.


### 6. Flag ambiguity

Flag instances of:

- Hedged language in requirements: "might", "should probably", "if applicable"
- Undefined nouns or jargon used without definition
- Passive constructions hiding the actor ("data is processed" — by what?)


### 7. Ensure unknowns relevance

Ensure that the listed ambiguities are legitimate. Call out noise in this section. Make sure there is a clear
resolution possible for each item. Call out any missing ambiguities that need to be addressed.


### 8. Categorize findings

Each finding should be given a severity level:

- **Critical**: structure violation (missing/extra sections), untestable ACs, hallucinated project elements.
- **Significant**: missing modes in AC, ambiguity that would block implementation planning, fuzzy scope.
- **Trivial**: incorrect grammar, awkward wording, markdown formatting violations, minor disagreement.

----

## Artifact

Write the review to `design-review--{N}.md` in the same directory as the design plan. Read
`.agents/artifacts/design-review/description.md` for the canonical section definitions, and render
`.agents/artifacts/design-review/template.md.j2` to produce the initial file. Replace all dummy
content — every line drawn from the retro encabulator — with real content for this review. The
rendered file must contain no placeholder text when submitted. Supply the path to your caller on completion.
