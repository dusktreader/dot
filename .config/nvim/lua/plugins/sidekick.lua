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
          cmd = { "opencode", "--continue" },
        },
      },
    },
  },
  keys = {
    {
      "<leader>aa",
      function() require("sidekick.cli").toggle({ name = "opencode" }) end,
      desc = "Sidekick Toggle CLI",
    },
    {
      "<leader>as",
      function() require("sidekick.cli").select() end,
      -- Or to select only installed tools:
      -- require("sidekick.cli").select({ filter = { installed = true } })
      desc = "Select CLI",
    },
    {
      "<leader>ad",
      function() require("sidekick.cli").close() end,
      desc = "Detach a CLI Session",
    },
    {
      "<leader>at",
      function() require("sidekick.cli").send({ msg = "{this}" }) end,
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
      function() require("sidekick.cli").send({ msg = "{file}" }) end,
      desc = "Send File",
    },
    -- Example of a keybinding to open Claude directly
    {
      "<leader>ac",
      function() require("sidekick.cli").toggle({ name = "opencode", focus = true }) end,
      desc = "Sidekick Toggle opencode",
    },
  },
}
