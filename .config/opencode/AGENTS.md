# Agent Instructions

Read `~/.agents/README.md` for system-wide instructions and directory layout.


## Instructions

Read the relevant instruction file before starting any task that matches the trigger below.

| File                                   | Read when                                     |
| -------------------------------------- | --------------------------------------------- |
| `~/.agents/instructions/editing.md`    | Editing any file                              |
| `~/.agents/instructions/git-safety.md` | Performing any git operation                  |
| `~/.agents/instructions/git.md`        | Writing a commit message                      |
| `~/.agents/instructions/github.md`     | Using the `gh` CLI or interacting with GitHub |
| `~/.agents/instructions/local.md`      | Needing machine-specific context              |
| `~/.agents/instructions/markdown.md`   | Writing or editing any markdown file          |
| `~/.agents/instructions/python.md`     | Writing or editing Python code or docstrings  |


## Testing

After small changes, run only the relevant unit tests during iteration. Do not run integration or end-to-end suites
after
each edit; run them once at the end only when the change warrants them or the user requests them.


## Markdown formatting

Run `dt format markdown` on Markdown files after authoring or editing them. Do not pass `--check` during
normal agent work; reserve it for explicit human or CI validation.
