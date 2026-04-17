# GitHub Account Usage

Two GitHub accounts are available via the `gh` CLI. Always use the correct account
for the repository being worked on. Switch accounts with:

```shell
gh auth switch --user <username>
```


## Account mapping

| Account              | Use for                                                         |
|----------------------|-----------------------------------------------------------------|
| `dusktreader`        | Repositories owned by `dusktreader`                             |
| `Tucker-Beck_mcgraw` | Repositories owned by `mcgrawhill-llc` or `Tucker-Beck_mcgraw` |


## Rules

- Before any `gh` operation (creating PRs, opening issues, reading issue lists, etc.)
  check the repository owner and switch to the correct account.
- `dusktreader` is the personal account. It **cannot** create PRs or issues on
  enterprise-managed repos (`mcgrawhill-llc`, `Tucker-Beck_mcgraw`).
- `Tucker-Beck_mcgraw` is the MHE enterprise-managed account. Do **not** use it for
  personal (`dusktreader`) repos.
- If you are unsure which account is active, run `gh auth status` to check.


## Push policy

**Never run `git push` (in any form) without explicit confirmation from the user.**

This applies to:

- `git push`
- `git push -u origin <branch>`
- `git push --force` / `git push --force-with-lease`
- Any `gh` command that pushes commits or refs (e.g. `gh pr create` after an unpushed branch)

Before pushing, always show the user what will be pushed and ask for confirmation. Only
push after receiving an unambiguous "yes" for that specific push.
