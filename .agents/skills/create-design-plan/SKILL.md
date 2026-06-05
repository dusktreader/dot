---
name: design-plans
description: Instructions for writing good design plan artifacts. Use when specifically requested.
---

# Create Design Plan Skill

Based on business requirements, create a design plan artifact.


## Prerequisites

Your prompt must include:

- Business requirements or a description of the feature to design
- Path to the project directory where the artifact will be written

If not provided, ask before proceeding. Do not guess.


## Overview

Design plans describe requirements for a feature, a refactor, a new project, etc. They are not implementation plans.
Design plans describe WHAT will be executed. They do not describe specifics of HOW to execute.

Implementation plans follow design plans. Those documents explain the HOW.

Design plans should be architecture-level documents.

**The plan MUST conform to the structure defined in the template!** Plans that deviate will be flagged by the
plan reviewer with Critical Findings. Avoid that embarrassment by making sure your plan is conformant.


## Relevant Skills

Load all relevant skills before writing the plan following these guidelines:

- Project-local skills (in the working tree) ALWAYS take precedence over global skills covering the same topic.
- Search available skills by category, not by one hardcoded name.
- Filter skills py relevance to the project; skills oriented around quality should always be included if relevant.
- If project docs or skills define stricter standards than nearby existing artifacts, the stricter standards win.
  Do not preserve weak local patterns just because they exist.

You especially need relevant testing skills loaded when writing per-task Acceptance Criteria, because each AC will be
tied to a test that satisfies it.


## Scope

The work is complete after the design plan is created. The work does not include writing the implementation plan. The
work should never include creation or modification of product code.


## Structure

Use `.agents/templates/design-plan.md` as a guide for the artifact structure. Each area that should be filled in during
the construction of the plan artifact is indicated with double curly braces.

A good design plan is succinct and clear. It can be consumed by agents and humans alike to understand the scope of the
project and specific deliverables.


## Artifact

Write the design plan to `{project-dir}/design-plan.md`. Supply the path to your caller on completion.
