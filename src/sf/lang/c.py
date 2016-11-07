from re import compile as recompile

from sf.solution import Solution, execute

class CSolution(Solution):
    SOURCES_GLOB = '*.c'
    MAIN_SOURCE_RE = recompile(r'int\s+main')
    def __init__(self, path):
        super(CSolution, self).__init__(path)
        self.run_command = ['./soluzione']
    def compile(self):
        return execute(['gcc', '-o', 'soluzione'], args = self.sources, cwd = self.path)
