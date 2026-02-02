return {
  -- Testing in neovim
  "nvim-neotest/neotest",
  dependencies = {
    "nvim-neotest/nvim-nio",
    "nvim-lua/plenary.nvim",
    "antoinemadec/FixCursorHold.nvim",
    "nvim-treesitter/nvim-treesitter",
    "nvim-neotest/neotest-python",
    "nvim-neotest/neotest-jest",
    "nvim-neotest/neotest-plenary",
    "dusktreader/neotest-mocha",
    {
      "fredrikaverpil/neotest-golang",
      version = "*",
    },
    "MisanthropicBit/neotest-busted",
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
          go_test_args = {
            "-v",
            "-race",
            "-count=1",
            "-timeout=60s",
          },
          dap_go_enabled = true,
          testify_enabled = true,
          warn_test_name_dupes = true,
          warn_test_not_executed = true,
        }),
        require("neotest-jest")({
          dap = { justMyCode = false },
          jestCommand = "npm test --",
        }),
        require('neotest-mocha')({
          -- dap = { justMyCode = false },
          command = "npx mocha",
          command_args = function(context)
            local args = {
                "--require=babel-core/register",
                "--recursive",
                "--full-trace",
                "--reporter=json",
                "--reporter-options=output=" .. context.results_path,
                "--fgrep=" .. context.test_name,
                context.path,
            }
            return args
          end,
        }),
        require('neotest-busted')({
          local_luarocks_only = false,
        }),
      },
    })
  end,
}
