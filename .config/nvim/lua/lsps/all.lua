require("lsps.basedpyright")
require("lsps.lua_ls")
require("lsps.gopls")
require("lsps.pylsp")
require("lsps.ts_ls")
require("lsps.typos")
require("lsps.angularls")
require("lsps.lemminx")
require("lsps.ruff")

vim.api.nvim_create_autocmd('LspAttach', {
  desc = 'LSP actions',
  callback = function(event)
    vim.lsp.set_log_level("debug")
    local opts = {buffer = event.buf}

    vim.keymap.set('n', '<leader>K',  vim.lsp.buf.hover, opts)
    vim.keymap.set('n', '<leader>gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', '<leader>gD', vim.lsp.buf.declaration, opts)
    vim.keymap.set('n', '<leader>gi', vim.lsp.buf.implementation, opts)
    vim.keymap.set('n', '<leader>go', vim.lsp.buf.type_definition, opts)
    vim.keymap.set('n', '<leader>gr', vim.lsp.buf.references, opts)
    vim.keymap.set('n', '<leader>gs', vim.lsp.buf.signature_help, opts)
    vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
    vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
    vim.keymap.set({"n", "x"}, "<leader>FF", function() vim.lsp.buf.format({async = true}) end, opts)

  end,
})

function RestartLSP()
  vim.print("Restarting LSPs")
  vim.lsp.stop_client(vim.lsp.get_clients())
  vim.cmd.edit()
end

vim.api.nvim_create_user_command('RestartLSP', RestartLSP, {})
