from os import environ
from pathlib import Path

DEFAULT_ENCODING = 'utf-8'
MAX_BYTES_READ = 1048576
TEST_TIMEOUT = int(environ.get('SIMFUNI_TIMEOUT', 1))
VERSION = '1.1.0'

def deread(path, max_bytes = None):
  with open(path, 'r', encoding = DEFAULT_ENCODING, errors = 'ignore') as f:
    if max_bytes is None: return f.read()
    else: return f.read(max_bytes)