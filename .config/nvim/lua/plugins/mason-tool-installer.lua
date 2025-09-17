return {
  -- automated mason tool installation
  "WhoIsSethDaniel/mason-tool-installer.nvim",
  dependencies = {
    "williamboman/mason.nvim",
  },
  opts = {
    ensure_installed = {

      -- Language LSPs
      'basedpyright',
      'gopls',
      'lua-language-server',
      'python-lsp-server',
      'typescript-language-server',
      -- 'typescript-tools',

      -- Other LSPs
      'angular-language-server',
      'typos-lsp',
      'ruff',
      'lemminx', -- XML

      -- DAPs
      'js-debug-adapter',

      -- Formatters
      'prettierd',

      -- Other
      'tree-sitter-cli',
    },
  },
}
