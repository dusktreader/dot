---
name: execute-implementation-task
description: Instructions for executing a task from an implementation plans. Use when specifically requested.
---

# Execute Implementation Task Skill

Read the provided implementation plan artifact and find the task you were assigned in the document.
Execute the task to completion and report results back to your caller.


## Prerequisites

Your prompt must include:

- Path to the implementation plan
- The task identifier (number or name, e.g. `task-03`)

If either is missing, ask before proceeding. Do not guess.


## Scope

The work is complete after the task is fully executed such that the acceptance criteria are fully met.

All code that is produced must have unit test coverage. If a section should not be tested (generic
setup/boilerplate) or cannot be directly tested (external calls that would be onerous to mock), exclude it
via inline exclusion markers for the coverage tool. 100% coverage for all new or modified code should be
the goal.

You are writing code, not providing commentary on the plan artifact. If you have doubts about the plan, you
should report that feedback to the caller before you start executing the task. Do NOT modify ANY planning
documents.


## Process

Follow these steps during execution:


### 1. Understand the task

- Read the complete implementation plan document.
- Re-read the task you were assigned:
  - Make sure the steps you need to take are clear to you.
  - Pay close attention to the acceptance criteria.
- Read the corresponding design plan document.
- Review the project commands. If they are missing from the plan, STOP and report back.


### 2. Execute the task

- Follow Test-driven design:
  - Write the failing test.
  - Run it and verify it fails.
  - Implement the code.
  - Run the test and verify that it passes.
- Document as needed.
- Run linters and type checks for the code you wrote.


### 3. Report back

Report back to your caller. You must include the following:

- **Status**: "Complete" or "Incomplete" and an explanation of why the status was selected
- **Overview**: brief summary of the work performed to execute the task
- **Steps taken**: for each step, a description of what was done
- **Files modified**: for each modified file, whether it was created, updated, or deleted and the filename
- **Acceptance criteria validation**: for each AC:
  - **Status**: Satisfied or Unsatisfied
  - **Evidence or Explanation**: either evidence of satisfaction or explanation for unsatisfaction
- **Additional notes**: any other important context including challenges, ambiguities, or surprises
