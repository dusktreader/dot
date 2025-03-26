require("dropbar").setup({
    sources = {
      path = {
        relative_to = function(_, _)
          local wsf = vim.lsp.buf.list_workspace_folders()
          if next(wsf) ~= nil then
            return wsf[1]
          end

          return vim.fn.getcwd()
        end,
      },
    },
})
