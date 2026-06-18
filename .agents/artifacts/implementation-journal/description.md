# Implementation Journal

A running record of what was done during execution of an implementation plan. Written by the
implementer as they work, one section per task. Provides the evidence trail for execution review.


## Template Variables

| Variable     | Description                                              |
| ------------ | -------------------------------------------------------- |
| `plan_title` | Title of the implementation plan this journal covers     |


## Sections


### Source Plan

Path to the implementation plan artifact this journal covers.


### Status

Top-level completion status for the entire journal. Values: `Complete` or `Incomplete`,
followed by a brief explanation if incomplete.


### Tasks

One `### Task NN: name` subsection per task in the plan, in order.

Each task subsection contains:

#### Status

`Complete` or `Incomplete`, with a brief explanation if incomplete.

#### Overview

A brief summary of the work performed to execute the task. Enough context for a reviewer
to understand what was done without reading every step.

#### Steps Taken

A bulleted list of actions taken. One bullet per meaningful step. Matches the steps defined
in the plan but reflects what actually happened, including any deviations.

#### Files Modified

A bulleted list of every file touched during this task, prefixed with `CREATED`, `UPDATED`,
or `DELETED`. One entry per file. Reviewers use this list to scope their review.

#### Acceptance Criteria Validation

One `##### ` subsection per AC defined in the plan task. Each heading is prefixed with
`Satisfied` or `Unsatisfied`.

For satisfied ACs: provide concrete validation evidence — test name, output, or
`file:line` reference. For unsatisfied ACs: explain the failure.

#### Additional Notes

Any important context from the execution: challenges encountered, ambiguities resolved,
surprises, decisions made that deviated from the plan. Omit if there is nothing to add.
