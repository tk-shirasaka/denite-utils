# ============================================================================
# FILE: lsp/code_actions.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

from denite.base.source import Base as BaseSource
from denite.base.kind import Base as BaseKind


class Source(BaseSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'lsp/code_actions'
        self.kind = Kind(vim)

    def gather_candidates(self, context):
        candidates = self.vim.call('luaeval', 'require("denite-utils.lsp").code_actions()')
        return [{
            'word': x['title'],
            'action__command': x,
        } for x in candidates]


class Kind(BaseKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'docker/image'
        self.default_action = 'run'

    def action_run(self, context):
        target = context['targets'][0]
        self.vim.exec_lua('vim.lsp.buf.execute_command(...)', target['action__command'])
