return {
  -- Automatic folding/splitting of blocks using treesitter
  "Wansmer/treesj",
  dependencies = { "nvim-treesitter/nvim-treesitter" },
  keys = {
    { "<leader>j", function() require("treesj").split() end, desc = "TreeSJ Split" },
    { "<leader>k", function() require("treesj").join() end,  desc = "TreeSJ Join" },
  },
  opts = {
    use_default_keymaps = false,
  },
}
