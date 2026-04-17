return {
  "nvim-neo-tree/neo-tree.nvim",
  branch = "v3.x",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-tree/nvim-web-devicons",
    "MunifTanjim/nui.nvim",
  },
  lazy = false,
  keys = {
    { "<leader>e",  ":Neotree<CR>",                                    desc = "Neotree Open",           noremap = true },
    { "<leader>E-", function() vim.cmd("split")  vim.cmd("Neotree") end, desc = "Neotree Horizontal Split", noremap = true },
    { "<leader>E|", function() vim.cmd("vsplit") vim.cmd("Neotree") end, desc = "Neotree Vertical Split",   noremap = true },
  },
  opts = {
    close_if_last_window = true,
    window = {
      width = 80,
    },
    filesystem = {
      follow_current_file = {
        enabled = true,
        leave_dirs_open = true,
      },
    },
    buffers = {
      follow_current_file = {
        enabled = true,
        leave_dirs_open = true,
      },
    },
    event_handlers = {
      {
        event = "file_opened",
        handler = function(file_path)
          require("neo-tree.command").execute({ action = "close" })
        end
      },
    },
  },
}
