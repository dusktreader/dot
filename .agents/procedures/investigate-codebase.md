# Investigate Codebase Procedure

Investigate a specific question about an existing codebase and report evidence-based findings to the caller.


## Required inputs

The caller must provide:

- A specific investigation question
- Relevant project context, such as a bug description, audit scope, or feature requirement
- Known reproduction steps or constraints, when applicable
- An instruction to return findings directly to the caller without writing a report file

If the question is missing or ambiguous, ask the caller before proceeding.


## Scope

- Read only. Do not edit files, run commands that modify state, or write new files.
- Stay focused on the question. Do not produce a general survey unless asked.
- Do not propose improvements or alternative approaches unless asked.
- Load relevant project skills that provide context about the codebase.


## Process

### Understand the question

Restate the question in your own words. If it is ambiguous, stop and ask for clarification before proceeding.


### Identify entry points

Identify the most relevant files, modules, classes, functions, and tests related to the question. Read broadly enough to
avoid missing relevant paths.


### Explore systematically

Follow imports, trace call chains, read tests, and check documentation. Continue until you have enough evidence to
answer the question or have exhausted the relevant surface area.


### Gather and label evidence

Collect specific locations using `file:line` references. Label each finding as an observation directly supported by the
code or an inference drawn from observations.


### Report findings

Use the sections in `.agents/artifacts/investigation-report/description.md` as a guide. Omit `## Open Questions` when
none remain. Report findings directly to the caller; do not write an artifact.