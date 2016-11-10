from os.path import isfile, join
import re

from sf.solution import Solution, execute

class CSolution(Solution):
    SOURCES_GLOB = '*.c'
    MAIN_SOURCE_RE = re.compile(r'int\s+main')
    def __init__(self, path):
        super(CSolution, self).__init__(path)
        self.run_command = ['./soluzione']
    def compile(self):
        return execute(['gcc', '-o', 'soluzione'], args = self.sources, cwd = self.path)
    def is_compiled(self):
        return isfile(join(self.path, 'soluzione'))
