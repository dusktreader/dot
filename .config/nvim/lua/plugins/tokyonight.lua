return {
  -- A nice color scheme
  "folke/tokyonight.nvim",
  opts = {
    style = "night",
    on_highlights = function(hl, colors)
      hl.Visual = { bg = colors.dark5 }
      hl.WinSeparator = { fg = colors.border_highlight }
    end
  },
}
