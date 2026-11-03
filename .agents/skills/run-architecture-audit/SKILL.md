# Run Architecture Audit Skill

Coordinate an architecture audit: investigate the existing codebase and synthesize findings into a structured assessment
with problem areas and recommendations. Store audit artifacts in the directory returned by
`.agents/procedures/use-artifact-dir.md`.


## When to use

Use this skill when a human wants a structured assessment of a codebase's architecture — identifying problem areas,
technical debt, and improvement opportunities — without committing to implementing any specific change.

This is a standalone skill triggered directly by humans. It does not produce a plan or write code. If the audit surfaces
specific work to do, follow up with `run-feature`, `triage-bug`, or `run-fix` as appropriate.

Do not confuse with `triage-bug` (diagnosing a suspected defect), `run-fix` (applying an explicitly authorized known
fix), or `run-feature` (building a feature). Use this skill when the goal is *understanding* rather than *changing*.


## Prerequisites

Your prompt must include:

- Scope of the audit (e.g. "the authentication subsystem", "the entire backend", "the data layer")
- Any specific concerns or questions to address

If not provided, ask before proceeding. Do not guess.


## Artifact directory

Invoke `.agents/procedures/use-artifact-dir.md` from the current worktree with `branch_type=docs`, the audit scope as
the summary, and ticket if provided. Set `audit_path` to the next unused `architecture-audit--{scope-slug}--NN.md` in
the returned directory. Use a short lowercase kebab-case scope slug and a zero-padded sequence starting at `01`.

| Artifact                                  | Description                                             |
| ----------------------------------------- | ------------------------------------------------------- |
| `architecture-audit--{scope-slug}--NN.md` | Structured assessment with findings and recommendations |


## Process

### 1. Investigate

Dispatch one or more `engineer-investigator` subagents with `.agents/procedures/investigate-codebase.md`. Derive
targeted questions from the audit scope and any specific concerns provided. Multiple investigators may run in parallel
for different subsystems or concerns.

Synthesize all findings before proceeding to the assessment.


### 2. Assess

Dispatch an `architect-planner` subagent to produce `audit_path` from the investigation findings. Read
`.agents/artifacts/architecture-audit/description.md` for the canonical section definitions, and render
`.agents/artifacts/architecture-audit/template.md.j2` to produce the initial file. Replace all dummy content — every
line drawn from the retro encabulator — with real content for this audit. The rendered file must contain no placeholder
text when submitted.

**STOP — end your turn here.** Present the audit to the human. Discuss findings and recommendations. If the human
requests deeper investigation into a specific area, dispatch another `engineer-investigator` and update the audit.

Before ending your turn, verify every item in this checklist:
- [ ] I have presented the architecture audit to the human in this turn
- [ ] I have NOT started any follow-up implementation or planning work
- [ ] I am ending my turn now and will not act again until the human responds


### 3. Report

Report completion to the human with the project directory path and the audit artifact path.
