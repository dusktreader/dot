-- Borrowed from: https://github.com/nvim-lualine/lualine.nvim/pull/1296#issuecomment-2376374266
function format(str, len)
  if string.len(str) > len then
    return string.sub(str,1,len/2) .. '…' .. string.sub(str, str:len()-len/2+1, str:len())
  else
    return str
  end
end

require('lualine').setup {
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
      statusline = 1000,
      tabline = 1000,
      winbar = 1000,
    }
  },
  sections = {
    lualine_a = {'mode'},
    --lualine_b = {'branch', 'diff', 'diagnostics'},
    lualine_b = {
      {
        'branch',
        fmt = function(str)
          return format(str, 32)
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
    --
    lualine_x = {'encoding', 'fileformat', 'filetype'},
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
}
