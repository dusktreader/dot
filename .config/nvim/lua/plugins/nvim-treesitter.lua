return {
  -- Powerful treesitter integration into neovim
  "nvim-treesitter/nvim-treesitter",
  opts = {
    indent = {
      enable = true,
      disable = { "python" },
    }
  },
}
