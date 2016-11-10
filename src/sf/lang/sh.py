from os.path import isfile, join
import re

from sf.solution import Solution, Result, execute

class ShSolution(Solution):
    SOURCES_GLOB = '*.sh'
    MAIN_SOURCE_RE = re.compile(r'.*')
    def __init__(self, path):
        super(ShSolution, self).__init__(path)
        self.run_command = ['bash', self.main_source]
    def compile(self):
        return Result(None,None,None,0)
    def is_compiled(self):
        return True
