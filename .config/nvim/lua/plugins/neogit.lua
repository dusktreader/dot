return {
  "NeogitOrg/neogit",
  lazy = true,
  dependencies = {
    -- "esmuellert/codediff.nvim",
    "m00qek/baleia.nvim",
    "folke/snacks.nvim",
  },
  cmd = "Neogit",
  keys = {
    { "<leader>git", function() require("neogit").open({ kind = "auto" }) end, desc = "Show Neogit UI" }
  },
  opts = {
    mappings = {
      status = {
        ["<cr>"] = "Toggle",
        ["o"]    = "GoToFile",
        ["<tab>"] = false,
        ["za"]   = false,
      },
    },
  },
}
