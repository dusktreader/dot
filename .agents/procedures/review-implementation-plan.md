# Review Implementation Plan Procedure

Define the independent review of an implementation plan for completeness, feasibility, testability, and alignment with
its design or supplied planning context.


## Required inputs

The caller must provide:

- Implementation plan path
- Review iteration (`01` for the first review; increment for each re-review)
- Review mode: `full` or `final-blocker-check`
- Output implementation-review artifact path
- For re-reviews, the prior review artifact
- For final blocker checks, the initial full review and any prior blocker-check artifact
- Exact human-approved plan revision for `final-blocker-check` mode

If any input is missing or ambiguous, ask the caller before reviewing. Never substitute another plan revision.


## Reviewer instructions

Read `.agents/artifacts/implementation-plan/description.md` as the canonical plan structure and locate the design plan
referenced by the implementation plan, or equivalent context supplied by the caller.

In `full` mode:

- Check structural completeness against the artifact definition.
- Verify that `Project Standards` lists relevant existing standards and that `Relevant Skills` lists only existing
  skills or procedures.
- Check that tasks are correctly scoped, actionable, ordered, and feasible.
- Check that acceptance criteria are numbered, observable, and testable, covering success cases, variations, edge cases,
  and relevant failure modes.
- Check that Unknowns are genuine, answerable, and complete, with no unlisted ambiguity that blocks execution.
- Assign severity: Critical for structural violations, untestable acceptance criteria, or hallucinated project elements;
  Significant for missing important modes or blocking ambiguity; Trivial for grammar, wording, formatting, or minor
  disagreement.
- In full mode only, run `dt format markdown` on the plan before review. Do not modify the plan in blocker-check mode.

In `final-blocker-check` mode, inspect the exact human-approved revision and initial review. On recheck, inspect the
prior blocker-check result first. Do not repeat the full checklist. Report only Critical or Significant issues that
could make execution infeasible, contradict approved design, omit critical acceptance or verification work, or introduce
substantial security, data-integrity, or operational risk. Ignore wording and formatting.

Do not modify the plan, run project tests/builds/linters, author implementation code, approve on the human's behalf,
commit, publish, or advance the workflow.


## Review artifact

Read `.agents/artifacts/implementation-review/description.md` for canonical sections. Render
`.agents/artifacts/implementation-review/template.md.j2` as the caller-supplied artifact path, using the plan title and
review iteration. Replace all sample content with review-specific findings and evidence. On re-review, include prior
finding resolution. Leave no placeholders.

For a final blocker check, report `Gate result: PASS` in Notes and explicitly approve the plan for execution when no
blockers exist. Otherwise report `Gate result: BLOCKED` and identify the blocking findings. In full mode, record
findings and review notes without claiming human approval.

Return the review artifact path and outcome to the caller. The caller resolves findings and controls all subsequent
workflow gates.
