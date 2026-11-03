# Run PR Skill

Publish a branch to GitHub and creates a pull-request for it when the human explicitly invokes this skill. This is the
only workflow that creates a pull request.


## When to use

Use after the requested work is complete and the human wants its topic branch published as a pull request. Do not invoke
as an automatic follow-up to another workflow.


## Preconditions

Operate only from a clean topic branch. Reject `main` and `master`. Stop if the worktree is dirty, the branch is
detached, or the regular branch cannot be identified. Make sure the branch is properly based on `main` or `master`. If
`main` or `master` is not a base, stop and notify the user that the branch needs to be rebased.


## Restrictions

Never force-push. Do not merge into `main` or `master`. Do not push or create a pull request unless the human explicitly
invoked `run-pr` in the current request.


## Workflow phases and states

| Phase       | State                   | Transition                                                       |
| ----------- | ----------------------- | ---------------------------------------------------------------- |
| Setup       | Publication context     | Confirm GitHub account, remote, target base, and rebase decision |
| Publication | Base synchronization    | Compare with confirmed base; resolve required rebase             |
| Publication | Push branch             | Push the regular branch without force options                    |
| Publication | Create pull request     | Create against the confirmed base with `gh pr create`            |
| Handoff     | Return pull request URL | Report the pull request URL                                      |


### Setup phase

#### Publication context

Read `~/.agents/instructions/github.md` before using `gh`. Confirm the authenticated `gh` account as required there,
confirm the intended remote, and determine the target base. If the base branch or whether the normal branch must be
rebased is ambiguous, ask the human and wait. Never infer either decision.


### Publication phase

#### Base synchronization

Check the normal branch against the confirmed base. Resolve any required rebase before publication. Do not alter a base
branch.


#### Push branch

Push the normal branch without force options. The human must explicitly invoke `run-pr` in the current request before
any push.


#### Create pull request

Create the pull request against the confirmed base with `gh pr create`.


### Handoff phase

#### Return pull request URL

Return the pull request URL.
