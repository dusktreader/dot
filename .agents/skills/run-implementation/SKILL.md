---
name: run-implementation
description: Orchestrates the full implementation workflow from feature description to reviewed code.
---

# Run Implementation Skill

Coordinate the full implementation workflow: design, implementation planning, execution, and review.


## Prerequisites

Your prompt must include:

- Feature description or business requirements to implement

If not provided, ask before proceeding. Do not guess.


## Project directory

Before starting, derive a `{project-name}` from the feature description:

- Kebab-case, lowercase, no special characters except hyphens
- Short and descriptive (under 50 characters)
- Examples: `add-user-authentication`, `refactor-payment-module`

Create `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`. All artifacts for this project are stored there.

| Artifact                                  | Description                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| `design-plan.md`                          | Design plan                                                                                |
| `design-review--{N}.md`                   | Design plan review (N = zero-padded 2 digits: 01, 02, ...)                                 |
| `implementation-plan.md`                  | Implementation plan                                                                        |
| `implementation-review--{N}.md`           | Implementation plan review (N = zero-padded 2 digits: 01, 02, ...)                         |
| `implementation-journal.md`               | Execution journal                                                                          |
| `execution-review--{scope-id}--{N}.md`    | Execution review (scope-id = task-NN or whole-plan; N = zero-padded 2 digits: 01, 02, ...) |



## Process

### 1. Design

Dispatch an `architect-planner` subagent with the `create-design-plan` skill, the feature description,
and the project directory.

Then dispatch an `architect-reviewer` subagent with the `review-design-plan` skill, the design plan path,
and iteration `01`.

**Stop.** Present the design plan and its review to the human. Apply trivial findings directly. Discuss
significant and critical findings. Re-dispatch an `architect-reviewer` with `review-design-plan` at N+1
until the design plan is approved.


### 2. Plan

Dispatch an `engineer-planner` subagent with the `create-implementation-plan` skill and the design plan
path.

Then dispatch an `architect-reviewer` subagent with the `review-implementation-plan` skill, the
implementation plan path, and iteration `01`.

**Stop.** Present the implementation plan and its review to the human. Apply trivial findings directly.
Discuss significant and critical findings. Re-dispatch an `architect-reviewer` with
`review-implementation-plan` at N+1 until the implementation plan is approved.


### 3. Execute

Dispatch an `engineer-executor` subagent with the `execute-implementation-plan` skill and the
implementation plan path.

Then dispatch an `engineer-reviewer` subagent with the `review-implementation-execution` skill, the
journal path, scope `whole-plan`, and iteration `01`.

**Stop.** Present the execution review to the human. Dispatch an `engineer-executor` to fix Critical and
Significant findings, then re-dispatch an `engineer-reviewer` with `review-implementation-execution` at
N+1 until the execution is approved.


### 4. Report

Report completion to the human with the project directory path and the final status of each artifact.
