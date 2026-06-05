---
name: execute-implementation-plan
description: Instructions for executing implementation plans. Use when specifically requested.
---

# Execute Implementation Plan Skill

Read the provided implementation plan artifact and coordinate its execution. Record progress in an
implementation journal.


## Prerequisites

Your prompt must include:

- Path to the implementation plan

If not provided, ask before proceeding. Do not guess.


## Artifact

Write the journal to `{project-dir}/implementation-journal.md`, where `{project-dir}` is the directory
containing the implementation plan. Use `.agents/templates/implementation-journal.md` as the template.
Supply the path to your caller on completion.


## Relevant Skills

Load all relevant skills before executing the plan following these guidelines:

- Project-local skills (in the working tree) ALWAYS take precedence over global skills covering the same topic.
- Search available skills by category, not by one hardcoded name.
- Filter skills by relevance to the project; skills oriented around quality should always be included if relevant.
- If project docs or skills define stricter standards than nearby existing artifacts, the stricter standards win.
  Do not preserve weak local patterns just because they exist.

You especially need relevant testing and quality-assurance skills loaded as you will need to run these checks
throughout the execution process to ensure quality is maintained.


## Scope

The work is complete after the implementation plan is fully executed.

Each listed task must be completed such that the acceptance criteria are fully met.

All code that is produced must have unit test coverage. If a section should not be tested (generic
setup/boilerplate) or cannot be directly tested (external calls that would be onerous to mock), exclude it
via inline exclusion markers for the coverage tool. 100% coverage for all new or modified code should be
the goal.

You are writing code, not providing commentary on the plan artifact. If you have doubts about the plan, you
should report that feedback to the caller before you start executing the task. Do NOT modify ANY planning
documents.


## Process

Follow these steps during execution:


### 1. Understand the plan

- Read the complete implementation plan document.
- Read the corresponding design plan document.
- Review the project commands. If they are missing from the plan, STOP and report back.
- Load the relevant skills.


### 2. Choose execution mode

If the plan involves many tasks (use judgement, but more than 5 could be considered "many"), orchestrate
subagents to execute each task independently. We will refer to this as "team" mode.

If the plan does not qualify for "team" mode, execute the steps yourself. We will refer to this as
"solo" mode.


### 3.A Execute the plan in "team" mode

- Progress through the tasks one by one. For each:
  - Dispatch an `engineer-executor` subagent to perform the task.
  - Review the results from each subagent.
  - If the results do not satisfy the acceptance criteria, dispatch another subagent to fix the issue.
  - Write a journal entry describing the process and results as reported by the subagent.


### 3.B Execute the plan in "solo" mode

- Progress through the tasks one by one. For each:
  - Carefully read the task, paying close attention to the acceptance criteria.
  - Follow Test-driven design:
    - Write the failing test.
    - Run it and verify it fails.
    - Implement the code.
    - Run the test and verify that it passes.
  - Document as needed.
  - Run linters and type checks for the code you wrote.
  - Write a journal entry describing the process and results.


### 4. Report back

Report back to the orchestrator. Summarize results and outline challenges, ambiguities, or surprises.
