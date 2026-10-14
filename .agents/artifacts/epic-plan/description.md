# Epic plan

An epic plan is the durable product-level record for a multi-feature initiative. It owns the overall outcome, feature
register, MVP boundary, and roadmap progression while linking to detailed feature-specific artifacts.


## Template variables

| Variable     | Description                                     |
| ------------ | ----------------------------------------------- |
| `epic_title` | Short descriptive name for the initiative       |
| `epic_id`    | Stable epic identifier when the project has one |
| `date`       | Date used in the epic artifact directory        |


## Sections

### Goal

Describe the product or business outcome and who benefits. Keep
the statement understandable without child feature artifacts.


### Scope and non-goals

Define the initiative boundary, what the work includes, and explicit exclusions. Keep
child feature implementation specifications in their own artifact directories.


### Success criteria

List measurable product-level outcomes used to assess the integrated
product and each slice. State how each criterion will be verified.


### Architecture and cross-cutting decisions

Record product-level architecture and cross-feature decisions that constrain decomposition
or integration. Do not embed child feature designs or implementation plans.


### Feature register

Give every feature a stable, zero-padded `FNN` identifier. Each row records its outcome, slice, priority,
dependencies, state, and link to its separate identifier-bearing
artifact directory. Do not use branch names as feature identity.


### Slice register

Record `T01` as the MVP and each approved later delivery slice as `T02`, `T03`, and so on. For each slice record its
objective, included features, prerequisite slices, state, verification result, artifact links, coordinator-owned
regular branch, and coordinator-owned worktree. A later slice starts only from the accepted integrated product state
of every prerequisite slice. If the baseline is not accepted, keep the slice blocked.


### T01 MVP plan

State the minimum useful release boundary, objective, included `FNN` features, feature dependencies, and the success
criteria that define acceptance. Every committed MVP feature requires a complete, individually reviewed design plan
before implementation planning or code begins. Present the complete design
set for explicit human approval before starting implementation planning.


### Post-MVP roadmap briefs

Keep deferred features as concise outcome briefs until the human approves a delivery slice. Do not create speculative
child design or implementation artifacts. Record the proposed priority, dependencies,
and expected value needed to make a later slice decision.


### Dependencies

Describe product-level, external, and cross-slice dependencies.
Link dependencies to affected feature and slice identifiers.


### Risks

Record risks that could affect outcome, scope, sequencing, integration, or acceptance, with mitigation and ownership.


### Unknowns

List unresolved product decisions as specific, answerable questions. Resolve
them one at a time before approving the epic plan or a slice design set.


### Closure criteria

Define the conditions for accepting a slice, closing the epic, and making a roadmap decision. Each slice requires
individual feature verification, integrated verification against its success criteria, and explicit human acceptance.


## Artifact topology

Store an epic at `.artifacts/{YYYYMMDD}--{epic-name}/epic-plan.md`. Store each feature's detailed artifacts separately
at `.artifacts/{YYYYMMDD}--{epic-name}--FNN-{feature-name}/`. Repeat the `FNN` identifier in the feature plan title,
review title, journal, relevant metadata, and epic register. Keep feature designs, implementation
plans, reviews, journals, deviations, and QA records in the feature directory.
