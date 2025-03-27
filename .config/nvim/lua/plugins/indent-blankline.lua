return {
  -- Show the span of code blocks
  "lukas-reineke/indent-blankline.nvim",
  opts = {
    scope = {
      enabled = false,
    },
  },
  config = function(_, opts)
    require("ibl").setup(opts)
  end,
}
