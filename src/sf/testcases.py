import io
from collections import Mapping
from difflib import context_diff, IS_CHARACTER_JUNK
from errno import EACCES
from glob import glob
from itertools import chain
from json import dumps
import os
from os.path import join, isfile, basename
from pipes import quote
import re
from shlex import split
import sys
from textwrap import dedent
from multiprocessing import Process, Queue
from Queue import Empty
from sf import DEFAULT_ENCODING, TEST_TIMEOUT, MAX_BYTES_READ, WronglyEncodedFile
from sf.solution import ExecutionException

def _encode(u):
    if u is None: return None
    return u.encode(DEFAULT_ENCODING)

def _decode(s):
    return s.decode(DEFAULT_ENCODING)

def _normalized_lines(u):
    if u is None: return u''
    if not u.endswith('\n'): u += '\n'
    return list(map(lambda _: _.rstrip() + '\n', dedent(u).splitlines(True)))

def timed_diffs(name, expected, actual):
    def _diffs(name, expected, actual, queue):
        expected = _normalized_lines(expected)
        actual = _normalized_lines(actual)
        expected_name = TestCase.FORMATS['expected'].format(name)
        actual_name = TestCase.FORMATS['actual'].format(name)
        diffs = list(context_diff(expected, actual, expected_name, actual_name))
        queue.put(u''.join(diffs) if diffs else None)
    q = Queue()
    p = Process(target = _diffs, args = (name, expected, actual, q))
    p.start()
    try:
        diffs = q.get(True, TEST_TIMEOUT)
    except Empty:
        p.terminate()
        return u'<<DIFFS TIMEOUT>>\n'
    p.join()
    return diffs


class TestCase(object):

    KINDS = 'args input expected actual errors diffs'.split() # kept internally as unicode
    FORMATS = dict((kind, '{}-{{}}.txt'.format(kind)) for kind in KINDS)
    GLOBS = dict((kind, '{}-*.txt'.format(kind)) for kind in KINDS)
    TEST_NUM_RE = re.compile(r'(?:{})-(.+)\.txt'.format('|'.join(KINDS)))

    @staticmethod
    def u2args(u):
        if u:
            return map(_decode, split(_encode(u), posix=True))
        else:
            return None

    @staticmethod
    def args2u(args):
        if args:
            return _decode(' '.join(map(quote, map(_encode, args))) + '\n')
        else:
            return None

    def __init__(self, name, path = None):
        self.name = name
        if path is None:
            for kind in TestCase.KINDS: setattr(self, kind, None)
            return
        for kind in TestCase.KINDS:
            case_path = join(path, TestCase.FORMATS[kind].format(name))
            if isfile(case_path):
                try:
                    with io.open(case_path, 'r', encoding = DEFAULT_ENCODING) as f: data = f.read(MAX_BYTES_READ)
                except UnicodeDecodeError:
                    raise WronglyEncodedFile(case_path)
                if kind == 'args': data = TestCase.u2args(data)
            else:
                data = None
            setattr(self, kind, data)

    def _fill(self, solution, kind, timeout = 0):
        setattr(self, kind, None)
        result = solution.run(self.args, self.input, timeout) # should we encode/decode here?
        if result.exception:
            raise result.exception
        if result.returncode:
            raise ExecutionException('Exit status: {} (non-zero), errors: "{}"'.format(result.returncode, result.stderr))
        setattr(self, kind, _decode(result.stdout))

    def fill_expected(self, solution, timeout = 0):
        self._fill(solution, 'expected', timeout)
        self.errors = None
        self.diffs = None

    def fill_actual(self, solution):
        try:
            self._fill(solution, 'actual', TEST_TIMEOUT)
        except ExecutionException as e:
            self.diffs = None
            self.errors = u'[{}] {}\n'.format(type(e).__name__, str(e).rstrip())
        else:
            self.diffs = timed_diffs(self.name, self.expected, self.actual)
            self.errors = None

    # writes members to files
    # non-empty members are written if:
    #  - the file does not exists, or
    #  - overwrite is true, and the existing file is writable
    # empty (None) members determine the deletion of the file if:
    #  - overwrite is true, and the existing file is writable
    def write(self, path, overwrite = False):
        written = []
        for kind in TestCase.KINDS:
            data = getattr(self, kind)
            case_path = join(path, TestCase.FORMATS[kind].format(self.name))
            if data is None:
                if overwrite and os.access(case_path, os.W_OK):
                    os.unlink(case_path)
                    written.append('- {}'.format(basename(case_path)))
                continue
            if kind == 'args': data = TestCase.args2u(data)
            if overwrite or not isfile(case_path):
                try:
                    with io.open(case_path, 'w', encoding = DEFAULT_ENCODING) as f: f.write(data)
                    written.append('+ {}'.format(basename(case_path)))
                except IOError as e:
                    if e.errno == EACCES and isfile(case_path): pass
                    else: raise
        return written

    def to_dict(self):
        result = {'name': self.name}
        for kind in TestCase.KINDS:
            data = getattr(self, kind)
            if kind == 'args': data = TestCase.args2u(data)
            result[kind] = data
        return result

    def __str__(self):
        parts = [ 'Name: ' + self.name]
        if self.args is not None:
            parts.append('Args: ' + ', '.join(map(_encode, self.args)))
        parts.extend('{}:\n{}'.format(kind.capitalize(), _encode(getattr(self, kind)).rstrip()) for kind in TestCase.KINDS[1:] if getattr(self,kind) is not None)
        return '\n'.join(parts)

class TestCases(Mapping):

    def __init__(self, path_or_dict = '.'):
        if isinstance(path_or_dict, dict):
            self.path = '<TAR_DATA>'
            self.cases = path_or_dict
        else:
            self.path = path_or_dict
            cases_paths = chain(*map(glob, (join(self.path, TestCase.GLOBS[kind]) for kind in TestCase.KINDS)))
            names = set()
            for case_path in cases_paths:
                names.add(TestCase.TEST_NUM_RE.match(basename(case_path)).group(1))
            self.cases = dict((name, TestCase(name, self.path)) for name in names)

    def __getitem__(self, key):
        return self.cases[key]

    def __len__(self):
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)

    def fill_actual(self, solution):
        n = 0
        for case in self.cases.values():
            case.fill_actual(solution)
            n += 1
        return n

    def fill_expected(self, solution, timeout = 0):
        for case in self.cases.values():
            case.fill_expected(solution, timeout)

    def write(self, path, overwrite = False):
        written = []
        for case in self.cases.values():
            written.extend(case.write(path, overwrite))
        return written

    def to_list_of_dicts(self):
        return [case.to_dict() for case in self.cases.values()]

    def __str__(self):
        result = [ 'Path: {}'.format(self.path) ]
        names = sorted(self.cases.keys())
        for name in names:
            result.append(str(self.cases[name]))
        return '\n\n'.join(result)
