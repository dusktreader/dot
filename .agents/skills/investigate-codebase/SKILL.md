---
name: investigate-codebase
description: Instructions for investigating a codebase to answer a specific question.
---

# Investigate Codebase Skill

Read a specific investigation question, explore the codebase to answer it, and report findings to your caller.


## When to use

Use this skill when you need to answer a specific, bounded question about an existing codebase —
root cause of a bug, how a subsystem works, blast radius of a change, etc.

This skill is a sub-skill called by orchestrators. It is used by:
- `run-bug-fix` — to confirm root cause before planning a fix
- `run-hotfix` — to quickly locate a bug's root cause
- `run-architecture-audit` — to gather raw findings before synthesis
- `run-implementation` — when the principal needs targeted codebase context

Do not confuse with `review-code`, which reviews code quality rather than answering a question.


## Prerequisites

1. **Confirm you have a question.** If no question was provided, stop and ask for one. No guessing.
2. **Load any relevant project skills** that provide context about the codebase under investigation.


## Scope

- Read only. Do not edit files, run commands that modify state, or write new files.
- Stay focused on the question. Do not produce a general survey of the codebase unless that is the question.
- Do not propose improvements or alternative approaches unless asked.


## Process


### 1. Understand the question

Restate the question in your own words. If the question is ambiguous, stop and ask for clarification before
proceeding.


### 2. Identify entry points

Identify the most relevant files, modules, classes, functions, and tests related to the question. Cast a wide
net at this stage — it is better to read too much than to miss a relevant path.


### 3. Explore systematically

Follow imports, trace call chains, read tests, and check documentation. Continue until you have enough evidence
to answer the question or have exhausted the relevant surface area.


### 4. Gather and label evidence

Collect specific locations using `file:line` references. For each piece of evidence, decide whether it is an
observation (directly seen in the code) or an inference (a conclusion drawn from observations).


### 5. Report findings

Compose a structured report using the sections defined in `.agents/artifacts/investigation-report/description.md`
as a guide. Omit `## Open Questions` if there are none. Report findings directly to your caller; do not write a file
artifact.
