# Epic review

An epic review records an adversarial assessment of an `epic-plan.md` against product decomposition,
MVP readiness, roadmap, dependency, and artifact-boundary requirements.


## Template variables

| Variable    | Description                         |
| ----------- | ----------------------------------- |
| `epic_id`   | Epic identifier when one exists     |
| `iteration` | Zero-padded review number           |
| `epic_plan` | Path to the reviewed `epic-plan.md` |
| `reviewer`  | Reviewer role or identity           |
| `date`      | Review date                         |


## Sections

### Source artifact

Identify the exact epic plan path and review iteration. Record the epic and feature-set
revision reviewed so later reviews can establish whether the source changed.


### Outcome

Choose `Approved` only when no unresolved material findings block the epic plan. Otherwise choose
`Changes required`. State whether the plan can proceed to its human approval gate.


### Findings

Record findings with unique identifiers, severity (`Critical`, `Significant`, or `Minor`), source location, evidence,
impact, and a concrete resolution. Cover outcome clarity, scope and non-goals, success and closure criteria, MVP
minimality, feature boundaries and independent deliverability, `FNN`/`TNN` consistency, dependencies and sequencing,
cross-cutting decisions, deferred-scope clarity, slice baseline and verification
gates, and separation from feature-level implementation detail.


### Prior-review resolution

For a re-review, link the prior review and record each prior finding as resolved, unresolved, or
regressed with evidence. For an initial review, state that no prior review applies.


## Review contract

Name reviews `epic-review--NN.md` in the epic artifact directory, using a zero-padded sequence beginning at `01`. Do not
edit the epic plan during review. Return findings to the plan author for disposition. Re-review material changes and
record prior finding resolution. An approved review does not replace explicit human approval of the epic plan.
