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
        doc_continue = {
          cmd = { "dt", "opencode", "launch", "--continue" },
        },
        doc_new = {
          cmd = { "dt", "opencode", "launch" },
        },
        doc_premium = {
          cmd = { "dt", "opencode", "launch", "--premium-ok" },
        },
        woc_continue = {
          cmd = { "wdt", "opencode", "launch", "--continue" },
        },
        woc_new = {
          cmd = { "wdt", "opencode", "launch" },
        },
        woc_premium = {
          cmd = { "wdt", "opencode", "launch", "--premium-ok" },
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
      "<leader>adc",
      function() require("user.opencode").toggle({ focus = true }, "doc_continue") end,
      desc = "Sidekick Personal OpenCode",
    },
    {
      "<leader>adn",
      function() require("user.opencode").toggle({ focus = true }, "doc_new") end,
      desc = "Sidekick Personal OpenCode",
    },
    {
      "<leader>adp",
      function() require("user.opencode").toggle({ focus = true }, "doc_premium") end,
      desc = "Sidekick Personal OpenCode",
    },
    {
      "<leader>awc",
      function() require("user.opencode").toggle({ focus = true }, "woc_continue") end,
      desc = "Sidekick New Personal OpenCode Session",
    },
    {
      "<leader>awn",
      function() require("user.opencode").toggle({ focus = true }, "woc_new") end,
      desc = "Sidekick Work OpenCode",
    },
    {
      "<leader>awp",
      function() require("user.opencode").toggle({ focus = true }, "woc_premium") end,
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
      "<leader>af",
      function() require("user.opencode").send({ msg = "{file}" }) end,
      desc = "Send File",
    },
    {
      "<leader>ar",
      function() require("user.opencode").review_staged() end,
      mode = { "n" },
      desc = "Review staged diff in opencode",
    },
  },
}
