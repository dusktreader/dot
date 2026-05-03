# System-Wide Agent Instructions

Instructions applied to every agent session, regardless of project. These complement
any project-level `.agents/` or `AGENTS.md` files found in the working directory.


## What to read

Read `markdown.md` before editing any file in this directory. Read `github.md` and
`git-safety.md` at the start of every session — git and GitHub operations come up
in almost every project, and the safety rules are non-negotiable. Read `editing.md`
before editing any file, every session — this is non-negotiable. Read `git.md`
whenever writing a commit message. Read `python.md` before writing or editing any
Python code or docstrings. Read `local.md` if it exists — it contains context
specific to the current machine and is not tracked in any repository.

| File        | Topic                                                          |
|-------------|----------------------------------------------------------------|
| `editing.md`    | Check file timestamps before every edit — mandatory        |
| `git-safety.md` | Never push, never commit on main/master — mandatory        |
| `git.md`        | Commit message style — bullet list bodies, always          |
| `github.md`     | Which `gh` account to use for which repository owner       |
| `local.md`      | Machine-local context: hardware, purpose, quirks (optional)|
| `markdown.md`   | Markdown style rules for all `.agents/` files              |
| `python.md`     | Python style — no Sphinx markup in docstrings              |
