# Epic deviation

An epic deviation records a post-plan feature change that affects initiative or slice scope, dependencies, sequencing,
success criteria, integration, or another feature. It assesses product-level impact and governs pauses and renewed
approvals for unfinished dependent work.


## Template variables

| Variable      | Description                                |
| ------------- | ------------------------------------------ |
| `epic_title`  | Epic name or identifier                    |
| `sequence`    | Zero-padded deviation number               |
| `epic_plan`   | Path to the governing `epic-plan.md`       |
| `slice_id`    | Affected slice, such as `T01`              |
| `feature_ids` | Affected stable feature IDs, such as `F01` |
| `date`        | Date of the deviation record               |


## Sections

### Source and departure

Identify the epic plan, slice, affected feature IDs, linked feature deviation journals, and the human-approved request.
Identify the approved plan or acceptance criterion affected and whether the change follows or departs from it.


### Product-level impact

Assess effects on the epic outcome, scope, MVP or slice boundary, success criteria, feature dependencies, sequencing,
integration, and any other feature. Link affected feature and slice IDs rather than duplicating their detailed plans.


### Work decision

Record whether affected unfinished work pauses or continues, which dependencies are blocked, and the justification. Do
not resume paused work until the impact assessment is complete and required approval has been renewed.


### Approval requirements

State whether the epic plan, slice design set, or another human approval must be renewed. Record the approval evidence
and the exact approved revision before dependent work resumes.


### Verification

List feature-level and integrated verification needed to establish the changed outcome. Record each result and human
acceptance decision, linking to feature `plan-deviations.md` entries where relevant. An unverified or failed criterion
keeps the affected slice and dependent slices blocked.


## Record contract

Store each record as `epic-deviation--NN.md` in the epic artifact directory using a zero-padded sequence. Link the
record from `epic-plan.md`. Feature-specific changes remain in the corresponding feature `plan-deviations.md`; the epic
record links those journals and captures only cross-feature product impact and coordination decisions.
