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
      'terraform-ls',
      -- 'typescript-tools',

      -- Other LSPs
      'angular-language-server',
      'typos-lsp',
      'ruff',
      'lemminx', -- XML

      -- AI
      'copilot-language-server',

      -- DAPs
      'js-debug-adapter',

      -- Formatters
      'prettierd',

      -- Other
      'tree-sitter-cli',
    },
  },
}
