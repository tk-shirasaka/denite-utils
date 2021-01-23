# ============================================================================
# FILE: utils.py
# AUTHOR: Takahiro Shirasaka <tk.shirasaka@gmail.com>
# License: MIT license
# ============================================================================

from denite.base.source import Base
from denite.base.kind import Base as Kind
from denite.process import Process


class BaseSource(Base):
    def highlight(self):
        for name, highlight in self.vars.get('highlight', {}).items():
            name = '%s%s' % (self.syntax_name, name)
            parent = '%s%s' % (self.syntax_name, highlight.get('parent', ''))
            if 'link' in highlight:
                self.vim.command('highlight default link %s %s' % (name, highlight['link']))
            self.vim.command('syntax match %s /%s/ contained containedin=%s' % (name, highlight['pattern'], parent))


class AsyncSource(BaseSource):
    def on_init(self, context):
        context['__proc'] = None

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def gather_candidates(self, context):
        if not context['__proc']:
            context['__proc'] = Process(self.build_command(context), context, context['path'])

        outs, errs = context['__proc'].communicate(0.5)

        if errs:
            self.error_message(context, errs)

        context['is_async'] = not context['__proc'].eof()

        if context['__proc'].eof():
            context['__proc'] = None

        if not outs:
            return []

        outs = outs if getattr(self, 'duplicatable', None) else list(dict.fromkeys(outs))
        candidates = [self.build_candidate(x, context) for x in outs]
        return [x for x in candidates if x]

    def build_command(self, context):
        return self.vars['command'] + [arg for arg in context['args'] if arg]

    def build_candidate(self, line, context):
        pass


class AsyncKind(Kind):
    def __init__(self, vim):
        super().__init__(vim)

        self._previewed_winid = 0
        self._previewed_target = {}

    def run(self, command, context):
        proc = Process(command, context, context['path'])
        while not proc.eof():
            outs, errs = proc.communicate(1)

            if len(errs):
                self.debug('\n'.join(errs).replace('\t', '    '))

    def terminal(self, command, context):
        self.vim.command('tabedit term://%s//0:%s' % (context['path'], command))
        self.vim.command('startinsert | autocmd BufEnter <buffer> startinsert | autocmd BufLeave <buffer> stopinsert')

    def preview(self, command, context):
        target = context['targets'][0]

        if not self.vim.call('executable', 'bat'):
            return

        prev_id = self.vim.call('win_getid')

        if self._previewed_winid:
            self.vim.call('win_gotoid', self._previewed_winid)
            if self.vim.call('win_getid') != prev_id:
                self.vim.command('close!')
            self.vim.call('win_gotoid', prev_id)
            self._previewed_winid = 0

            if self._previewed_target == target:
                # Close the window only
                return

        self.vim.call('denite#helper#preview_file', context, '')
        self.vim.call('termopen', command)

        self._add_previewed_buffer(self.vim.call('bufnr', '%'))
        self._previewed_winid = self.vim.call('win_getid')

        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def _add_previewed_buffer(self, bufnr):
        previewed_buffers = self.vim.vars['denite#_previewed_buffers']
        previewed_buffers[str(bufnr)] = 1
        self.vim.vars['denite#_previewed_buffers'] = previewed_buffers
