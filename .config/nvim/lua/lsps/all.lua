require("lsps.basedpyright")
require("lsps.default")
require("lsps.lua_ls")
require("lsps.gopls")
require("lsps.pylsp")
require("lsps.ts_ls")
require("lsps.typos")

vim.lsp.config("*", { capabilities = require("blink.cmp").get_lsp_capabilities(), })
vim.lsp.enable({
  "lemminx",
})
