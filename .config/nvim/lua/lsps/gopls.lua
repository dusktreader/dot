vim.lsp.config(
  "gopls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    settings = {
      gopls = {
        staticcheck = true,
      },
    },
  }
)
