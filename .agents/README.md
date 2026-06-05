# System-Wide Agent Instructions

Instructions applied to every agent session, regardless of project. These complement
any project-level `.agents/` or `AGENTS.md` files found in the working directory.


## Directory layout

| Path             | Contents                                                         |
| ---------------- | ---------------------------------------------------------------- |
| `agents/`        | Tool-agnostic agent prose definitions                            |
| `instructions/`  | Instruction files — read when relevant to the task               |
| `skills/`        | Skill definitions (auto-loaded by opencode and compatible tools) |
| `templates/`     | Document templates for planning artifacts                        |
| `tools/`         | Executable scripts                                               |


## Instructions

Instruction files live in `instructions/`. Read them when they are relevant to the task at hand.

| File                          | Read when                                              |
| ----------------------------- | ------------------------------------------------------ |
| `instructions/editing.md`     | Editing any file                                       |
| `instructions/git-safety.md`  | Performing any git operation                           |
| `instructions/git.md`         | Writing a commit message                               |
| `instructions/github.md`      | Using the `gh` CLI or interacting with GitHub          |
| `instructions/local.md`       | Needing machine-specific context (file may not exist)  |
| `instructions/markdown.md`    | Editing markdown files                                 |
| `instructions/python.md`      | Writing or editing Python code or docstrings           |


## Tools

Scripts in `tools/` are executable — invoke them directly. Run any tool with `--help` to see usage.

| Tool                        | Purpose                                             |
| --------------------------- | --------------------------------------------------- |
| `tools/align-md-tables.py`  | Rewrite markdown files in place with aligned tables |
