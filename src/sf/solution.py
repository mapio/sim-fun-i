from collections import namedtuple
from glob import glob
from os.path import isfile, basename, join
from re import compile as recompile
from shlex import split
import subprocess
from threading import Timer

Result = namedtuple('Result','returncode,stdout,stderr,exception')

class ExecutionException(Exception):
    pass

class NotCompiledException(ExecutionException):
    pass

class TimeoutException(ExecutionException):
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
            return Result(None, None, None, exception = TimeoutException('{}s timeout exceeded'.format(timeout)))
        finally:
            timer.cancel()
    else:
        stdout, stderr = process.communicate(input_data)
        return Result(process.returncode, stdout, stderr, None)

TEST_TIMEOUT = 1

class Solution(object):

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
        if not self.is_compiled(): raise NotCompiledException('Cannot find the compiled solution')
        return execute(self.run_command, args, input_data, timeout = timeout, cwd = self.path)

    def __str__(self):
        return 'Lang: {}, Path: {}, Sources: {}'.format(self.NAME, self.path, ' ,'.join(self.sources))

from sf.lang import JavaSolution, CSolution

def autodetect_solution(path = '.'):
    for cls in JavaSolution, CSolution:
        if glob(join(path,cls.SOURCES_GLOB)): return cls(path)
    return None
