return {
  -- code formatting
  "stevearc/conform.nvim",
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
