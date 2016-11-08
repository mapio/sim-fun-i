import io
from collections import Mapping
from difflib import context_diff, IS_CHARACTER_JUNK
from glob import glob
from itertools import chain
from json import dumps
from os.path import join, isfile, basename
from pipes import quote
import re
from shlex import split
from textwrap import dedent

from sf.solution import ExecutionException

DEFAULT_ENCODING = 'utf-8'
TEST_TIMEOUT = 1
MAX_BYTES_READ = 1024 * 1024

def _encode(u):
    if u is None: return u''
    return u.encode(DEFAULT_ENCODING)

def _decode(s):
    return s.decode(DEFAULT_ENCODING)

def _normalized_lines(u):
    if not u.endswith('\n'): u += '\n'
    return list(map(lambda _: _.rstrip() + '\n', dedent(u).splitlines(True)))

class TestCase(object):

    KINDS = 'args input output actual errors diffs'.split() # kept internally as unicode
    FORMATS = dict((kind, '{}-{{}}.txt'.format(kind)) for kind in KINDS)
    GLOBS = dict((kind, '{}-*.txt'.format(kind)) for kind in KINDS)
    TEST_NUM_RE = re.compile(r'(?:{})-(.+)\.txt'.format('|'.join(KINDS)))

    def __init__(self, path, name):
        self.name = name
        for kind in TestCase.KINDS:
            case_path = join(path, TestCase.FORMATS[kind].format(name))
            if isfile(case_path):
                with io.open(case_path, 'rU', encoding = DEFAULT_ENCODING) as f: data = f.read(MAX_BYTES_READ)
                if kind == 'args': data = map(_decode, split(_encode(data), posix=True))
            else:
                data = None
            setattr(self, kind, data)

    def _fill(self, solution, kind, timeout = 0):
        result = solution.run(self.args, self.input, timeout)
        if result.exception:
            raise result.exception
        if result.returncode:
            raise ExecutionException(result.stderr)
        setattr(self, kind, result.stdout.decode(DEFAULT_ENCODING))

    def fill_output(self, solution):
        self.output = None
        self._fill(solution, 'output')

    def fill_actual(self, solution):
        try:
            self._fill(solution, 'actual', TEST_TIMEOUT)
        except ExecutionException, e:
            self.actual = None
            self.errors = '[{}] {}\n'.format(type(e).__name__, str(e).rstrip())
        else:
            self.diffs = ''.join(context_diff(
                _normalized_lines(self.output), _normalized_lines(self.actual),
                TestCase.FORMATS['output'].format(self.name), TestCase.FORMATS['actual'].format(self.name)
            ))

    def write(self, path, overwrite = False):
        written = []
        for kind in TestCase.KINDS:
            data = getattr(self, kind)
            if data is None: continue
            if kind == 'args': data = _decode(' '.join(map(quote, map(_encode, data))) + '\n')
            case_path = join(path, TestCase.FORMATS[kind].format(self.name))
            if overwrite or not isfile(case_path):
                with io.open(case_path, 'w', encoding = DEFAULT_ENCODING) as f: f.write(data)
                written.append(basename(case_path))
        return written

    def to_dict(self):
        result = {}
        for kind in TestCase.KINDS:
            data = getattr(self, kind)
            if kind == 'args': data = _decode(' '.join(map(quote, map(_encode, data))) + '\n')
            result[kind] = data
        return result

    def __str__(self):
        parts = [ 'Name: ' + self.name]
        if self.args is not None:
            parts.append('Args: ' + ', '.join(map(_encode, self.args)))
        parts.extend('{}:\n{}'.format(kind.capitalize(), _encode(getattr(self, kind)).rstrip()) for kind in TestCase.KINDS[1:] if getattr(self,kind) is not None)
        return '\n'.join(parts)

class TestCases(Mapping):

    def __init__(self, path = '.'):
        self.path = path
        cases_paths = chain(*map(glob, (join(path, TestCase.GLOBS[kind]) for kind in TestCase.KINDS)))
        names = set()
        for case_path in cases_paths:
            names.add(TestCase.TEST_NUM_RE.match(basename(case_path)).group(1))
        self.cases = dict((name, TestCase(path,name)) for name in names)

    def __getitem__(self, key):
        return self.cases[key]

    def __len__(self):
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)

    def fill_actual(self, solution):
        for case in self.cases.values():
            case.fill_actual(solution)

    def fill_output(self, solution):
        for case in self.cases.values():
            case.fill_output(solution)

    def write(self, path, overwrite = False):
        written = []
        for case in self.cases.values():
            written.extend(case.write(path, overwrite))
        return written

    def json(self, path):
        result = [case.to_dict() for case in self.cases.values()]
        with io.open(path, 'w', encoding = DEFAULT_ENCODING) as f: f.write(dumps(result, ensure_ascii = False))
