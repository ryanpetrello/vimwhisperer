from . import api

import vim


def complete():
    row, col = vim.current.window.cursor
    for line in api.complete(vim.current.buffer[row - 1]):
        vim.current.buffer.append(line)
