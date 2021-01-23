# ============================================================================
# FILE: git/log.py
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

        self.name = 'git/log'
        self.kind = Kind(vim)
        self.vars['command'] = ['git', 'log', '--no-color', '--graph',
                                '--pretty=format:%h -%d %s (%cr) <%an>']
        self.vars['highlight'] = {
            'Ref': {'pattern': r'[0-9a-z]\{7,13\}', 'link': 'Title'},
            'Time': {'pattern': r'([^)]\{-})', 'link': 'Keyword'},
            'User': {'pattern': r'<[^>]\{-}>', 'link': 'Constant'},
        }
        self.duplicatable = True

    def build_command(self, context):
        if not len(context['args']) and self.vim.current.buffer.name:
            context['args'] = ['--follow', self.vim.current.buffer.name]
        return super().build_command(context)

    def build_candidate(self, line, context):
        match = re.search(r'([0-9A-Za-z]{6,13})\s-\s', line)

        return {
            'word': line,
            'action__commit': match.group(1) if match else None,
            'action__path': context['args'][-1] if '--follow' in context['args'] else '',
        }


class Kind(AsyncKind):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'git/log'
        self.default_action = 'narrow'
        self.persist_actions += ['checkout', 'cherrypick', 'reset']
        self.redraw_actions += ['checkout', 'cherrypick', 'reset']

    def action_narrow(self, context):
        target = context['targets'][0]
        args = []
        if target['action__commit']:
            args = [target['action__commit']]
            args += ['--follow', target['action__path']] if target['action__path'] else []
        context['sources_queue'].append([{'name': 'git/log', 'args': args}])

    def action_checkout(self, context):
        if context['targets'][0]['action__commit']:
            self.run(['git', 'checkout', '--detach', context['targets'][0]['action__commit']], context)

    def action_cherrypick(self, context):
        if context['targets'][0]['action__commit']:
            self.run(['git', 'cherry-pick', context['targets'][0]['action__commit']], context)

    def reset(self, option, context):
        if context['targets'][0]['action__commit']:
            self.run(['git', 'reset', option, context['targets'][0]['action__commit']], context)

    def action_reset(self, context):
        self.reset('--mixed', context)

    def action_reset_soft(self, context):
        self.reset('--soft', context)

    def action_reset_hard(self, context):
        self.reset('--hard', context)

    def action_diff(self, context):
        file = context['targets'][0]['action__path']
        commit1 = context['targets'][0]['action__commit']
        commit2 = context['targets'][1]['action__commit'] if len(context['targets']) > 1 else '%s~' % commit1

        if commit1 and commit2:
            self.terminal('git difftool %s..%s -- %s' % (commit2, commit1, file), context)

    def action_preview(self, context):
        self.preview(['git', '-P', 'show', '--stat', '--patch', context['targets'][0]['action__commit']], context)

    def action_blame(self, context):
        target = context['targets'][0]
        if target['action__commit'] and target['action__path']:
            filetype = self.vim.current.buffer.options['filetype']
            self.terminal('git blame %s -- %s' % (target['action__commit'], target['action__path']), context)
            self.vim.command('syntax on | set filetype=%s' % filetype)
