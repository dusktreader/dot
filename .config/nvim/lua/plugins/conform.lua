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
      python = { "uv_ruff_format" },
      javascript = { "prettierd" },
      typescript = { "prettierd" },
      json = { "prettierd" },
    },
    formatters = {
      uv_ruff_format = {
        command = "uv",
        args = { "run", "ruff", "format", "--stdin-filename", "$FILENAME", "-" },
        cwd = function(_, ctx)
          return vim.fs.root(ctx.dirname, { "pyproject.toml", "uv.lock", ".git" })
        end,
      },
    },
  },
}
