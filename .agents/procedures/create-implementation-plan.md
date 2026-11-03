# Create Implementation Plan Procedure

Define the authoring instructions for an executor-ready implementation plan from an approved design or equivalent
planning context.


## Authoring

Read the supplied planning context, which may be an approved design plan, bug report, or direct human requirements, plus
relevant project context. Investigate the codebase to establish relevant files, patterns, tests, commands, and standards
before writing.

Read `.agents/artifacts/implementation-plan/description.md` for canonical section definitions and render
`.agents/artifacts/implementation-plan/template.md.j2` as the requested plan. Replace all sample content with
project-specific content. The plan must conform to the artifact definition and contain no placeholder text.

Translate the supplied requirements into specific, ordered, executor-ready tasks with observable acceptance criteria,
tests at appropriate levels, exact project commands, and relevant project standards. When planning context includes a
bug report or design plan, use it to ground the requirements. For a scoped fix plan, keep the scope limited to the
identified gap. Capture unresolved decisions as Unknowns for human resolution before review; do not invent answers.

Do not write or modify product code, review or approve the plan, resolve Unknowns without the human, commit, or perform
workflow transitions.
