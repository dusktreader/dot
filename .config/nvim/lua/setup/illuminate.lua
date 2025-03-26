require('illuminate').configure({
  -- Disable illuminate in insert mode
  modes_denylist = { 'i' },
})
