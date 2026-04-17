return {
  "windwp/nvim-autopairs",
  event = "InsertEnter",
  opts = {
    check_ts = true, -- use treesitter to avoid pairing inside strings/comments
  },
}
