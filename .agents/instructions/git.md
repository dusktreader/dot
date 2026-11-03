# Git Usage

## Safety rules

Mandatory safety rules for all git operations. These override any default tool behavior and apply to every session in
every repository.


### Never publish packages

Never run `uv publish`, `twine upload`, `npm publish`, `cargo publish`, or any other package registry publish command.
Publishing is a human decision.

This applies even when:

- The build succeeded cleanly and all tests pass
- A version bump was just made as part of the current task
- The user asks "are we done?" or "what's next?" — neither is permission to publish
- The prior conversation context discussed publishing as a next step

There are no exceptions. An agent should never publish.


### Never push

Never run `git push` without explicit human approval for every push. Getting approval earlier does not mean you can
also push new commits. Pushing is always a human decision.

This applies even when:

- The branch is brand new and has no remote tracking
- A commit hook rewrites SHAs and the local branch diverges from origin
- The user asks "are we done?" or "what's next?" — neither is permission to push
- A PR has been opened and CI is asking for the latest commits
- The branch is a personal fork branch with no shared history
- A skill or workflow previously pushed during the same session — that permission was specific to that moment and does
  not carry forward

The user's permission to push must be an explicit, unambiguous instruction in the current message. For example "push
this branch now" or "go ahead and push". A prior session's permission does not carry over.

Before running any `git push`, check the current branch with `git branch --show-current` and confirm the human
explicitly requested publication in the current request.


### Never force-push

Never run `git push --force`, `git push --force-with-lease`, or any variant that rewrites remote history. Force-pushing
is categorically forbidden, regardless of branch, context, or apparent safety.

This applies even when:

- The branch is a personal feature branch with no other contributors
- A prior `git push` was run in the same session and the local branch has since diverged
- The user says "fix the PR comments" or "amend the commit" — neither is permission to force-push
- CI asked for a history-clean branch

Force-pushes are strictly forbidden for agents in any context. Do not do it even if prompted to.


### Never amend commits

Never run `git commit --amend` for any reason. Amending rewrites history and, when the branch has already been pushed,
always requires a force-push. Both operations are forbidden by these rules.

If a committed change needs correction, create a new commit instead.

This applies even when:

- The prior commit was made in the same session
- The change is trivially small (a typo, a missing file)
- The user says "just fix that in the commit" — that is not permission to amend

Commit amendment is strictly forbidden for agents in any context. Do not do it even if prompted to.


### Never commit on main or master

Never add commits directly to `main` or `master`, regardless of how trivial the change appears. If the working tree has
changes that need committing and the current branch is `main` or `master`:

1. Stop before staging anything
2. Propose a new branch name to the user, following the repository's existing branch naming conventions if discoverable
from `git log` or `git branch -a`
3. Wait for the user to confirm or supply a different name
4. Only after confirmation, create the branch with `git switch -c <name>` and commit there

This rule has no exceptions. "Just a typo fix" still gets a branch.


### When in doubt, ask

If a git operation feels like it might be destructive, irreversible, or politically loaded (force push, history rewrite,
branch deletion, tag manipulation, anything touching a shared remote), stop and ask the user before running the command.
The cost of one extra question is much lower than the cost of one bad push.


## Commit messages

When writing commit messages, use conventional commit style. Always use a bullet list in the body to describe the
individual changes. Never write the body as prose.


### Types

The type must be one of:

- `feat`: a new feature
- `fix`: a bug fix
- `docs`: documentation-only changes
- `style`: formatting changes that do not affect behavior (whitespace, semicolons, etc.)
- `refactor`: code changes that neither fix a bug nor add a feature
- `perf`: performance improvements
- `test`: adding or correcting tests
- `build`: build system or dependency changes
- `ci`: CI configuration and scripts
- `chore`: maintenance tasks that do not modify src or tests
- `revert`: reverting a previous commit

The `(<ticket-id>)` scope is included when a ticket ID is known. Work projects require it; see the work context
instructions.

For personal projects, omit `(<ticket-id>)` if none is supplied. Don't use `NO-TICKET` for personal projects.

For the commit body, always use a bullet list to describe the individual changes. Never write the body as prose.


### Format

```text
<type>(<ticket-id>): <summary>

- <change 1>
- <change 2>
- <change 3>
```

The `ticket-id` is extracted from the branch name (e.g. `feature/ABC-123--my-thing` → `ABC-123`).

The `summary` is lowercase and does not end with a period. Each bullet describes one logical change concisely, also
lowercase, no trailing period.


### Example

```text
ci(ABC-123): redesign github actions workflows

- replace tag-per-environment deploy model with versioned promotion chain
- extract docker-publish, verify-images, helm-deploy, ui-sync composite actions
- migrate ui config from build-time env-cmd to runtime config.json
- add terraform-deploy.yml for dispatch-based single-environment tf deployments
- delete merge.yml, fixing unconditional terraform apply on every merge to main
```
