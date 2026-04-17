return {
  -- Code outline window
  "stevearc/aerial.nvim",
  dependencies = {
     "nvim-treesitter/nvim-treesitter",
     "nvim-tree/nvim-web-devicons"
  },
  keys = {
    { "<leader>o", "<cmd>AerialOpen<cr>", desc = "Aerial Open Outline", noremap = true },
  },
  opts = {
    close_on_select = true,
  },
}
