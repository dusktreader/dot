return {
  -- automated mason tool installation
  "WhoIsSethDaniel/mason-tool-installer.nvim",
  dependencies = {
    "williamboman/mason.nvim",
  },
  opts = {
    ensure_installed = {
      'typos-lsp',
      'basedpyright',
      'gopls',
      'lua-language-server',
      'ruff',
      'python-lsp-server',
      'lemminx',
    },
  },
}




