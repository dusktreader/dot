return {
  -- Auto-completion in neovim
  "saghen/blink.cmp",
  version = "1.*",
  opts = {
    completion = {
      menu = {
        border = 'rounded',
      },
      ghost_text = {
        enabled = true,
      },
      list = {
        selection = {
          auto_insert = false,
        },
      },
      documentation = {
        auto_show = true,
        auto_show_delay_ms = 500,
        window = {
          border = 'rounded',
          scrollbar = true,
        },
      },
    },
    keymap = {
      ['<tab>']      = { 'select_next',               'fallback' },
      ['<s-tab>']    = { 'select_prev',               'fallback' },
      ['<cr>']       = { 'accept',                    'fallback' },
      ['<s-space>']  = { 'hide',                      'fallback' },
      ['<c-space>']  = { 'show',                      'fallback' },
      ['<pageup>']   = { 'scroll_documentation_up',   'fallback' },
      ['<pagedown>'] = { 'scroll_documentation_down', 'fallback' },
    },
    sources = {
      default = { "lsp", "path", "buffer", "copilot"},
      providers = {
        lsp = {
          score_offset = 1,
        },
        path = {
          score_offset = 2,
        },
        buffer = {
          score_offset = 3,
        },
        copilot = {
          name = "copilot",
          module = "blink-copilot",
          score_offset = 4,
          enabled = true,
          async = true,
          opts = {},
        },
      },
    },
  },
}
