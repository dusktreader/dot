return {
  -- Powerful treesitter integration into neovim
  "nvim-treesitter/nvim-treesitter",
  opts = {
    ensure_installed = { "javascript" },
    auto_install = true,
    indent = {
      enable = true,
      disable = { "python" },
    }
  },
}
