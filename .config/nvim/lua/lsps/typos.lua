vim.lsp.config(
  "typos_lsp",
  {
    capabilities = require("blink.cmp").get_lsp_capabilities(),
    init_options = {
      config = "pyproject.toml",
    },
  }
)
