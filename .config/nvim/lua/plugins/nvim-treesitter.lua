return {
  -- Powerful treesitter integration into neovim
  "nvim-treesitter/nvim-treesitter",
  branch = "main",
  build = ":TSUpdate",
  lazy = false,
  opts = {
    auto_install = true,
    indent = {
      enable = true,
      disable = { "python" },
    }
  },
}
