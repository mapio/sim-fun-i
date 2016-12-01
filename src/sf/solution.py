from collections import namedtuple
from glob import glob
import io
from os.path import isfile, basename, join
import re
from shlex import split
import subprocess
from threading import Timer

from sf import DEFAULT_ENCODING, TEST_TIMEOUT

Result = namedtuple('Result','returncode,stdout,stderr,exception')

class ExecutionException(Exception):
    pass

class NotCompiledException(ExecutionException):
    pass

class TimeoutException(ExecutionException):
    pass


def execute(cmd, args = None, input_data = None, timeout = 0, cwd = None): # I/O is in DEFAULT_ENCODING
    if args is None: args = []
    try:
        process = subprocess.Popen(cmd + args, stdin = subprocess.PIPE if input_data is not None else None, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = cwd)
    except OSError as e:
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

class Solution(object):

    def __init__(self, path):
        self.NAME = type(self).__name__
        self.path = path
        self.sources = map(basename, glob(join(path,self.SOURCES_GLOB)))
        main_source = []
        for name in self.sources:
            with io.open(join(path,name), 'rU', encoding = DEFAULT_ENCODING) as f: content = f.read()
            if self.MAIN_SOURCE_RE.search(content): main_source.append((name, content))
        self.main_source = main_source[0] if len(main_source) == 1 else None

    def run(self, args = None, input_data = None, timeout = 0): # I unicode, O utf-8
        input_data = input_data.encode(DEFAULT_ENCODING) if input_data is not None else None
        if not self.is_compiled(): raise NotCompiledException('Cannot find the compiled solution.')
        return execute(self.run_command, args, input_data, timeout = timeout, cwd = self.path)

    def __str__(self):
        return 'Lang: {}, Path: {}, Sources: {}'.format(self.NAME, self.path, ' ,'.join(self.sources))

from sf.lang import JavaSolution, CSolution, ShSolution

def autodetect_solution(path = '.'):
    for cls in JavaSolution, CSolution, ShSolution:
        solution = cls(path)
        if solution.main_source: return solution
    return None
