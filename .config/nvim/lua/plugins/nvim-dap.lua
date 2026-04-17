return {
  "mfussenegger/nvim-dap",
  dependencies = {
    {
      "igorlfs/nvim-dap-view",
      opts = {}
    }, {
      "mfussenegger/nvim-dap-python",
      config = function(_, opts)
        -- Note that opts isn't used by this fucking plugin
        require('dap-python').setup("uv")
      end,
    }, {
      "leoluz/nvim-dap-go",
      opts = {
        tests = {
          verbose = true,
        }
      },
    },
  },
  keys = {
    { "<leader>db", function() require("dap").toggle_breakpoint() end,  desc = "DAP Toggle Breakpoint" },
    { "<leader>dc", function() require("dap").continue() end,           desc = "DAP Continue" },
    { "<leader>do", function() require("dap").step_over() end,          desc = "DAP Step Over" },
    { "<leader>di", function() require("dap").step_into() end,          desc = "DAP Step Into" },
    { "<leader>dO", function() require("dap").step_out() end,           desc = "DAP Step Out" },
    { "<leader>dt", function() require("dap-view").toggle() end,        desc = "DAP Toggle View" },
    {
      "<leader>dX",
      function()
        local dap = require("dap")
        local dapview = require("dap-view")
        dap.disconnect()
        dap.close()
        dapview.close()
      end,
      desc = "DAP Disconnect and Close",
    },
  },
  opts = {},
  config = function(_, opts)
    -- This fucking plugin doesn't use setup() for some reason
    local dap, dapview = require("dap"), require("dap-view")
    dap.set_log_level("WARN")
    dap.adapters["pwa-node"] = {
      type = "server",
      host = "localhost",
      port = "${port}",
      executable = {
        command = "node",
        args = { vim.fn.stdpath("data") .. "/mason/packages/js-debug-adapter/js-debug/src/dapDebugServer.js", "${port}" },
      },
    }
    dap.adapters.java = {
      type = "server",
      host = "localhost",
      port = "${port}",
      executable = {
        command = "node",
        args = { vim.fn.stdpath("data") .. "/mason/packages/js-debug-adapter/js-debug/src/dapDebugServer.js", "${port}" },
      },
    }
    dap.configurations.python = {
      {
        name = 'Attach to Python debugger',
        type = 'python',
        request = 'attach',
        host = '127.0.0.1',
        port = 5678,
        console = 'integratedTerminal',
      },
    }
    dap.configurations.javascript = {
      {
        name = 'Attach to Node debugger',
        type = 'pwa-node',
        request = 'attach',
        address = 'localhost',
        port = 9229,
        cwd = '${workspaceFolder}',
      },
      {
        name = 'Launch Node debugger',
        type = 'pwa-node',
        request = 'launch',
        program = '${file}',
        cwd = '${workspaceFolder}',
        sourceMaps = true,
      },
    }
    dap.configurations.typescript = {
      {
        name = 'Attach to Node debugger',
        type = 'pwa-node',
        request = 'attach',
        address = 'localhost',
        port = 9229,
        cwd = '${workspaceFolder}',
      },
      {
        name = 'Launch Node debugger',
        type = 'pwa-node',
        request = 'launch',
        program = '${file}',
        cwd = '${workspaceFolder}',
        sourceMaps = true,
        showGlobalVariables = false,
      },
    }
    dap.listeners.before.attach["dap-view-config"] = function() dapview.open() end
    dap.listeners.before.launch["dap-view-config"] = function() dapview.open() end
    dap.listeners.before.event_terminated["dap-view-config"] = function() dapview.close() end
    dap.listeners.before.event_exited["dap-view-config"] = function() dapview.close() end
  end
}
