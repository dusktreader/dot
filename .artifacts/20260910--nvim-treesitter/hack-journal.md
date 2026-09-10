# Hack journal: Restore Neovim Tree-sitter

This record documents the focused Neovim Tree-sitter repair for the Neovim 0.12 migration.


## Diagnosis

Neovim is `v0.12.4`, and the installed `nvim-treesitter` checkout is on `main` at commit `427e9222`. The plugin's
current main branch requires the external `tree-sitter-cli` executable to compile parsers. The configured machine did
not have that executable, so `:checkhealth nvim-treesitter` reported `tree-sitter-cli not found` and parser installation
failed with `ENOENT` while running `tree-sitter build`.

The existing Apple Silicon workaround was stale. The current plugin implementation does not support its old
`prefer_git` setting and always invokes the CLI for compilation.


## Changes

- Added `tree-sitter-cli` to `etc/install.yaml`, using MacPorts on Darwin and `apt` on Linux.
- Removed the obsolete Apple Silicon `CFLAGS` and `prefer_git` configuration from the Tree-sitter plugin setup.
- Installed the missing CLI locally with MacPorts.


## Verification

Ran the following checks after installation:

```shell
tree-sitter --version
nvim --headless '+checkhealth nvim-treesitter' '+qa!'
nvim --headless '+TSUpdate' '+qa!'
```

The CLI is available, the Tree-sitter health check no longer reports a missing CLI, and the configured parsers can be
compiled and loaded by Neovim.
