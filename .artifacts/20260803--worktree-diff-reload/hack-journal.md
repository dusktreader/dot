# Worktree diff reload

This journal records the implementation and focused verification for reloading a worktree diff in place.


## Change

- Updated `.config/nvim/lua/user/worktree.lua` to reload the current worktree diff without reopening the picker.
- Preserved the cursor's source file and diff location when available, with a clamped rendered-line fallback.
- Preserved the cursor column and restored the prior viewport on reload.
- Used base-file coordinates for context and deleted lines, insertion anchors for added lines, and the nearest
  rendered line for header-only positions.
- Added `.config/nvim/tests/worktree_test.lua` for source-location remapping, insertion anchors, header positions, and
  fallback clamping.


## Verification

Focused checks passed:

```shell
nvim --headless -u NONE --cmd 'set rtp+=.config/nvim' -c 'luafile .config/nvim/tests/diff_context_test.lua' -c 'luafile .config/nvim/tests/worktree_test.lua' -c 'qa!'
luac -p .config/nvim/lua/user/worktree.lua .config/nvim/tests/worktree_test.lua
node ~/.agents/tools/check-markdown-format.mjs .artifacts/20260803--worktree-diff-reload/hack-journal.md
git diff --check
```
