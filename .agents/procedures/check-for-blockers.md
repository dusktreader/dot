# Check for Blockers Procedure

Perform a focused final blocker assessment on a plan candidate or completed execution. The invoking orchestrator
dispatches the appropriate reviewer agent with this procedure; this procedure defines the assessment and result only.


## Inputs

The caller supplies:

- `check_stage`: `plan` or `execution`
- The exact plan revision
- For a plan check: the initial full-review artifact (implementation-plan review or task-plan review, as applicable)
- For an execution check: `execution-journal.md`, the deviation-journal path, and the execution-review artifact
- For a recheck: the prior blocker-check result
- For an execution check: required verification results

If required context is missing or ambiguous, return that issue to the caller. Never substitute another plan revision or
infer approval evidence.


## Assessment

For a `plan` check, assess only critical blockers that could invalidate the plan or make its outcome unsafe. Apply the
same criteria to task plans and implementation plans: contradictory requirements, missing critical acceptance or
verification work, infeasible sequencing, or material architectural, security, or data-integrity risks.

For an `execution` check, assess only blockers to safely advancing: unresolved actionable execution-review findings,
missing required acceptance-criteria evidence, undocumented material plan departures, or critical correctness, security,
or data-integrity risks.

On a recheck, verify prior blocker findings first, then check for new blockers. Ignore wording, formatting, style, and
optional suggestions. Do not expand the assessment into a full review.


## Result

Return `Gate result: PASS` or `Gate result: BLOCKED`, with evidence and any blocking findings, to the caller. Include
the result in the review artifact or notes specified by the caller. Do not contact the human or dispatch another agent.

The caller owns all follow-up: resolve plan blockers, obtain any required human input, and review and recheck the exact
revised plan. Route execution blockers back through implementation and review. A pass does not imply human plan
approval; follow the caller's approval order and advance only to the next state it specified.

Do not author plans, modify implementation code, approve on the human's behalf, commit, publish, or advance the
workflow.
