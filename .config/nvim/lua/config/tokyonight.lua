require("tokyonight").setup({
  style = "night",
  on_highlights = function(hl, colors)
    hl.Visual = { bg = colors.dark5 }
  end
})
