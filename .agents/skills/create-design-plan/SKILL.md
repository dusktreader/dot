---
name: design-plans
description: Instructions for writing good design plan artifacts. Use when specifically requested.
---

# Create Design Plan Skill

Based on business requirements, create a design plan artifact.


## When to use

Use this skill to produce a design plan artifact from business requirements or a feature
description. It is always the first artifact stage in the `run-implementation` workflow.

This skill is a sub-skill called by orchestrators:
- `run-implementation` — stage 1 (design)

Do not use this skill to write implementation plans, fix plans, or any code. The output is a
design plan only. Do not confuse with `create-implementation-plan`, which translates a design
plan into executable steps.


## Prerequisites

Your prompt must include:

- Business requirements or a description of the feature to design
- Path to the project directory where the artifact will be written

If not provided, ask before proceeding. Do not guess.


## Overview

Design plans describe requirements for a feature, a refactor, a new project, etc. They are not
implementation plans. Design plans describe WHAT will be built and WHY. They do not describe HOW
to build it.

The single most important rule: **a design plan must not contain implementation details.** If you
find yourself writing a file path, a function name, a parameter name, a configuration key, or
anything that presupposes a specific implementation, stop and reframe it as a behavior or
outcome instead. Those details belong in the implementation plan.

The line between design and implementation:

| Design plan (correct)                              | Implementation plan (not here)                        |
| -------------------------------------------------- | ----------------------------------------------------- |
| The UI fetches runtime config at startup           | `config.ts` calls `fetch('/config.json')` on load     |
| The release pipeline verifies images before deploy | `verify-images/action.yml` accepts a `sha` input      |
| Terraform applies are manually triggered only      | `terraform-dev.yml` uses `on: workflow_dispatch`      |
| The bundle is built once and promoted unchanged    | `release.yml` uploads `ui/dist/` as a workflow artifact |

Implementation plans follow design plans. Those documents explain the HOW.

**The plan MUST conform to the structure defined in the template!** Plans that deviate will be
flagged by the plan reviewer with Critical Findings.


## Scope

The work is complete after the design plan is created. The work does not include writing the
implementation plan. The work should never include creation or modification of product code.


## Structure

Read `.agents/artifacts/design-plan/description.md` for the canonical definition of each
section — what belongs there, what good looks like, and what is explicitly excluded.

Use `.agents/artifacts/design-plan/template.md.j2` as the structural stub. A good design plan is
succinct and clear. It can be consumed by agents and humans alike to understand the scope and
goals of the project. A reviewer should be able to approve or reject the direction without
needing to know how any of it will be implemented.


## Artifact

Write the design plan to `{project-dir}/design-plan.md`. Supply the path to your caller on
completion.

Render `.agents/artifacts/design-plan/template.md.j2` to produce the initial file. Replace
all dummy content — every line drawn from the retro encabulator — with real content for this
project. The rendered file must contain no placeholder text when submitted.

Before writing, read and follow `~/.agents/instructions/markdown.md`. All heading spacing,
list formatting, line length, and code fence rules apply to every plan artifact.
