return {
  -- Show git status line-by-line in the gutter
  "lewis6991/gitsigns.nvim",
  event = "BufReadPost",
  opts = {
    signs = {
      add          = { text = "▎" },
      change       = { text = "▎" },
      delete       = { text = "" },
      topdelete    = { text = "" },
      changedelete = { text = "▎" },
      untracked    = { text = "▎" },
    },
  },
}
