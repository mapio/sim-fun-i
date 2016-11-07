from collections import namedtuple
from glob import glob
from os.path import isfile, basename, join
from re import compile as recompile
from shlex import split
import subprocess
from threading import Timer

Result = namedtuple('Result','returncode,stdout,stderr,exception')

class SourceNotFoundException(Exception):
    pass

class CompilationException(Exception):
    pass

class ExecutionException(Exception):
    pass

class TimeputException(ExecutionException):
    pass

def execute(cmd, args = None, input_data = None, timeout = 0, cwd = None):
    if args is None: args = []
    try:
        process = subprocess.Popen(cmd + args, stdin = subprocess.PIPE if input_data else None, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = cwd)
    except OSError, e:
        return Result(None, None, None, exception = e)
    if timeout:
        timer = Timer(timeout, process.kill)
        try:
            timer.start()
            stdout, stderr = process.communicate(input_data)
            if timer.is_alive():
                timer.cancel()
                return Result(process.returncode, stdout, stderr, None)
            return Result(None, None, None, exception = TimeputException)
        finally:
            timer.cancel()
    else:
        stdout, stderr = process.communicate(input_data)
        return Result(process.returncode, stdout, stderr, None)

TEST_TIMEOUT = 1

class Solution(object):

    INPUT_GLOB = 'input-*.txt'
    ARGS_GLOB = 'args-*.txt'
    OUTPUT_GLOB = 'output-*.txt'
    TEST_NUM_RE = recompile(r'(?:output|input|args)-(.+)\.txt')
    INPUT_FMT = 'input-{}.txt'
    ARGS_FMT = 'args-{}.txt'
    OUTPUT_FMT = 'output-{}.txt'
    ACTUAL_FMT = 'actual-{}.txt'

    def __init__(self, path):
        self.NAME = type(self).__name__
        self.path = path
        sources = glob(join(path,self.SOURCES_GLOB))
        main_source = []
        self.sources = []
        for source in sources:
            self.sources.append(basename(source))
            with open(source, 'rU') as f:
                for line in f:
                    if self.MAIN_SOURCE_RE.search(line):
                        main_source.append(basename(source))
        self.main_source = main_source[0] if len(main_source) == 1 else None

    def run(self, args = None, input_data = None, timeout = 0):
        return execute(self.run_command, args, input_data, timeout = timeout, cwd = self.path)

from sf.lang import JavaSolution, CSolution

def autodetect_solution(path = '.'):
    for cls in JavaSolution, CSolution:
        if glob(join(path,cls.SOURCES_GLOB)): return cls(path)
    raise SourceNotFoundException()
