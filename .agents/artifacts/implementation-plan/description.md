# Implementation Plan

An implementation plan translates an approved design plan into a concrete, step-by-step
execution guide. Where a design plan answers WHAT and WHY, an implementation plan answers HOW.
It names specific files, modules, functions, and parameters. It defines tests at multiple levels.


## Template Variables

| Variable  | Description                                          |
| --------- | ---------------------------------------------------- |
| `title`   | Short descriptive title for the implementation plan  |


## Sections


### Goal

One or two paragraphs describing what the plan is building and its approach. Derived from the
design plan's Goal but may be more specific about implementation choices.


### Project Commands

Exact commands implementers and reviewers will use to build, test, run, and check quality.
One `### ` subsection per command.

Each subsection contains:
- **Prerequisites**: named dependencies with links to setup docs. Omit if none.
- **Command**: the exact shell command in a fenced code block.
- **Expected Output**: a description or representative sample of what success looks like.


### Project Standards

Links to all standard documents or configuration files that govern this implementation.
Prevents plans from violating project-specific expectations.


### Relevant Skills

All agent skills relevant to executing this plan — both project-local and global. Lists only
skills that actually exist; hallucinated skill names are a Critical finding in plan review.


### Execution

The ordered list of tasks to complete. One `### ` subsection per task, numbered with a
two-digit prefix (e.g. `### 01: task-name`).

Each task contains:

#### Acceptance Criteria

Testable criteria for the task. Numbered `AC01`, `AC02`, etc. within the task.

Covers happy path, variations, edge cases, and relevant failure modes. Each AC must be
observable and directly verifiable in code or output.

Good AC: `AC01`: `GET /users` returns 200 with `[]` when no users exist
Bad AC: The API works as expected

#### Steps

Concise, sequential steps to complete the task. Steps for functionality tasks follow
test-driven design: write the failing test → run it → implement → run it again. Steps for
infrastructure tasks are literal shell or file operations.

#### Technical Notes

Optional. Implementation notes, code snippets, or references specific to this task. Omit
if there is nothing task-specific to note.


### Unknowns

Ambiguities that must be resolved before execution begins. Each is a specific, answerable
question. Resolved during plan review and marked with their outcome.


### Technical Notes

Additional technical context for the implementation: code patterns, API details, constraints.
May include code snippets. Use `### ` subsections for larger projects.
