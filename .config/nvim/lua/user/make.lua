local M = {}

-- job table: cmd -> { job_id, term }
local jobs = {}
local current_cmd = nil

-- Parse make targets from the Makefile in cwd
local function get_targets()
  local makefile = vim.fn.getcwd() .. "/Makefile"
  if vim.fn.filereadable(makefile) == 0 then
    vim.notify("No Makefile found in " .. vim.fn.getcwd(), vim.log.levels.WARN)
    return {}
  end

  local targets = {}
  for line in io.lines(makefile) do
    local target = line:match("^([a-zA-Z0-9_%.%-%/][a-zA-Z0-9_%.%-%/]*)%s*:[^=]")
    if target and target ~= ".PHONY" then
      table.insert(targets, target)
    end
  end
  return targets
end

local function term_opts(id, cmd)
  local short_cwd = vim.fn.fnamemodify(vim.fn.getcwd(), ":~")
  return {
    id = "make:" .. id,
    interactive = true,
    auto_close = false,
    win = {
      position = "bottom",
      height = 20,
      wo = {
        winbar = " " .. short_cwd .. ":  " .. cmd,
      },
      on_buf = function(self)
        vim.api.nvim_create_autocmd("TermClose", {
          buffer = self.buf,
          once = true,
          callback = function()
            local code = vim.v.event.status
            local icon = code == 0 and "✓" or "✗"
            local msg = code == 0 and "succeeded" or ("failed (exit " .. code .. ")")
            vim.api.nvim_buf_set_lines(self.buf, -1, -1, false, {
              "",
              icon .. " " .. cmd .. " " .. msg,
            })
          end,
        })
      end,
    },
  }
end

local function run_command(cmd)
  -- If this command is already running, kill it first
  if jobs[cmd] then
    pcall(vim.fn.jobstop, jobs[cmd].job_id)
    jobs[cmd] = nil
  end

  local term = Snacks.terminal.open(cmd, term_opts(cmd, cmd))

  vim.defer_fn(function()
    if not (term and term.buf and vim.api.nvim_buf_is_valid(term.buf)) then return end

    local job_id = vim.b[term.buf].terminal_job_id
    jobs[cmd] = { job_id = job_id, term = term }

    -- Auto-scroll to bottom as output arrives
    vim.api.nvim_create_autocmd("TextChangedT", {
      buffer = term.buf,
      callback = function()
        local line_count = vim.api.nvim_buf_line_count(term.buf)
        for _, win in ipairs(vim.fn.win_findbuf(term.buf)) do
          vim.api.nvim_win_set_cursor(win, { line_count, 0 })
        end
      end,
    })
  end, 100)

  current_cmd = cmd
end

-- Pick a target with snacks, then run it
function M.run()
  local targets = get_targets()
  if #targets == 0 then return end

  Snacks.picker.select(targets, { prompt = "Make target" }, function(target)
    if target then
      run_command("make " .. target)
    end
  end)
end

-- Pick a target, edit the command, then run it
function M.run_edit()
  local targets = get_targets()
  if #targets == 0 then return end

  Snacks.picker.select(targets, { prompt = "Make target (edit before run)" }, function(target)
    if not target then return end
    vim.ui.input({
      prompt = "Command: ",
      default = "make " .. target,
    }, function(cmd)
      if cmd and cmd ~= "" then
        run_command(cmd)
      end
    end)
  end)
end

-- Toggle the current make terminal
function M.toggle()
  if current_cmd and jobs[current_cmd] then
    jobs[current_cmd].term:toggle()
  else
    vim.notify("No make job running", vim.log.levels.WARN)
  end
end

-- Show a picker to switch between running jobs
function M.pick()
  local running = {}
  for cmd, _ in pairs(jobs) do
    table.insert(running, cmd)
  end

  if #running == 0 then
    vim.notify("No make jobs running", vim.log.levels.WARN)
    return
  end

  if #running == 1 then
    current_cmd = running[1]
    jobs[current_cmd].term:focus()
    return
  end

  Snacks.picker.select(running, { prompt = "Running make jobs" }, function(cmd)
    if not cmd then return end
    current_cmd = cmd
    jobs[current_cmd].term:focus()
  end)
end

-- Kill the current make job
function M.kill()
  if not current_cmd or not jobs[current_cmd] then
    vim.notify("No make job running", vim.log.levels.WARN)
    return
  end

  local job_id = jobs[current_cmd].job_id
  local still_running = vim.fn.jobwait({ job_id }, 0)[1] == -1

  local function do_kill()
    pcall(vim.fn.jobstop, job_id)
    jobs[current_cmd] = nil
    current_cmd = nil
    vim.notify("make job killed", vim.log.levels.INFO)
  end

  if still_running then
    vim.ui.input({
      prompt = "Kill running job '" .. current_cmd .. "'? [y/N]: ",
    }, function(input)
      if input and input:lower() == "y" then
        do_kill()
      end
    end)
  else
    do_kill()
  end
end

vim.api.nvim_create_autocmd("VimLeavePre", {
  callback = function()
    for _, job in pairs(jobs) do
      pcall(vim.fn.jobstop, job.job_id)
    end
  end,
})

return M
