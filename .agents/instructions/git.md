# Git Usage

## Commit messages

When writing commit messages, always use a bullet list in the body to describe
the individual changes. Never write the body as prose.


### Format

```text
<type>(<jira-id>): <short description>

- <change 1>
- <change 2>
- <change 3>
```

The Jira ID is extracted from the branch name (e.g. `feature/FUS-123--my-thing` → `FUS-123`).
If the branch name contains `NO-TICKET`, use `NO-TICKET` as the ID. If there is no recognisable
ID in the branch name, omit the parenthetical entirely (e.g. `feat: add the jawa feature`).

The short description is lowercase and does not end with a period. Each bullet describes one
logical change concisely, also lowercase, no trailing period.


### Example

```text
ci(NO-TICKET): redesign github actions workflows

- replace tag-per-environment deploy model with versioned promotion chain
- extract docker-publish, verify-images, helm-deploy, ui-sync composite actions
- migrate ui config from build-time env-cmd to runtime config.json
- add terraform-deploy.yml for dispatch-based single-environment tf deployments
- delete merge.yml, fixing unconditional terraform apply on every merge to main
```


## Pushes

**Never run `git push` (in any form) without explicit confirmation from the user.**

This applies to:

- `git push`
- `git push -u origin <branch>`
- `git push --force` / `git push --force-with-lease`

Before pushing, always show the user what will be pushed and ask for confirmation. Only
push after receiving an unambiguous "yes" for that specific push.
