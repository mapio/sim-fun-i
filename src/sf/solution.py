from collections import namedtuple
from glob import glob
from os.path import isfile, basename, join
import re
from shlex import split
import subprocess
from threading import Timer

from sf import DEFAULT_ENCODING, TEST_TIMEOUT, deread

Result = namedtuple('Result','returncode,stdout,stderr,exception')


class ExecutionException(Exception):
    pass


class NotCompiledException(ExecutionException):
    pass


class TimeoutException(ExecutionException):
    pass

def execute(cmd, args = None, input_data = None, timeout = None, cwd = None):
    if args is None: args = []
    try:
        process = subprocess.run(cmd + args, encoding = DEFAULT_ENCODING, input = input_data, capture_output = True, timeout = timeout, cwd = cwd)
    except OSError as e:
        return Result(None, None, None, exception = e)
    except subprocess.TimeoutExpired as e:
        return Result(None, None, None, exception = TimeoutException('{}s timeout exceeded'.format(timeout)))
    return Result(process.returncode, process.stdout, process.stderr, None)

class Solution(object):

    def __init__(self, path):
        self.NAME = type(self).__name__
        self.path = path
        self.sources = list(map(basename, glob(join(path, self.SOURCES_GLOB))))
        main_source = []
        for name in self.sources:
            content = deread(join(path, name))
            if self.MAIN_SOURCE_RE.search(content): main_source.append((name, content))
        self.main_source = main_source[0] if len(main_source) == 1 else None
        self.run_command = None

    def run(self, args = None, input_data = None, timeout = None):
        if self.run_command is not None:
            if not self.is_compiled(): raise NotCompiledException('Cannot find the compiled solution.')
            return execute(self.run_command, args, input_data, timeout = timeout, cwd = self.path)
        else:
            return Result(1, '', '<<NOTHING TO RUN>>', None)

    def __str__(self):
        return 'Lang: {}, Path: {}, Sources: {}, Run command: {}'.format(self.NAME, self.path, self.sources, self.run_command)

class NoSolution(Solution):
    def __init__(self):
        self.NAME = type(self).__name__
        self.sources = None
        self.main_source = None

from sf.lang import JavaTestRunnerSolution, JavaSolution, CSolution, ShSolution

def autodetect_solution(path = '.', allow_unexecutable = False):
    for cls in JavaTestRunnerSolution, JavaSolution, CSolution, ShSolution:
        solution = cls(path)
        if (solution.sources and allow_unexecutable) or (solution.run_command is not None): return solution
    return NoSolution()
