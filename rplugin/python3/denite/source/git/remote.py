# ============================================================================
# FILE: git/remote.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource, AsyncKind


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/remote'
        self.kind = Kind(vim)
        self.vars['command'] = ['git', 'remote', 'show']

    def build_candidate(self, line, context):
        return {
            'word': line,
            'action__remote': line
        }


class Kind(AsyncKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/remote'
        self.default_action = 'sync'
        self.persist_actions += ['add', 'sync', 'rename', 'delete']
        self.redraw_actions += ['add', 'sync', 'rename', 'delete']

    def action_sync(self, context):
        for target in context['targets']:
            self.run(['git', 'remote', 'update', '--prune', target['action__remote']], context)
        context['sources_queue'].append([{'name': 'git/branch', 'args': []}])

    def action_add(self, context):
        self.run(['git', 'remote', 'add', self.vim.call('input', 'Name : '), self.vim.call('input', 'URL : ')], context)

    def action_rename(self, context):
        for target in context['targets']:
            remote = self.vim.call('input', 'New remote name : ', target['action__remote'])
            self.run(['git', 'remote', target['action__remote'], remote], context)

    def action_delete(self, context):
        for target in context['targets']:
            self.run(['git', 'remote', 'rm', target['action__remote']], context)
