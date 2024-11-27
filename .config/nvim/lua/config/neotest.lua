require("neotest").setup({
  log_level = "DEBUG",
  adapters = {
    require("neotest-python")({
      -- dap = { justMyCode = false },
      args = {
        "--log-level=DEBUG",
        "--verbose",
        "--verbose",
      },
    }),
    require("neotest-go")({
      -- dap = { justMyCode = false },
      args = {
        -- How to verbose?
      },
    }),
    -- require("neotest-plenary"),
    -- require("neotest-vim-test")({
    --   ignore_file_types = { "python", "vim", "lua" },
    -- }),
  },
})
