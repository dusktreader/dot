---
name: create-epic-plan
description: Create a product-level epic plan for a multi-feature initiative.
---

# Create Epic Plan Skill

Create an epic plan from product outcomes or business requirements. The artifact
owns initiative scope, feature identities, the MVP boundary, and roadmap briefs.


## When to use

Use this skill to frame a new project or substantial product expansion that requires multiple
independently deliverable features. A single cohesive deliverable belongs in `run-feature`.

This skill may be invoked by `run-epic` or specifically requested for epic-plan authoring. It creates the epic artifact
only. It does not create child design plans, implementation plans, code, reviews, or a feature lifecycle.


## Prerequisites

The prompt must include:

- Product outcome, business requirements, or an initiative description
- Epic artifact directory
- Repository context when the work affects an existing project

If essential information is missing, ask focused questions before writing. Do not
invent product decisions. Record unresolved decisions as answerable Unknowns.


## Process

1. Read and follow `~/.agents/instructions/markdown.md`.
2. When the epic extends an existing repository, inspect its structure, current behavior,
   standards, and relevant product documentation before proposing features.
3. Decompose the outcome into features that each have an independently meaningful user or product outcome. Give
   each a stable, zero-padded `FNN` identifier and record dependencies and ordering.
4. Define the smallest useful MVP as slice `T01`. Keep features outside the MVP
   as concise post-MVP briefs; do not create speculative detailed designs.
5. Record product-level success criteria, scope, non-goals, cross-cutting decisions, risks, dependencies, unknowns, and
   closure criteria. Keep feature design and implementation detail out of the epic plan.
6. Use one epic directory at `.artifacts/{YYYYMMDD}--{epic-name}/`. Put the plan at `epic-plan.md`. Use a separate
   directory for each feature: `.artifacts/{YYYYMMDD}--{epic-name}--FNN-{feature-name}/`.
7. Read `.agents/artifacts/epic-plan/description.md` and render `.agents/artifacts/epic-plan/template.md.j2` as the
   initial artifact. Replace every example and template variable with project-specific content.
8. Run `dt format markdown` on `epic-plan.md` and verify the artifact contains no placeholder text.


## Artifact

Write only `epic-plan.md` in the supplied epic artifact directory. Identify the complete path on completion. Every MVP
feature must receive a complete, individually reviewed design plan, and the complete T01 design set must receive
explicit human approval before implementation planning or code begins.
These are later workflow gates, not artifacts produced by this skill.
