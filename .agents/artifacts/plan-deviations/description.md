# Plan deviations

A chronological journal of changes made after a plan is approved, covering implementation, code review, and QA. Record
whether each change follows or departs from the approved plan, and capture its source and verification.


## Template variables

| Variable                   | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| `plan_title`               | Task, feature, or fix plan title                     |
| `design_plan_path`         | Approved design plan path, or `None` if not relevant |
| `implementation_plan_path` | Approved implementation or task plan path            |


## Source plans

Record the approved source plan paths. These remain immutable and are the baseline for identifying deviations. Use
`None` for a design plan when the workflow has no design stage.


## Changes

Add one subsection per implemented change made after plan approval, in chronological order. Include implementation,
code-review, and QA changes, whether requested by the human or initiated by the implementor. State whether each change
departs from the approved plan. Record the source and omit unimplemented or declined requests.

Each change subsection contains:


### Stage and source

Record whether the change arose during implementation, code review, or QA, and identify who or what requested it.


### Request

Record the request or change trigger accurately. Do not infer intent or rationale.


### Plan alignment

Identify the affected task, acceptance criterion, or plan section. State whether the change follows or departs from the
approved plan; for added work, state that the plan does not cover it.


### Change made

Describe the resulting implementation change and list the files modified.


### Reason

Record the human-provided reason when available. State that no reason was provided rather than inventing one.


### Verification

Record focused tests, quality gates, or manual verification and their results.
