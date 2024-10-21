local telescope = require('telescope')
local utils = require('telescope.utils')

telescope.setup {
    pickers = {
        find_files = {
            hidden = true,
            --cwd = utils.buffer_dir(),
        }
    }
}
