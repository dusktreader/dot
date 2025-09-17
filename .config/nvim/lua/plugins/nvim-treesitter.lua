return {
  -- Powerful treesitter integration into neovim
  "nvim-treesitter/nvim-treesitter",
  lazy = false,
  opts = {
    auto_install = true,
    indent = {
      enable = true,
      disable = { "python" },
    }
  },
}
