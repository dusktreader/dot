return {
  "folke/snacks.nvim", -- already loaded, just hooking keymaps here
  keys = {
    { "<leader>mr", function() require("user.make").run() end,      desc = "Make: run target" },
    { "<leader>me", function() require("user.make").run_edit() end, desc = "Make: run target (edit command)" },
    { "<leader>mk", function() require("user.make").kill() end,     desc = "Make: kill job" },
    { "<leader>mt", function() require("user.make").toggle() end,   desc = "Make: toggle output" },
    { "<leader>mm", function() require("user.make").pick() end,     desc = "Make: switch between jobs" },
  },
}
