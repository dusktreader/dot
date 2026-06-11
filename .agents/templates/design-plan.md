# Design Plan: {{ Title }}


## Goal

{{
  Describe at a high-level in 1 or 2 paragraphs WHAT the plan is building and its approach.
}}


## Acceptance Criteria

{{
  Identify observable, testable criteria for success. Each AC describes a system behavior or
  outcome — not a file, class, function, or parameter. If an AC names a specific file or
  implementation detail, it belongs in the implementation plan, not here.

  Use a flat bulleted list only when ALL of the following are true:
  - There are 5 or fewer items
  - Every item fits on a single line (no wrapping)

  Otherwise, use h3 subsections to group related ACs, with each individual AC as an h4 heading
  of the form `#### AC{N}: Brief title` followed by its description as a short paragraph. Do not
  use bullets when items wrap.

  Each AC should be numbered as `AC{N}` where N is a 2 digit number.

  Each AC should either describe a successful outcome or a failure mode:

  Success cases include one or more of each:
  - **"Happy path"**: the most common use-case
  - **Variation**: common use-cases outside the "happy path"
  - **Edge-case**: boundary condition like minimal or maximal valid set

  Failure modes include:
  - Invalid input handling
  - Invalid auth
  - Resource exhaustion
  - External dependency failure

  Each AC must be observable and testable. AC will be directly used to define tests for the implementation.

  Good AC look like:
  - API returns 401 when token is expired
  - User sees error message when password is less than 8 characters
  - System processes 100 concurrent requests within 2 seconds
  - The XYZ dependency is updated to its latest version

  Bad AC look like:
  - System is secure (vague)
  - Code is clean (subjective)
  - Performance is acceptable (unmeasurable)
  - `foo/bar.ts` exports a `createFoo()` function (implementation detail — belongs in the impl plan)
}}


## Architecture

{{
  Succinctly describe the structure of the project at a conceptual level.

  Name components, subsystems, and the relationships between them. Describe data flow, control
  flow, and key design decisions. Include diagrams when it is useful to visualize how components
  are connected.

  Do NOT name specific files, classes, functions, parameters, or configuration keys. Those are
  implementation details and belong in the implementation plan. If you find yourself writing a
  file path or a function signature, stop — reframe it as a component responsibility instead.
}}


## Unknowns

{{
  List ambiguities that need to be resolved before implementation.

  Use a flat bulleted list only when there are 5 or fewer items and each fits on a single line.
  Otherwise, use h3 subsections — one per unknown.

  Each question should be clear and specific. It should be answerable with a direct, specific conclusion.

  These will be marked as "RESOLVED" with an outcome during the design plan review.
}}


## Technical Notes

{{
  Enumerate any additional technical notes that are important for the implementation. This should
  not include code snippets or implementation details. However, it could go deeper into design
  patterns, communication protocols, or concurrency models.

  Use a flat bulleted list only when there are 5 or fewer items and each fits on a single line.
  Otherwise, use h3 subsections — one per note.
}}
