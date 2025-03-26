require('mason-lspconfig').setup({
  ensure_installed = {
    'typos_lsp',
    'basedpyright',
    'gopls',
    'lua_ls',
  },
  handlers = {
    function(server_name)
      require('lspconfig')[server_name].setup({})
    end,
  },
})
