require("config.globals")
require("config.options")

require("setup.lazy")

require("user.clipboard")
require("user.linelen")
require("user.keymap")
require("user.reload")

require("config.commands")

require("lsps.basedpyright")
require("lsps.default")
require("lsps.lua_ls")
require("lsps.gopls")
require("lsps.pylsp")
require("lsps.ts_ls")
require("lsps.typos")
