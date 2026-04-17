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
  keys = {
    { "<leader>t",  function() require("neotest").run.run() end,                                        desc = "Neotest Run Nearest" },
    { "<leader>T",  function() require("neotest").run.run(vim.fn.expand("%")) end,                      desc = "Neotest Run File" },
    { "<leader>TT", function() require("neotest").run.run(vim.uv.cwd()) end,                            desc = "Neotest Run All" },
    { "<leader>tl", function() require("neotest").run.run_last() end,                                   desc = "Neotest Run Last" },
    { "<leader>to", function() require("neotest").output.open({ enter = true, auto_close = true }) end, desc = "Neotest Output" },
    { "<leader>tp", function() require("neotest").output_panel.toggle() end,                            desc = "Neotest Output Panel" },
    { "<leader>ts", function() require("neotest").summary.toggle() end,                                 desc = "Neotest Summary" },
    { "<leader>tw", function() require("neotest").watch.toggle(vim.fn.expand("%")) end,                 desc = "Neotest Watch File" },
    { "<leader>td", function() require("neotest").run.run({ strategy = "dap" }) end,                   desc = "Neotest Run DAP" },
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
