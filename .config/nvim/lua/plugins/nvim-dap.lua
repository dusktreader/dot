return {
  "mfussenegger/nvim-dap",
  dependencies = {
    {
      "igorlfs/nvim-dap-view",
      opts = {

      }
    },
  },
  opts = {},
  config = function(_, opts)
    -- This fucking plugin doesn't use setup() for some reason
    local dap, dapview = require("dap"), require("dap-view")
    -- dap.set_log_level("DEBUG")
    dap.adapters["pwa-node"] = {
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
        processId = require('dap.utils').pick_process,
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
    dap.listeners.before.attach["dap-view-config"] = function() dapview.open() end
    dap.listeners.before.launch["dap-view-config"] = function() dapview.open() end
    dap.listeners.before.event_terminated["dap-view-config"] = function() dapview.close() end
    dap.listeners.before.event_exited["dap-view-config"] = function() dapview.close() end end
}
