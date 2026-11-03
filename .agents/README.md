# System-Wide Agent Instructions

Instructions applied to every agent session, regardless of project. These complement any project-level `.agents/` or
`AGENTS.md` files found in the working directory.


## Directory layout

| Path            | Contents                                                             |
| --------------- | -------------------------------------------------------------------- |
| `agents/`       | Tool-agnostic agent prose definitions                                |
| `artifacts/`    | Artifact definitions: one subdirectory per artifact type             |
| `instructions/` | Instruction files: read when relevant to the task                    |
| `procedures/`   | Reusable procedure descriptions invoked by skills for specific tasks |
| `skills/`       | Skill definitions (auto-loaded by opencode and compatible tools)     |
| `tools/`        | Executable scripts                                                   |


## Agents

Agent definitions live in `agents/`. Each file defines the persona, responsibilities, and mindset for one agent type.
Orchestrators reference these by name when dispatching subagents.

| Agent                   | Role                                                                           |
| ----------------------- | ------------------------------------------------------------------------------ |
| `architect-planner`     | Creates design artifacts; dictates high-level structure                        |
| `architect-reviewer`    | Reviews design and implementation plans from an architect's perspective        |
| `engineer-executor`     | Writes code following an approved plan using shared execution procedures       |
| `engineer-investigator` | Explores codebases to answer a specific question; does not write code          |
| `engineer-planner`      | Translates an approved design plan into a detailed implementation plan         |
| `engineer-reviewer`     | Reviews implementation execution against a plan for quality and coverage       |
| `engineer-task-planner` | Investigates the codebase and authors a focused task plan without a design doc |
| `principal`             | Primary human-facing agent; orchestrates execution of a full workflow          |


## Artifacts

Artifact definitions live in `artifacts/`. Each subdirectory is named for the artifact type and contains exactly two
files:

| File             | Contents                                                |
| ---------------- | ------------------------------------------------------- |
| `description.md` | Canonical section-by-section definition of the artifact |
| `template.md.j2` | Renderable Jinja2 stub for the artifact                 |

The `description.md` is the single source of truth for what belongs in each section. Skills reference it rather than
carrying their own structural definitions. The `template.md.j2` is a minimal stub — headings and `{{ variable }}` slots
— suitable for programmatic rendering.

| Artifact type            | Description                                               |
| ------------------------ | --------------------------------------------------------- |
| `architecture-audit/`    | Structured assessment of a codebase's architecture        |
| `bug-report/`            | Bug triage findings, root cause, impact, and proposed fix |
| `clear-evaluation/`      | Output format and worked example for CLEAR prompt scoring |
| `code-review/`           | Standalone code quality review without a plan             |
| `design-plan/`           | WHAT and WHY: requirements, AC, and architecture          |
| `design-review/`         | Structured critique of a design plan                      |
| `epic-deviation/`        | Product-level assessment of a feature-plan departure      |
| `epic-plan/`             | Product-level outcome, feature register, MVP, and roadmap |
| `epic-review/`           | Adversarial review of an epic plan                        |
| `execution-review/`      | Code review against a plan and execution journal          |
| `execution-journal/`     | Record of work implemented against a plan                 |
| `implementation-plan/`   | HOW: step-by-step execution tasks with AC and steps       |
| `implementation-review/` | Structured critique of an implementation plan             |
| `investigation-report/`  | Structured answer to a specific codebase question         |
| `plan-deviations/`       | Post-plan change and verification journal                 |
| `pr-review/`             | PR comment triage and resolution log                      |
| `task-plan/`             | Focused plan for a minor engineering task                 |
| `task-plan-review/`      | Structured critique of a focused task plan                |


## Instructions

Instruction files live in `instructions/`. Read them when they are relevant to the task at hand.
`instructions/about-me.md` is the exception: read it every session.

| File                       | Read when                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `instructions/about-me.md` | Every session — context about the user                                                      |
| `instructions/git.md`      | Performing any git operation or writing a commit message                                    |
| `instructions/github.md`   | Using the `gh` CLI or interacting with GitHub                                               |
| `instructions/local.md`    | Needing machine-specific context **or accessing any external service** (file may not exist) |
| `instructions/markdown.md` | Editing markdown files                                                                      |
| `instructions/python.md`   | Writing or editing Python code or docstrings                                                |
| `instructions/work.md`     | Working in any work repository or accessing work services (Jira, Confluence, Datadog, etc.) |

Branch-based workflows must follow `procedures/use-worktree.md` (which uses `tools/use-worktree.py`) to obtain worktrees
beneath the repository's `.worktrees/` directory. Never use temporary directories for implementation work.


## Tools

Scripts in `tools/` are executable — invoke them directly. Run any tool with `--help` to see usage.

| Tool                           | Purpose                                                     |
| ------------------------------ | ----------------------------------------------------------- |
| `tools/create-artifact-dir.py` | Create or reuse a dated artifact directory from task inputs |
| `tools/md-to-pdf.py`           | Render markdown files to styled PDF (headless browser)      |
| `tools/use-worktree.py`        | Use a worktree for isolated work                            |


## Skill discovery

Skills are directories containing a `SKILL.md` file. Search for a named skill with `**/*<skill-name>*/SKILL.md` under
the skills directory, or read a known skill using its full path. Searching only for a skill directory name may not
return a result with all filesystem glob implementations.


## Procedure discovery

Procedures are reusable workflow instructions called by skills or other procedures. Search `.agents/procedures/` by the
procedure name referenced by the calling workflow, for example `.agents/procedures/apply-fix.md`.
