return {
  -- code formatting
  "stevearc/conform.nvim",
  event = "BufWritePre",
  keys = {
    { "<leader>FF", function() require("conform").format() end, desc = "Conform Format Buffer", noremap = true },
  },
  opts = {
    formatters_by_ft = {
      lua = { "stylua" },
      python = { "ruff" },
      javascript = { "prettierd" },
      typescript = { "prettierd" },
      json = { "prettierd" },
    },
  },
}
