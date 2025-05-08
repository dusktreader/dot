local exports = {}

function exports.set()
  local result = vim.system({"get-config-line-length"}, { text = true }):wait()
  vim.print(result)
  local line_length = tonumber(vim.trim(result["stdout"]))
  local range = {}
  for i=line_length + 1, 1335 do
    table.insert(range, i)
  end
  local columns = table.concat(range, ",")
  vim.opt.colorcolumn = columns
  vim.opt.textwidth = line_length
end

exports.set()

return exports
