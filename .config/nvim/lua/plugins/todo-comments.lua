return {
  -- Highlight and find TODO and other similar comments
  'folke/todo-comments.nvim',
  event = "BufReadPost",
  dependencies = { 'nvim-lua/plenary.nvim' },
  opts = {},
}
