# ============================================================================
# FILE: git/status.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys
import re

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource, AsyncKind
from denite.kind.file import Kind as File

STATUS_MAP = {
    ' ': ' ',
    'M': '~',
    'A': '+',
    'D': '-',
    'R': '→',
    'C': 'C',
    'U': 'U',
    '?': '?'
}


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/status'
        self.kind = Kind(vim)
        self.vars['command'] = ['git', 'status', '-suall']
        self.vars['highlight'] = {
            'Header': {'pattern': r'.*\s'},
            'File': {'pattern': r'\s\zs.*'},
            'Add': {'pattern': r'+', 'parent': 'Header', 'link': 'Keyword'},
            'Change':  {'pattern': r'\~', 'parent': 'Header', 'link': 'Type'},
            'Delete':  {'pattern': r'-', 'parent': 'Header', 'link': 'Special'},
            'Unknown':  {'pattern': r'?', 'parent': 'Header', 'link': 'Constant'},
        }

    def build_candidate(self, line, context):
        line = line.replace('\t', '  ')
        path = re.sub(r'.* -> ', '', line[3:])
        status = STATUS_MAP[line[0]] + STATUS_MAP[line[1]]
        word = '%s %s' % (status, line[3:])
        return {
            'word': word,
            'action__path': os.path.join(context['path'], path),
            'action__status': status,
        }


class Kind(AsyncKind, File):
    def __init__(self, vim):
        super(AsyncKind, self).__init__(vim)
        super(File, self).__init__(vim)

        self.name = 'git/status'
        self.default_action = 'open'
        self.persist_actions += ['commit', 'amend', 'add', 'reset']
        self.redraw_actions += ['commit', 'amend', 'add', 'reset']

    def action_commit(self, context):
        message = self.vim.call('input', 'message : ')
        self.run(['git', 'commit', '-m', message] + [target['action__path'] for target in context['targets']], context)

    def action_amend(self, context):
        self.run(['git', 'commit', '--amend', '--no-edit'] + [target['action__path'] for target in context['targets']], context)

    def action_add(self, context):
        self.run(['git', 'add'] + [target['action__path'] for target in context['targets']], context)

    def action_reset(self, context):
        for target in context['targets']:
            if target['action__status'] == '??':
                self.run(['git', 'clean', '-f', target['action__path']], context)
            elif target['action__status'][0] != ' ':
                self.run(['git', 'reset', 'HEAD', target['action__path']], context)
            elif target['action__status'][1] != ' ':
                self.run(['git', 'checkout', target['action__path']], context)

    def action_stash(self, context):
        message = self.vim.call('input', 'message : ')
        self.run(['git', 'stash', 'push', '-u', '-m', message] + [target['action__path'] for target in context['targets']], context)
        context['sources_queue'].append([{'name': 'git/stash', 'args': []}])

    def diff(self, option, context):
        files = [target['action__path'] for target in context['targets']]
        self.terminal('git difftool %s %s' % (option, ' '.join(files)), context)

    def action_diff(self, context):
        self.diff('', context)

    def action_diff_cached(self, context):
        self.diff('--cached', context)

    def patch(self, action, context):
        files = [target['action__path'] for target in context['targets']]
        self.terminal('git %s -p %s' % (action, ' '.join(files)), context)

    def action_patch(self, context):
        self.patch('add', context)

    def action_patch_reset(self, context):
        self.patch('reset', context)

    def action_preview(self, context):
        self.preview(['git', '-P', 'diff', context['targets'][0]['action__path']], context)
