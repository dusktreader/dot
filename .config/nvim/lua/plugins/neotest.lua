return {
  -- Testing in neovim
  "nvim-neotest/neotest",
  dependencies = {
    "nvim-neotest/nvim-nio",
    "nvim-lua/plenary.nvim",
    "antoinemadec/FixCursorHold.nvim",
    "nvim-treesitter/nvim-treesitter",
    "nvim-neotest/neotest-python",
    "fredrikaverpil/neotest-golang",
    "nvim-neotest/neotest-jest",
    { "dusktreader/neotest-mocha", branch_name="feature/add-test-name-to-context" },
  },
  opts = {
    log_level = "DEBUG",
  },
  config = function(_, opts)
    require('neotest').setup({
      unpack(opts),
      adapters = {
        require("neotest-python")({
          dap = { justMyCode = false },
          args = {
            "--log-level=DEBUG",
            "--verbose",
            "--verbose",
          },
        }),
        require("neotest-golang")({
          -- dap = { justMyCode = false },
          args = {
            -- How to verbose?
          },
        }),
        require("neotest-jest")({
          dap = { justMyCode = false },
          jestCommand = "npm test --",
        }),
        -- require("neotest-plenary"),
        -- require("neotest-vim-test")({
        --   ignore_file_types = { "python", "vim", "lua" },
        -- }),
        require('neotest-mocha')({
          -- dap = { justMyCode = false },
          command = "npx mocha",
          command_args = function(context)
            return {
                "--require=babel-core/register",
                "--recursive",
                "--full-trace",
                "--reporter=json",
                "--reporter-options=output=" .. context.results_path,
                "--fgrep=" .. context.test_name,
                context.path,
            };
          end,
        }),
      },
    })
  end,
}
