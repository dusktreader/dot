# Plan deviations

A chronological record of human-directed implementation changes that depart from the approved design or implementation
plans after execution begins.


## Template variables

| Variable                   | Description                              |
| -------------------------- | ---------------------------------------- |
| `plan_title`               | Title of the implementation plan         |
| `design_plan_path`         | Path to the approved design plan         |
| `implementation_plan_path` | Path to the approved implementation plan |


## Source plans

Record the paths to the approved design plan and implementation plan. These are the immutable baseline for identifying
deviations.


## Deviations

Add one subsection per implemented human-directed change that departs from the approved plans, in chronological order.
Do not record requests that were declined or changes that remain within the approved plan.

Each deviation subsection contains:


### Stage

Record whether the request arose during execution, human code review, or QA.


### Human feedback

Record the human's request or an accurate summary. Do not infer intent or rationale.


### Approved plan reference

Identify the affected task, acceptance criterion, or plan section. For added work, state that the approved plans do not
cover it.


### Change made

Describe the resulting implementation change and list the files modified.


### Reason

Record the human-provided reason when available. State that no reason was provided rather than inventing one.


### Verification

Record focused tests, quality gates, or manual verification and their results. Link to the QA journal entry for QA
deviations.
