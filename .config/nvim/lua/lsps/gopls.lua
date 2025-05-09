vim.lsp.config(
  "gopls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "go" },
    settings = {
      gopls = {
        staticcheck = true,
      },
    },
  }
)
vim.lsp.enable({"gopls"})
