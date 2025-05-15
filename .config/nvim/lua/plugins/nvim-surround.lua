return {
  -- Surround
  "kylechui/nvim-surround",
  event = "VeryLazy",
  config = function()
    -- For some goddamned reason, this requires setup to be called explicitly
    require("nvim-surround").setup({})
  end,
}
