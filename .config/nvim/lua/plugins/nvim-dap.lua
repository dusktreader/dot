return {
  "mfussenegger/nvim-dap",
  opts = {},
  config = function(_, opts)
    -- This fucking plugin doesn't use setup() for some reason
    local dap = require("dap")
    dap.set_log_level("DEBUG")
  end
}
