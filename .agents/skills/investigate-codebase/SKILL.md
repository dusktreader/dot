# Investigate Codebase Skill

Delegate substantive codebase investigations to an `engineer-investigator` through the canonical procedure.


## When to use

Use this skill whenever answering a request or advancing a workflow requires a deep codebase investigation, such as
tracing behavior across files or modules, following a non-obvious call path, or establishing how existing code works.
Use it within larger workflows when they need codebase investigation. Do not use it for a simple file or symbol lookup.


## Dispatch

Provide a specific investigation question and relevant project context, including known reproduction steps or constraints
when applicable. If the question is missing or ambiguous, ask for clarification before dispatching.

Dispatch an `engineer-investigator` with `.agents/procedures/investigate-codebase.md`, the question, and its context. Tell
the investigator to return findings directly in its response to you without writing a report file. For separate
investigation questions, dispatch separate investigators as needed.


## Use the findings

Use the returned evidence to answer the question or continue the calling workflow. Cite relevant locations as `file:line`
and distinguish direct observations from inferences and unresolved uncertainty. Follow the calling workflow for any
subsequent artifacts or decisions; this skill does not create an artifact.
