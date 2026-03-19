return {
  desc = "Show a notification when a task starts",
  constructor = function()
    return {
      on_start = function(self, task)
        vim.notify("Task started: " .. task.name, vim.log.levels.INFO)
      end,
    }
  end,
}
