# Task plan: Human-gated plan reviews

Update the feature workflow so plan review is collaborative during human feedback and uses one consolidated agent review
after the human finishes reviewing each plan artifact.


## Goal

Revise the `run-feature` plan-review cadence to stop dispatching adversarial agent reviews after every human-directed
edit. Preserve an initial agent review, allow an uninterrupted human feedback loop, then run a final consolidated review
before requesting approval. Apply the same gates to design and implementation plans without weakening unknown-resolution
or explicit-approval requirements.


## Project commands

### Format changed skill files

Command:

```shell
~/.agents/tools/markdown-format.py format <changed-skill-files>
```

Expected output:

Changed skill files are formatted without Markdown errors.


## Project standards

- [Repository guide](../../.dot_agents/dot.md)
- [Markdown style guide](../../.agents/instructions/markdown.md)
- [`run-feature` workflow](../../.agents/skills/run-feature/SKILL.md)
- [`review-design-plan` skill](../../.agents/skills/review-design-plan/SKILL.md)
- [`review-implementation-plan` skill](../../.agents/skills/review-implementation-plan/SKILL.md)


## Steps

1. Audit the workflow and related planning/review skills for instructions that dispatch reviewers after individual human
   comments or revisions.
2. Update the design-plan gate: create the plan, run the initial agent review, then allow iterative human feedback and
   edits without automatically dispatching another reviewer. On an explicit human signal such as `ready for final
   review`, run one consolidated review of the current plan and all accumulated changes.
3. Apply the same cadence to the implementation-plan gate. Keep design approval required before implementation planning
   and implementation-plan approval required before execution.
4. Resolve final-review findings as a batch. Run a follow-up review only to verify material fixes, then request the
   relevant explicit human approval. Preserve the existing one-at-a-time resolution of design unknowns and all
   stage-specific approval boundaries.
5. Remove or revise conflicting guidance in related skills so reviewers are not independently re-dispatched during the
   human feedback loop.
6. Format changed Markdown files and inspect the final workflow for clear review triggers, approval gates, and no
   automatic review after each human-directed edit.


## Acceptance criteria

- AC01: Human comments and requested plan edits do not automatically dispatch an adversarial reviewer.
- AC02: An explicit `ready for final review` signal triggers one consolidated agent review of the current plan artifact.
- AC03: Design and implementation plans each retain their own final review and explicit human approval gates.
- AC04: Follow-up reviews verify material fixes from the consolidated review; they are not triggered by every human
  iteration.
- AC05: Existing sequential unknown resolution, stage ordering, and approval boundaries remain intact.


## Technical notes

The human review loop is for collaborative refinement, not approval by silence. The final agent review does not replace
explicit human approval.