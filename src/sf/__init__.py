from os import environ

DEFAULT_ENCODING = 'utf-8'
MAX_BYTES_READ = 1048576
TEST_TIMEOUT = int(environ.get('SIMFUNI_TIMEOUT', 1))
VERSION = '0.3.1-beta'

class WronglyEncodedFile(UnicodeError):
    pass
