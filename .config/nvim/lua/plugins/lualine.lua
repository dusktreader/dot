return {
  -- A really nice status line plugin
  "nvim-lualine/lualine.nvim",
  dependencies = {
    { "folke/tokyonight.nvim" },
  },
  config = function()
    -- CodeCompanion spinner for lualine
    local spinner_frames = { "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏" }
    local spinner_idx = 0
    local cc_active = false
    local spinner_timer = nil

    local function start_spinner()
      if spinner_timer then return end
      cc_active = true
      spinner_timer = vim.uv.new_timer()
      spinner_timer:start(0, 100, vim.schedule_wrap(function()
        spinner_idx = (spinner_idx + 1) % #spinner_frames
        vim.cmd("redrawstatus")
      end))
    end

    local function stop_spinner()
      if spinner_timer then
        spinner_timer:stop()
        spinner_timer:close()
        spinner_timer = nil
      end
      cc_active = false
      vim.cmd("redrawstatus")
    end

    vim.api.nvim_create_autocmd("User", {
      pattern = "CodeCompanionRequestStarted",
      callback = start_spinner,
    })
    vim.api.nvim_create_autocmd("User", {
      pattern = { "CodeCompanionRequestFinished", "CodeCompanionRequestCancelled" },
      callback = stop_spinner,
    })

    local function cc_status()
      if not cc_active then return "" end
      return spinner_frames[(spinner_idx % #spinner_frames) + 1] .. " CC"
    end

    require("lualine").setup({
      options = {
        icons_enabled = true,
        theme = 'tokyonight-night',
        component_separators = { left = '\u{E0B1}', right = '\u{E0B3}'},
        section_separators = { left = '\u{E0B0}', right = '\u{E0B2}'},
        disabled_filetypes = {
          statusline = {},
          winbar = {},
        },
        ignore_focus = {},
        always_divide_middle = true,
        globalstatus = false,
        refresh = {
          statusline = 100,
          tabline = 1000,
          winbar = 1000,
        }
      },
      sections = {
        lualine_a = {'mode'},
        lualine_b = {
          {
            'branch',
            fmt = function(str)
              -- Borrowed from: https://github.com/nvim-lualine/lualine.nvim/pull/1296#issuecomment-2376374266
              local len = 32
              if string.len(str) > len then
                return string.sub(str,1,len/2) .. '…' .. string.sub(str, str:len()-len/2+1, str:len())
              else
                return str
              end
            end
          },
          'diff',
        },
        lualine_c = {
          {
            'filename',
            path = 1,
          }
        },
        lualine_x = { cc_status, 'encoding', 'fileformat', 'filetype'},
        lualine_y = {'progress'},
        lualine_z = {'location'}
      },
      inactive_sections = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = {'filename'},
        lualine_x = {'location'},
        lualine_y = {},
        lualine_z = {}
      },
      tabline = {},
      winbar = {},
      inactive_winbar = {},
      extensions = {},
    })
  end,
}
