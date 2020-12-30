local util = vim.lsp.util
local timeout = 10000
local M = {}

local request_lsp = function(method, params, converter)
    local locations = {}
    local results = vim.lsp.buf_request_sync(0, method, params, timeout)

    for _, data in pairs(results) do
        if data.result then
            local location = converter(data.result)
            vim.list_extend(locations, location)
        end
    end

    return locations
end

M.diagnostics = function()
    local locations = {}

    for bufnr, items in pairs(vim.lsp.diagnostic.get_all()) do
        local filename = vim.api.nvim_buf_get_name(bufnr)
        for _, item in pairs(items) do
            table.insert(locations, {
                text = '[' .. item.source .. '] ' .. item.message,
                filename = filename,
                lnum = item.range.start.line + 1,
                col = item.range.start.character + 1,
            })
        end
    end

    return locations
end

M.references = function()
    local params = util.make_position_params()
    params.context = { includeDeclaration = true }

    return request_lsp('textDocument/references', params, util.locations_to_items)
end

M.document_symbols = function()
    local params = util.make_position_params()

    return request_lsp('textDocument/documentSymbol', params, util.symbols_to_items)
end

M.workspace_symbols = function()
    local params = { query = '' }
    return request_lsp('workspace/symbol', params, util.symbols_to_items)
end

M.code_actions = function()
    local params = vim.lsp.util.make_range_params()
    params.context = { diagnostics = vim.lsp.diagnostic.get_line_diagnostics() }

    return request_lsp('textDocument/codeAction', params, function(ret) return ret end)
end

return M
