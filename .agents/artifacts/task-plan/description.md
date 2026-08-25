# Task plan

A task plan is a focused, principal-authored guide for a minor engineering task. It answers HOW without requiring a
prior design plan. Use it when the change is well-understood and scoped — a small feature, refactor, cleanup,
configuration change, or documentation update.

A task plan is intentionally lighter than a full implementation plan: it omits the `Relevant Skills` section and
replaces the multi-task `Execution` section with a single flat task. If the work naturally decomposes into two or
three independent tasks, each may be listed as its own subsection, but the plan should never grow to the point where
a full implementation plan would be more appropriate.


## Template variables

| Variable | Description                                      |
| -------- | ------------------------------------------------ |
| `title`  | Short descriptive title for the task (≤ 8 words) |


## Sections

### Goal

One paragraph describing what the task accomplishes and why. Be specific about the scope of the change and what is
explicitly out of scope.


### Project commands

Exact commands needed to build, test, and verify the change. One `### ` subsection per command, each containing:

- **Command**: the exact shell command in a fenced code block
- **Expected output**: a description or representative sample of what success looks like
- **Prerequisites**: named dependencies with links to setup docs — omit if none


### Project standards

Links to all standard documents or configuration files that govern this task. Omit if there are none relevant to
the change.


### Steps

A single flat ordered list of steps to complete the task. Steps should be concise and actionable. For code changes,
follow test-driven design: write the failing test, run it, implement, run it again. For non-code tasks (config,
docs), steps are literal file or shell operations.

If the work has two or three genuinely independent sub-tasks, each may be a `### ` subsection with its own steps
list. Do not split a single coherent change across sub-tasks.


### Acceptance criteria

Testable, observable criteria confirming the task is done. Numbered `AC01`, `AC02`, etc. Each criterion must be
verifiable in code or output — not a description of intent.

Good: `AC01`: `GET /users` returns `200` with `[]` when no users exist
Bad: The API works as expected


### Technical notes

Optional. Implementation notes, code snippets, caveats, or references specific to this task. Omit if there is
nothing task-specific to note.
