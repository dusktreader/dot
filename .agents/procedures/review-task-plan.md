# Review Task Plan Procedure

Define the independent review of a focused task plan before human approval.


## Required inputs

The caller must provide:

- Path to the task plan
- Review iteration (`01` for the first review)
- For re-reviews, the prior task-plan review path
- Output path for the review artifact

If any input is missing or ambiguous, ask the caller before reviewing.


## Review

Read `.agents/artifacts/task-plan/description.md` as the canonical plan structure. Evaluate whether the plan is
complete, focused, executor-ready, and consistent with the task request and codebase evidence.

Check that:

- The goal clearly states the outcome, scope, and exclusions.
- Project commands are exact, documented, and have meaningful expected results.
- Relevant project standards are identified without hallucinated references.
- Steps are actionable, correctly ordered, and follow test-driven design for code changes.
- Acceptance criteria are observable, testable, and cover important behavior and failure modes.
- Technical notes clarify genuine task-specific constraints without expanding scope.
- No unresolved Unknowns or contradictions prevent execution.

Read `.agents/artifacts/task-plan-review/description.md` and render `.agents/artifacts/task-plan-review/template.md.j2`
as `task-plan-review--{NN}.md` in the task artifact directory. Replace all template values with project-specific
content. Record findings, their severity, and actionable suggestions. On re-review, verify prior findings and assess
changes introduced by their resolution. Do not edit the task plan or decide how findings should be resolved.

The caller resolves findings and repeats review after material plan revisions. An approved agent review opens human
feedback; it does not approve the plan for the human. Do not contact the human, run project checks, modify code, commit,
or advance the workflow.
