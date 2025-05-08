vim.lsp.config(
  "ts_ls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    exclude = {"node_modules"}
  }
)
