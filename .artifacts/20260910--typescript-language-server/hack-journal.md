# Hack journal: Bootstrap TypeScript language server

This record documents the TypeScript language-server installation repair for Neovim's built-in LSP client.


## Diagnosis

Opening a TypeScript buffer produced a spawn warning because `typescript-language-server` was absent from the machine.
The Neovim configuration already enables `ts_ls`, and Mason's tool list already included the package, but Mason and
`mason-tool-installer.nvim` were both lazy-loaded on `VeryLazy`. The installer had not loaded or run during the affected
startup, so no Mason package or executable existed.


## Changes

- Made `mason.nvim` load during startup so it can establish its executable path before LSP startup.
- Made `mason-tool-installer.nvim` load during startup and explicitly enabled its startup installation pass.
- Added a one-second startup delay so Mason has initialized before the installer runs.
- Kept `typescript-language-server` in the Mason-managed language-server list.

The repository bootstrap manifest remains the owner of system-wide prerequisites. Mason remains the owner of Neovim
language servers, which avoids duplicating npm-managed packages in `dt configure`.


## Verification

Installed the Mason-managed package with `MasonToolsInstallSync`. The package installed successfully and exposed:

```text
/Users/tucker.beck/.local/share/nvim/mason/bin/typescript-language-server
```

The follow-up verification opens a TypeScript buffer, confirms the executable resolves through Neovim's PATH, and checks
that the `ts_ls` client attaches without a spawn warning.
