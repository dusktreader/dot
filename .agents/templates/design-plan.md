# Design Plan: {{ Title }}


## Goal

{{
  Describe at a high-level in 1 or 2 paragraphs WHAT the plan is building and its approach.
}}


## Acceptance Criteria

{{
  Identify clear criteria of success for the project.

  For small projects, this may be a bulleted list. For larger projects, this will be a set of h3 subsections.

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
}}


## Architecture

{{
  Succinctly describe the structure of the project.

  This should include components, modules, types, patterns, etc.

  Include diagrams when it is useful to visualize how components are connected.

  Do not describe specific changes to files, code snippets, etc. Those are implementation details.
}}


## Unknowns

{{
  List ambiguities that need to be resolved before implementation.

  For small projects, this may be a bulleted list. For larger projects, this will be a set of h3 subsections.

  Each question should be clear and specific. It should be answerable with a direct, specific conclusion.

  These will be marked as "RESOLVED" with an outcome during the design plan review.
}}


## Technical Notes

{{
  Enumerate any additional technical notes that are important for the implementation. This should not include code
  snippets or implementation details. However, it could go deeper into design patterns, communication protocols, or
  concurrency models.

  For small projects, this mayb be a bulleted list. For larger projects, this will be a set of h3 subsections.
}}
