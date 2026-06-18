---
name: create-implementation-plan
description: Instructions for writing good implementation plans artifacts. Use when specifically requested.
---

# Create Implementation Plan Skill

Read the provided design plan artifact and use it to produce an implementation plan artifact.


## When to use

Use this skill to translate an approved design plan into a step-by-step implementation plan.
It is always the second artifact stage in the `run-implementation` workflow, and is also used
in `run-bug-fix` (where a bug report takes the place of a design plan).

This skill is a sub-skill called by orchestrators:
- `run-implementation` — stage 2 (planning)
- `run-bug-fix` — planning stage
- `run-fix` — fix plan stage

Do not use this skill to write design plans or code. Do not confuse with `create-design-plan`,
which produces the higher-level artifact that this skill consumes.


## Prerequisites

Your prompt must include:

- Path to the design plan artifact to implement

If not provided, ask before proceeding. Do not guess.


## Overview

Implementation plans are lower-level artifacts that expand higher-level design plans into a more detailed, step-by-step
plan to execute the implementation.

Implementation plans describe the process to implement a feature, a refactor, a new project, etc. They are specific,
step-by-step instructions that produce complete, testable, and documented implementations. They should describe
specific code changes in particular files, modules, functions, etc. They should itemize tests to build at multiple
levels: unit, integration, end-to-end, etc.

The plan should break the process into succinct, concrete steps. The outcome of each step should be scoped and
verifiable.

Plans should be written assuming the implementor has little context for the project. You should assume the implementor
is a good engineer, but needs careful guidance in project standards, style, structure, and taste. Do not assume domain
expertise.

The plan artifact must operate within the project standards and structure. If the plan violates either, reviewers will
call it out and you will look bad. Have care.

**The plan MUST conform to the structure defined in the template!** Plans that deviate will be flagged by the
plan reviewer with Critical Findings. Avoid that embarrassment by making sure your plan is conformant.


## Scope

The work is complete after the implementation plan is created. The work does not include writing any code.


## Artifact

Write the implementation plan to `{project-dir}/implementation-plan.md`, where `{project-dir}` is the
directory containing the design plan. Read `.agents/artifacts/implementation-plan/description.md` for the
canonical section definitions, and render `.agents/artifacts/implementation-plan/template.md.j2` to produce
the initial file. Replace all dummy content — every line drawn from the retro encabulator — with real
content for this project. The rendered file must contain no placeholder text when submitted. Supply the
path to your caller on completion.

Before writing, read and follow `~/.agents/instructions/markdown.md`. All heading spacing,
list formatting, line length, and code fence rules apply to every plan artifact.
