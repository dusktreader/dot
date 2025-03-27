return {
  -- Highlight the currently selected word and show where else it's used
  "RRethy/vim-illuminate",
  opts = {
    -- Disable illuminate in insert mode
    modes_denylist = { 'i' },
  },
  config = function(_, opts)
    -- This fucking plugin uses `configure` instead of `setup` for some reason
    require('illuminate').configure(opts)
  end
}
