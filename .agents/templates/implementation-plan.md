# Implementation Plan: {{ Title }}


## Goal

{{
  Describe at a high-level in 1 or 2 paragraphs WHAT the plan is building and its approach.
}}


## Project Commands

<!--
  Identify exact commands implementers and reviewers will use to:

  - Build
  - Test
  - Run
  - Check quality (test, lint, type-check, etc)

  Add one h3 subsection per command using the structure below.
-->

### {{ Short Description }}

Prerequisites:

<!-- List prerequisites, one per line, or remove this section if none. -->
- {{ Name }}: {{ link to setup doc }}

Command:

```
{{ Command }}
```

Expected Output:

{{ Describe output or show a sample }}


## Project Standards

<!-- This section prevents implementation plans from violating project-specific expectations. -->

{{
  Provide links to all relevant standard documents or configuration files that define them.
}}


## Relevant Skills

{{
  List all relevant agent skills both local to the project and general.
}}


## Execution

<!--
  This section enumerates the tasks that should be completed to execute on this implementation plan.

  Add one h3 subsection per task using the structure below.
-->

### {{ task-number (2 digit) }}: {{ task-name }}

{{ Short summary of the task }}


#### Acceptance Criteria

{{
  Identify clear criteria of success for the task.

  This should be a bulleted list.

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

  Each AC must be observable and testable. AC will be directly used to create tests for the task.

  Good AC look like:
  - AC13: GET /users returns 200 with [] when no users exist

  Bad AC look like:
  - The API works as expected
}}


#### Steps

{{
  Define concise, sequential steps to take in order to complete the task.

  For functionality tasks, steps might look like:

  - Write the failing test
  - Run the test to make sure it fails
  - Implement the minimal code to make the test pass
  - Run the test to make sure it passes

  For infrastructure tasks, steps might look like:

  - Create the config file
  - Run the build to ensure it works
  - Clean up build artifacts
}}

----


## Unknowns

{{
  List ambiguities that need to be resolved before implementation.

  For small projects, this may be a bulleted list. For larger projects, this will be a set of h3 subsections.

  Each question should be clear and specific. It should be answerable with a direct, specific conclusion.

  These will be marked as "RESOLVED" with an outcome during the implementation plan review.
}}


## Technical Notes

{{
  Enumerate any additional technical notes that are important for the implementation. This might include code
  snippets and implementation details. Go as deep as necessary to be clear. Use links and line numbers to add clarity
  as necessary.

  For small projects, this may be a bulleted list. For larger projects, this will be a set of h3 subsections.
}}
