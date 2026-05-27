return {
  "folke/snacks.nvim",
  priority = 1000,
  lazy = false,
  opts = {
    picker = {
      enabled = true,
      -- Use snacks picker for all vim.ui.select calls
      ui_select = true,
    },
  },
  keys = {
    { "<leader>ff", function() Snacks.picker.files({ hidden = true }) end,  desc = "Find Files" },
    { "<leader>fg", function() Snacks.picker.grep() end,                    desc = "Live Grep" },
    { "<leader>fb", function() Snacks.picker.buffers() end,                 desc = "Buffers" },
    { "<leader>fh", function() Snacks.picker.help() end,                    desc = "Help Tags" },
    { "<leader>be", function() Snacks.picker.buffers() end,                 desc = "Buffer List" },
    { "<leader>sp", function() Snacks.picker.spelling() end,                desc = "Spell Suggest" },
  },
}
