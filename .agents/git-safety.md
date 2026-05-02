# Git Safety Rules

Mandatory safety rules for all git operations. These override any default tool
behavior and apply to every session in every repository.


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
