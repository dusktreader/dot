return {
  "folke/sidekick.nvim",
  dependencies = {
    "folke/snacks.nvim",
  },
  opts = {
    nes = {
      enabled = false,
    },
    cli = {
      default = "opencode",
      tools = {
        opencode = {
          cmd = { "dt", "opencode", "launch", "--continue" },
        },
        work_opencode = {
          cmd = { "wdt", "opencode", "launch", "--continue" },
        },
      },
      context = {
        worktree_diff = function(ctx)
          return require("user.opencode").diff_context(ctx)
        end,
      },
    },
  },
  keys = {
    {
      "<leader>aa",
      function() require("user.opencode").select() end,
      desc = "Sidekick Toggle CLI",
    },
    {
      "<leader>ad",
      function() require("user.opencode").toggle({ focus = true }, "opencode") end,
      desc = "Sidekick Personal OpenCode",
    },
    {
      "<leader>aw",
      function() require("user.opencode").toggle({ focus = true }, "work_opencode") end,
      desc = "Sidekick Work OpenCode",
    },
    {
      "<leader>as",
      function() require("sidekick.cli").select() end,
      -- Or to select only installed tools:
      -- require("sidekick.cli").select({ filter = { installed = true } })
      desc = "Select CLI",
    },
    {
      "<leader>at",
      function() require("user.opencode").send({ msg = "{this}" }) end,
      mode = { "n" },
      desc = "Send This",
    },
    {
      "<leader>at",
      function() require("user.opencode").send_selection() end,
      mode = { "x" },
      desc = "Send Selection to opencode",
    },
    {
      "<leader>ar",
      function() require("user.opencode").review_staged() end,
      mode = { "n" },
      desc = "Review staged diff in opencode",
    },
    {
      "<leader>af",
      function() require("user.opencode").send({ msg = "{file}" }) end,
      desc = "Send File",
    },
    -- Example of a keybinding to open Claude directly
    {
      "<leader>ac",
      function() require("user.opencode").toggle({ focus = true }) end,
      desc = "Sidekick Toggle opencode",
    },
  },
}
