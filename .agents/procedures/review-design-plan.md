# Review Design Plan Procedure

Define the independent review of a design plan for structural completeness, acceptance-criteria quality, architectural
clarity, and ambiguity.


## Required inputs

The caller must provide:

- Design plan path
- Review iteration (`01` for the first review; increment for each re-review)
- Review mode: `full` or `final-blocker-check`
- Output design-review artifact path
- For re-reviews, the prior design-review artifact
- For final blocker checks, the initial full review, exact human-approved plan revision, and any prior blocker-check
  artifact

If any input is missing or ambiguous, ask the caller before reviewing. Never substitute another plan revision.


## Reviewer instructions

Read `.agents/artifacts/design-plan/description.md` as the canonical design-plan structure. Use other read-only project
context or skills when relevant. Review the design artifact, not implementation code. Do not run project tests, builds,
or linters, and do not modify the plan.

In `full` mode:

- Check structural completeness against the design-plan artifact definition.
- Check that acceptance criteria are correctly numbered, observable, testable, and cover important success, variation,
  edge, and failure modes. Flag vague, subjective, redundant, or implementation-level criteria.
- Assess whether the architecture describes the needed components and matches the goal and acceptance criteria without
  prescribing unnecessary implementation detail.
- Flag hedged requirements, undefined jargon, passive language that obscures actors, and relevant unresolved or missing
  ambiguities.
- Assign severity: Critical for structural violations, untestable acceptance criteria, or hallucinated project elements;
  Significant for missing important modes, blocking ambiguity, or fuzzy scope; Trivial for grammar, wording, formatting,
  or minor disagreement.
- Run `dt format markdown` on the plan before reviewing. Do not pass `--check` or manually fix formatter-handled issues.

In `final-blocker-check` mode, examine only the exact human-approved revision and initial review. On blocker rechecks,
verify the prior blocker-check findings first. Do not repeat the full checklist. Report only Critical or Significant
flaws that could materially break the design outcome, invalidate acceptance criteria, or introduce substantial
architectural, safety, or data-integrity risk. Ignore wording and formatting. A pass means no blocker remains; do not
perform another full review.

For re-reviews, carry prior findings forward with resolution status. In final-blocker-check mode, carry forward only
unresolved findings that meet the blocker threshold.


## Review artifact

Read `.agents/artifacts/design-review/description.md` for canonical sections and render
`.agents/artifacts/design-review/template.md.j2` as the caller-supplied artifact path. Replace all sample content with
review-specific findings and evidence. Leave no placeholders. Record prior finding resolution on re-reviews.

In final-blocker-check mode, record `Gate result: PASS` in Notes and explicitly approve the design for the next stage
when no blocker exists. Otherwise record `Gate result: BLOCKED` and identify blocking findings. In full mode, record
findings and notes without claiming human approval.

Return the review artifact path and outcome to the caller. Do not contact the human, revise the plan, commit, publish,
or advance workflow gates.
