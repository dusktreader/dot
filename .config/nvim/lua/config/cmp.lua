local cmp = require('cmp')
local lspkind = require("lspkind")

cmp.setup({
  sources = {
    {name = 'typos_lsp'},
    {name = 'nvim_lsp'},
    {name = 'copilot', group_index = 2},
  },
  formatting = {
    format = lspkind.cmp_format({
      mode ="symbol",
      symbol_map = {
        Copilot = ""
      },
    })
  },
  mapping = cmp.mapping.preset.insert({
    -- Navigate between completion items
    ['<tab>'] = cmp.mapping.select_next_item({behavior = 'select'}),
    ['<S-tab>'] = cmp.mapping.select_prev_item({behavior = 'select'}),

    -- `Enter` key to confirm completion
    ['<CR>'] = cmp.mapping.confirm({select = false}),

    -- Ctrl+Space to trigger completion menu
    ['<C-Space>'] = cmp.mapping.complete(),

    -- Scroll up and down in the completion documentation
    ['<C-u>'] = cmp.mapping.scroll_docs(-4),
    ['<C-d>'] = cmp.mapping.scroll_docs(4),
  }),
  snippet = {
    expand = function(args)
      vim.snippet.expand(args.body)
    end,
  },
  -- Automatically select the first suggestion
  completion = {
    completeopt = 'menu,menuone,noinsert', -- Show menu, even when there's only one item
  },
  -- To enable the first suggestion to be selected automatically
  experimental = {
    ghost_text = true, -- Optional: for ghost text
  },
  window = {
    completion = {
      border = 'rounded',
      scrollbar = '║',
    },
    documentation = {
      border = 'rounded',
      scrollbar = '║',
    },
  },
})
