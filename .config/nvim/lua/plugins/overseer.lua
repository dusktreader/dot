return {
  "stevearc/overseer.nvim",
  opts = {
    component_aliases = {
      default = {
        "on_start_notify",
        { "on_complete_notify", statuses = { "FAILURE", "SUCCESS" } },
        "on_output_summarize",
        "on_exit_set_status",
        "on_complete_dispose",
      },
    },
  },
  keys = {
    { "<leader>mt", "<cmd>OverseerToggle<cr>",      desc = "Overseer: toggle task list" },
    { "<leader>mr", "<cmd>OverseerRun<cr>",         desc = "Overseer: run task" },
    { "<leader>mq", "<cmd>OverseerQuickAction<cr>", desc = "Overseer: quick action" },
  },
}
