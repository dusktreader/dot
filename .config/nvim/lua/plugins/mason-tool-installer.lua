return {
  -- automated mason tool installation
  "WhoIsSethDaniel/mason-tool-installer.nvim",
  dependencies = {
    "williamboman/mason.nvim",
  },
  opts = {
    ensure_installed = {

      -- Language LSPs
      'ty',
      'gopls',
      'lua-language-server',
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
      -- NOTE: tree-sitter-cli removed - on Apple Silicon, Mason installs x86_64 version
      -- which causes nvim-treesitter to compile parsers for wrong architecture.
      -- nvim-treesitter will clone and compile parsers directly instead (prefer_git = true)
      -- 'tree-sitter-cli',
    },
  },
}
