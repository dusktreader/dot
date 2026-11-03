# Review Execution With Human Procedure

Present an agent-reviewed implementation to the human, collect feedback or acceptance, and return control to the caller.


## Required inputs

The caller must provide:

- Concise implementation summary and changed-file scope for human review
- Summary of agent-review findings and their resolution status
- Focused verification results
- Artifact directory and worktree/branch context
- Current workflow state and states to resume for requested changes or acceptance
- Deviation journal path when it differs from `plan-deviations.md`

If required context is missing or ambiguous, ask the caller before presenting the review.


## Review protocol

1. Present the implementation summary and relevant diff or changed-file overview, the agent-review findings and
   resolution status, and focused verification results. The execution-review artifact is internal evidence, not a
   substitute for presenting the implementation to the human.
2. Ask the human whether they accept the reviewed implementation or request changes. Questions, silence, and silence
   about individual findings do not constitute acceptance.
3. If changes are requested, return those requests to the caller. The caller determines scope and implements approved
changes through its execution state, recording implemented changes in the caller-supplied deviation journal and
returning for agent review.
4. If the human accepts the implementation as reviewed, report that acceptance evidence to the caller and return control
   to its supplied next state. Do not start blocker checks, QA, commits, or handoff yourself.

Do not edit code, plans, reviews, journals, or deviation records. Never imply that the human accepted changes they have
not reviewed.
