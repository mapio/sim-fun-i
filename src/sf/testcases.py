from collections import Mapping
from concurrent.futures import ThreadPoolExecutor, TimeoutError
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
from queue import Empty
from sf import DEFAULT_ENCODING, TEST_TIMEOUT, MAX_BYTES_READ, deread
from sf.solution import ExecutionException

def _normalized_lines(u):
    if u is None: return ''
    if not u.endswith('\n'): u += '\n'
    return list([_.rstrip() + '\n' for _ in dedent(u).splitlines(True)])

def timed_diffs(name, expected, actual):
    def _diffs():
        diffs = list(context_diff(
          _normalized_lines(expected),
          _normalized_lines(actual),
          TestCase.FORMATS['expected'].format(name),
          TestCase.FORMATS['actual'].format(name)
        ))
        return ''.join(diffs) if diffs else None
    with ThreadPoolExecutor(max_workers=1) as tpe:
      diffs = tpe.submit(_diffs)
      try:
        return diffs.result(TEST_TIMEOUT)
      except TimeoutError:
        return '<<DIFFS TIMEOUT>>\n'


class TestCase(object):

    KINDS = 'args input expected actual errors diffs'.split() # kept internally as unicode
    FORMATS = dict((kind, '{}-{{}}.txt'.format(kind)) for kind in KINDS)
    GLOBS = dict((kind, '{}-*.txt'.format(kind)) for kind in KINDS)
    TEST_NUM_RE = re.compile(r'(?:{})-(.+)\.txt'.format('|'.join(KINDS)))

    @staticmethod
    def str2args(s):
        return list(split(s, posix=True)) if s is not None else None

    @staticmethod
    def args2str(args):
        return (' '.join(map(quote, args)) + '\n') if args is not None else None

    def __init__(self, name, path = None):
        self.name = name
        if path is None:
            for kind in TestCase.KINDS: setattr(self, kind, None)
            return
        for kind in TestCase.KINDS:
            case_path = join(path, TestCase.FORMATS[kind].format(name))
            if isfile(case_path):
                data = deread(case_path, MAX_BYTES_READ)
                if kind == 'args': data = TestCase.str2args(data)
            else:
                data = None
            setattr(self, kind, data)

    @classmethod
    def from_dict(cls, dct):
        tc = cls(dct['name'])
        for kind in TestCase.KINDS:
            try:
                data = dct[kind]
                if kind == 'args': data = TestCase.str2args(data)
                setattr(tc, kind, data)
            except KeyError:
                pass
        return tc

    def _fill(self, solution, kind, timeout = None):
        setattr(self, kind, None)
        result = solution.run(self.args, self.input, timeout)
        if result.exception:
            raise result.exception
        if result.returncode:
            raise ExecutionException('Exit status: {} (non-zero), errors: "{}"'.format(result.returncode, result.stderr))
        setattr(self, kind, result.stdout)

    def fill_expected(self, solution, timeout = None):
        self._fill(solution, 'expected', timeout)
        self.errors = None
        self.diffs = None

    def fill_actual(self, solution):
        try:
            self._fill(solution, 'actual', TEST_TIMEOUT)
        except (ExecutionException, UnicodeError) as e:
            self.diffs = None
            self.errors = '[{}] {}\n'.format(type(e).__name__, str(e).rstrip())
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
            if kind == 'args': data = TestCase.args2str(data)
            if overwrite or not isfile(case_path):
                try:
                    with open(case_path, 'w', encoding = DEFAULT_ENCODING, errors = 'ignore') as f: f.write(data)
                    written.append('+ {}'.format(basename(case_path)))
                except IOError as e:
                    if e.errno == EACCES and isfile(case_path): pass
                    else: raise
        return written

    def to_dict(self, kinds_to_skip = ()):
        result = {'name': self.name}
        for kind in TestCase.KINDS:
            if kind in kinds_to_skip: continue
            data = getattr(self, kind)
            if kind == 'args': data = TestCase.args2str(data)
            result[kind] = data
        return result

    def __str__(self):
        parts = [ 'Name: ' + self.name]
        if self.args is not None:
            parts.append('Args: ' + ', '.join(self.args))
        parts.extend('{}:\n{}'.format(kind.capitalize(), getattr(self, kind).rstrip()) for kind in TestCase.KINDS[1:] if getattr(self,kind) is not None)
        return '\n'.join(parts)

class TestCases(Mapping):

    def __init__(self, path = None):
        self.path = path
        if path is None:
            self.cases = {}
            return
        cases_paths = chain(*list(map(glob, (join(self.path, TestCase.GLOBS[kind]) for kind in TestCase.KINDS))))
        names = set()
        for case_path in cases_paths:
            names.add(TestCase.TEST_NUM_RE.match(basename(case_path)).group(1))
        self.cases = dict((name, TestCase(name, self.path)) for name in names)

    @classmethod
    def from_list_of_dicts(cls, lst):
        tcs = TestCases()
        for cases_dict in lst:
            tc = TestCase.from_dict(cases_dict)
            tcs.cases[tc.name] = tc
        return tcs

    def __getitem__(self, key):
        return self.cases[key]

    def __len__(self):
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)

    def fill_actual(self, solution):
        n = 0
        for case in list(self.cases.values()):
            case.fill_actual(solution)
            n += 1
        return n

    def fill_expected(self, solution, timeout = None):
        for case in list(self.cases.values()):
            case.fill_expected(solution, timeout)

    def write(self, path, overwrite = False):
        written = []
        for case in list(self.cases.values()):
            written.extend(case.write(path, overwrite))
        return written

    def to_list_of_dicts(self, kinds_to_skip = ()):
        return [case.to_dict(kinds_to_skip) for case in list(self.cases.values())]

    def __str__(self):
        result = [ 'Path: {}'.format(self.path) ]
        names = sorted(self.cases.keys())
        for name in names:
            result.append(str(self.cases[name]))
        return '\n\n'.join(result)
