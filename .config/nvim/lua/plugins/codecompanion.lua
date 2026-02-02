return {
  "olimorris/codecompanion.nvim",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-mini/mini.diff" ,
    "MeanderingProgrammer/render-markdown.nvim",
  },
  keys = {
    {
      "<leader>AA",
      "<cmd>CodeCompanionChat Toggle<cr>",
      desc = "CodeComanion Toggle Buffer",
      mode = { "n" },
    },
    {
      "<leader>AT",
      "<cmd>CodeCompanionChat Add<cr>",
      desc = "CodeCompanion add visual selection as context",
      mode = { "v" },
    },
  },
  opts = {
    display = {
      chat = {
        window = {
          position = "right",
          width = 0.33,
        },
      },
    },
    strategies = {
      chat = {
        adapter = "copilot",
        model = "claude-sonnet-4.5",
        keymaps = {
          close = {
            modes = { n = "<leader>q" },
          },
        },
      },
    },
  },
}
