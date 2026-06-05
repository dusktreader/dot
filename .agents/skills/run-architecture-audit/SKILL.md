---
name: run-architecture-audit
description: Orchestrates an architecture audit: investigate the codebase and produce a structured assessment with findings and recommendations.
---

# Run Architecture Audit Skill

Coordinate an architecture audit: investigate the existing codebase and synthesize findings into a
structured assessment with problem areas and recommendations. All artifacts are stored under
`.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`.


## Prerequisites

Your prompt must include:

- Scope of the audit (e.g. "the authentication subsystem", "the entire backend", "the data layer")
- Any specific concerns or questions to address

If not provided, ask before proceeding. Do not guess.


## Project directory

Derive `{project-name}` from the audit scope, prefixed with `audit-`
(e.g. `audit-auth-subsystem`). Create `.agents/work/{YYYYMMDD}-{HHmmss}--{project-name}/`. All artifacts
for this project are stored there.

| Artifact                | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| `architecture-audit.md` | Structured assessment with findings and recommendations |


## Process


### 1. Investigate

Dispatch one or more `engineer-investigator` subagents with the `investigate-codebase` skill. Derive
targeted questions from the audit scope and any specific concerns provided. Multiple investigators may run
in parallel for different subsystems or concerns.

Synthesize all findings before proceeding to the assessment.


### 2. Assess

Dispatch an `architect-planner` subagent to produce `architecture-audit.md` from the investigation
findings. Use `.agents/templates/architecture-audit.md` as the template.

**Stop.** Present the audit to the human. Discuss findings and recommendations. If the human requests
deeper investigation into a specific area, dispatch another `engineer-investigator` and update the audit.


### 3. Report

Report completion to the human with the project directory path and the audit artifact path.
