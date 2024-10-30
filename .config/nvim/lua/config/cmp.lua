local cmp = require('cmp')

cmp.setup({
  sources = {
    {name = 'nvim_lsp'},
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
