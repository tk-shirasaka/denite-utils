# ============================================================================
# FILE: git/branch.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

import os
import sys
import re

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from utils import AsyncSource, AsyncKind


class Source(AsyncSource):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/branch'
        self.kind = Kind(vim)
        self.vars['command'] = ['git', 'branch', '-avv', '--no-color']
        self.vars['highlight'] = {
            'Current': {'pattern': r'\*\s', 'link': 'Keyword'},
            'Remote': {'pattern': r'remotes\/.\{-} ', 'link': 'Special'},
            'Upstream': {'pattern': r'\[\zs.\{-}\ze[:\]]', 'link': 'Keyword'},
            'Behind': {'pattern': r' behind \d*\ze.\{-}\]', 'link': 'Type'},
            'Ahead': {'pattern': r' ahead \d*\ze.\{-}\]', 'link': 'Constant'},
            'Gone': {'pattern': r' gone\ze\]', 'link': 'Special'},
        }

    def build_candidate(self, line, context):
        match = re.search(r'^(.\s(remotes\/(.*?\/))?(.*?))\s', line)

        return {
            'abbr': line,
            'word': match.group(1),
            'action__remote': match.group(3) if match.group(3) else '',
            'action__branch': match.group(4),
        }


class Kind(AsyncKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/branch'
        self.default_action = 'open'
        self.persist_actions += ['open', 'new', 'push', 'rename', 'delete', 'merge', 'rebase']
        self.redraw_actions += ['open', 'new', 'push', 'rename', 'delete', 'merge', 'rebase']

    def action_open(self, context):
        self.run(['git', 'checkout', context['targets'][0]['action__branch']], context)

    def action_new(self, context):
        self.run(['git', 'checkout', '-b', self.vim.call('input', 'New branch : ')], context)

    def push(self, option, context):
        remote = self.vim.call('input', 'Remote name : ')
        for target in context['targets']:
            self.run(['git', 'push', '-u', remote, target['action__branch']] + option, context)

    def action_push(self, context):
        self.push([], context)

    def action_push_force(self, context):
        self.push(['-f'], context)

    def rename(self, option, context):
        for target in context['targets']:
            if target['action__remote']: continue

            branch = self.vim.call('input', 'New branch name : ', target['action__branch'])
            self.run(['git', 'branch', option, target['action__branch'], branch], context)

    def action_rename(self, context):
        self.rename('-m', context)

    def action_rename_force(self, context):
        self.rename('-M', context)

    def delete(self, option, context):
        for target in context['targets']:
            if target['action__remote'] and option == '-D':
                self.run(['git', 'push', target['action__remote'][:-1], ':%s' % target['action__branch']], context)
            elif not target['action__remote']:
                self.run(['git', 'branch', option, target['action__branch']], context)

    def action_delete(self, context):
        self.delete('-d', context)

    def action_delete_force(self, context):
        self.delete('-D', context)

    def action_merge(self, context):
        target = context['targets'][0]
        self.run(['git', 'merge',  '%s%s' % (target['action__remote'], target['action__branch'])], context)

    def action_rebase(self, context):
        target = context['targets'][0]
        self.run(['git', 'rebase', '%s%s' % (target['action__remote'], target['action__branch'])], context)

    def action_log(self, context):
        target = context['targets'][0]
        branch = '%s%s' % (target['action__remote'], target['action__branch'])
        context['sources_queue'].append([{'name': 'git/log', 'args': [branch]}])

    def action_preview(self, context):
        target = context['targets'][0]
        branch = '%s%s' % (target['action__remote'], target['action__branch'])
        self.preview_terminal(context, ['git', 'log', '--oneline', '--graph', branch], 'preview')
