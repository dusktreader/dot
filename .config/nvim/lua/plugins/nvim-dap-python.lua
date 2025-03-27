return {
  -- Add a debugging adapter for Python (requires uv project)
  "mfussenegger/nvim-dap-python",
  config = function(_, opts)
    -- Note that opts isn't used by this fucking plugin
    require('dap-python').setup("uv")
  end,
}
