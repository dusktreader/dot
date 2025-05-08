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
    dap.configurations.python = {
      {
        type = 'python',
        request = 'attach',
        host = '127.0.0.1',
        port = 5678,
      },
    }
    dap.listeners.before.attach["dap-view-config"] = function() dapview.open() end
    dap.listeners.before.launch["dap-view-config"] = function() dapview.open() end
    dap.listeners.before.event_terminated["dap-view-config"] = function() dapview.close() end
    dap.listeners.before.event_exited["dap-view-config"] = function() dapview.close() end end
}
