# Design Plan

A design plan describes WHAT will be built and WHY. It does not describe HOW to build it.
Implementation details — file paths, function names, parameter names, configuration keys —
do not belong here. Those belong in the implementation plan.


## Template Variables

| Variable  | Description                                  |
| --------- | -------------------------------------------- |
| `title`   | Short descriptive title for the design plan  |


## Sections


### Goal

One or two paragraphs describing at a high level what the plan is building and its overall
approach. Should be understandable without reading anything else in the document.


### Acceptance Criteria

Observable, testable criteria for success. Each AC describes a system behavior or outcome —
not a file, class, function, or parameter.

Each AC is numbered `AC01`, `AC02`, etc.

Each AC describes either a successful outcome or a failure mode:

- **Success cases**: happy path (the most common use-case), variations (common cases outside
  the happy path), edge cases (boundary conditions like minimal or maximal valid input)
- **Failure modes**: invalid input handling, invalid auth, resource exhaustion, external
  dependency failure

**Formatting**: use a flat bulleted list only when there are 5 or fewer ACs and each fits on
a single line. Otherwise use `### ` subsections to group related ACs, with each individual AC
as an `#### AC{N}: Brief title` heading followed by a short paragraph.

Good AC:
- `AC01`: API returns 401 when the token is expired
- `AC02`: User sees an error message when the password is fewer than 8 characters
- `AC03`: System processes 100 concurrent requests within 2 seconds

Bad AC:
- System is secure (vague, not testable)
- Code is clean (subjective)
- Performance is acceptable (unmeasurable)
- `foo/bar.ts` exports a `createFoo()` function (implementation detail — belongs in the plan)


### Architecture

A conceptual description of the structure of the solution. Names components, subsystems,
and the relationships between them. Describes data flow, control flow, and key design
decisions. May include diagrams.

Does not name specific files, classes, functions, parameters, or configuration keys.


### Unknowns

Ambiguities that must be resolved before implementation can begin. Each unknown is a
specific, answerable question — not a vague concern.

**Formatting**: flat bulleted list for 5 or fewer short items; `### ` subsections for
anything larger.

Unknowns are resolved during design review and marked with their outcome.


### Technical Notes

Additional technical context relevant to the design: patterns, protocols, concurrency
models, external constraints. No code snippets or implementation-level detail.

**Formatting**: flat bulleted list for 5 or fewer short items; `### ` subsections otherwise.

Omit this section if there is nothing to add.
