vim.lsp.config(
  "ts_ls",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    filetypes = { "typescript", "typescriptreact", "typescript.tsx", "javascript" },
    exclude = {"node_modules"}
  }
)
vim.lsp.enable({"ts_ls"})
