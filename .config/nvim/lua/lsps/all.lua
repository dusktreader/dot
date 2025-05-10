require("lsps.basedpyright")
require("lsps.lua_ls")
require("lsps.gopls")
require("lsps.pylsp")
require("lsps.ts_ls")
require("lsps.typos")

vim.lsp.config("*", { capabilities = require("blink.cmp").get_lsp_capabilities(), })
vim.lsp.enable({
  "lemminx",
})

-- function RestartLSP()
--   vim.lsp.stop_client(vim.lsp.get_active_clients())
--   vim.cmd('edit')
-- end
--
-- vim.api.nvim_create_user_command('RestartLSP', function() RestartLSP() end, {})
