---
name: review-implementation-plan
description: Instructions for reviewing implementation plans artifacts. Use when specifically requested.
---

# Review Implementation Plan Skill

Read the provided implementation plan artifact and critique it in a structured review artifact.


## Prerequisites

Your prompt must include:

- Path to the implementation plan
- Iteration number (N = 01 for first review, 02+ for re-reviews)
- For re-reviews: path to the prior review artifact

If not provided, ask before proceeding. Do not guess.


## Scope

- You are reviewing an **implementation plan** artifact. Not code.
- Do NOT run tests, builds, or linters.
- Do NOT modify the document.
- You MAY use read-only project skills for wider context.


## Steps

Track your progress through these steps:


### 0. Setup

Load the `create-implementation-plan` skill to understand the expected artifact structure. Load any other
relevant skills for context. Locate the design plan referenced in the implementation plan for higher-level
context.


### 1. Resolve prior findings (re-review only)

If a prior review artifact is provided, read it completely. For each prior finding, check whether the
implementation plan has been updated to address it:

- ✓ Fully resolved — note the change in the plan
- ⚠ Partially resolved — explain what remains
- ✗ Not resolved — carry this forward as a Critical finding in the current review


### 2. Evaluate structural completeness

The document MUST match the `.agents/templates/implementation-plan.md` template.

Call out missing sections, incomplete information, violations of scope, or deviation from the template.


### 3. Find missing standards

Review the `## Project Standards` section. Ensure that all relevant standards are enumerated. Flag missing or
hallucinated standards.


### 4. Check agent skills

Review the `## Relevant Skills` section. Ensure that all relevant skills are enumerated. Flag missing or
hallucinated skills.


### 5. Evaluate execution tasks

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

### 6. Ensure unknowns relevance

Ensure that the listed ambiguities are legitimate. Call out noise in this section. Make sure there is a clear
resolution possible for each item. Call out any missing ambiguities that need to be addressed.


### 7. Categorize findings

Each finding should be given a severity level:

- **Critical**: structure violation (missing/extra sections), untestable ACs, hallucinated project elements.
- **Significant**: missing modes in AC, ambiguity that would block implementation, fuzzy scope.
- **Trivial**: incorrect grammar, awkward wording, organizational improvements, minor disagreement.

----

## Artifact

Write the review to `implementation-review--{N}.md` in the same directory as the implementation plan. Use
`.agents/templates/implementation-review.md` as the template. Supply the path to your caller on completion.
