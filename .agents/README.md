# System-Wide Agent Instructions

Instructions applied to every agent session, regardless of project. These complement
any project-level `.agents/` or `AGENTS.md` files found in the working directory.


## Directory layout

| Path             | Contents                                                         |
| ---------------- | ---------------------------------------------------------------- |
| `agents/`        | Tool-agnostic agent prose definitions                            |
| `artifacts/`     | Artifact definitions: one subdirectory per artifact type         |
| `instructions/`  | Instruction files — read when relevant to the task               |
| `skills/`        | Skill definitions (auto-loaded by opencode and compatible tools) |
| `tools/`         | Executable scripts                                               |


## Artifacts

Artifact definitions live in `artifacts/`. Each subdirectory is named for the artifact type
and contains exactly two files:

| File               | Contents                                                        |
| ------------------ | --------------------------------------------------------------- |
| `description.md`   | Canonical section-by-section definition of the artifact         |
| `template.md.j2`   | Renderable Jinja2 stub for the artifact                         |

The `description.md` is the single source of truth for what belongs in each section. Skills
reference it rather than carrying their own structural definitions. The `template.md.j2` is a
minimal stub — headings and `{{ variable }}` slots — suitable for programmatic rendering.

| Artifact type             | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `architecture-audit/`     | Structured assessment of a codebase's architecture       |
| `bug-report/`             | Confirmed bug investigation findings and proposed fix    |
| `code-review/`            | Standalone code quality review without a plan            |
| `design-plan/`            | WHAT and WHY: requirements, AC, and architecture         |
| `design-review/`          | Structured critique of a design plan                     |
| `execution-review/`       | Code review against an implementation plan and journal   |
| `implementation-journal/` | Running record of execution progress                     |
| `implementation-plan/`    | HOW: step-by-step execution tasks with AC and steps      |
| `implementation-review/`  | Structured critique of an implementation plan            |
| `investigation-report/`   | Structured answer to a specific codebase question        |
| `pr-review/`              | PR comment triage and resolution log                     |


## Instructions

Instruction files live in `instructions/`. Read them when they are relevant to the task at hand.
`instructions/about-me.md` is the exception: read it every session.

| File                          | Read when                                                                                   |
| ----------------------------- | ------------------------------------------------------------------------------------------- |
| `instructions/about-me.md`    | Every session — context about the user                                                      |
| `instructions/editing.md`     | Editing any file                                                                            |
| `instructions/git-safety.md`  | Performing any git operation                                                                |
| `instructions/git.md`         | Writing a commit message                                                                    |
| `instructions/github.md`      | Using the `gh` CLI or interacting with GitHub                                               |
| `instructions/local.md`       | Needing machine-specific context **or accessing any external service** (file may not exist) |
| `instructions/markdown.md`    | Editing markdown files                                                                      |
| `instructions/python.md`      | Writing or editing Python code or docstrings                                                |


## Tools

Scripts in `tools/` are executable — invoke them directly. Run any tool with `--help` to see usage.

| Tool                        | Purpose                                                |
| --------------------------- | ------------------------------------------------------ |
| `tools/align-md-tables.py`  | Rewrite markdown files in place with aligned tables    |
| `tools/md-to-pdf.py`        | Render markdown files to styled PDF (headless browser) |
