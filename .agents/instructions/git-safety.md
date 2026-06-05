# Git Safety Rules

Mandatory safety rules for all git operations. These override any default tool
behavior and apply to every session in every repository.


## Never publish packages

Never run `uv publish`, `twine upload`, `npm publish`, `cargo publish`, or any
other package registry publish command. Publishing is a human decision.

This applies even when:

- The build succeeded cleanly and all tests pass
- A version bump was just made as part of the current task
- The user asks "are we done?" or "what's next?" — neither is permission to publish
- The prior conversation context discussed publishing as a next step

The only exception is an explicit, unambiguous instruction in the current message —
for example "publish it now" or "go ahead and publish to PyPI". A prior session's
permission does not carry over.


## Never push

Never run `git push` for any reason. Never push branches, never push tags, never
push to fork remotes, never push to upstream. Pushing is a human decision.

This applies even when:

- The branch is brand new and has no remote tracking
- A commit hook rewrites SHAs and the local branch diverges from origin
- The user asks "are we done?" or "what's next?" — neither is permission to push
- A PR has been opened and CI is asking for the latest commits
- The branch is a personal fork branch with no shared history

The only exception is if the user issues an explicit, unambiguous instruction in
the current message — for example "push this branch now" or "go ahead and push".
A prior session's permission does not carry over.


## Never force-push

Never run `git push --force`, `git push --force-with-lease`, or any variant that
rewrites remote history. Force-pushing is categorically forbidden, regardless of
branch, context, or apparent safety.

This applies even when:

- The branch is a personal feature branch with no other contributors
- A prior `git push` was run in the same session and the local branch has since
  diverged
- The user says "fix the PR comments" or "amend the commit" — neither is
  permission to force-push
- CI asked for a history-clean branch

The only exception is an explicit, unambiguous instruction in the current message —
for example "force-push this branch now". A prior session's permission does not
carry over.


## Never amend commits

Never run `git commit --amend` for any reason. Amending rewrites history and,
when the branch has already been pushed, always requires a force-push. Both
operations are forbidden by these rules.

If a committed change needs correction, create a new commit instead.

This applies even when:

- The prior commit was made in the same session
- The change is trivially small (a typo, a missing file)
- The user says "just fix that in the commit" — that is not permission to amend

The only exception is an explicit, unambiguous instruction in the current message —
for example "amend the last commit". A prior session's permission does not carry
over.


## Never commit on main or master

Never add commits directly to `main` or `master`, regardless of how trivial the
change appears. If the working tree has changes that need committing and the
current branch is `main` or `master`:

1. Stop before staging anything
2. Propose a new branch name to the user, following the repository's existing
   branch naming conventions if discoverable from `git log` or `git branch -a`
3. Wait for the user to confirm or supply a different name
4. Only after confirmation, create the branch with `git switch -c <name>` and
   commit there

This rule has no exceptions. "Just a typo fix" still gets a branch.


## When in doubt, ask

If a git operation feels like it might be destructive, irreversible, or
politically loaded (force push, history rewrite, branch deletion, tag
manipulation, anything touching a shared remote), stop and ask the user before
running the command. The cost of one extra question is much lower than the cost
of one bad push.
