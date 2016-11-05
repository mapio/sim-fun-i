from sys import argv

from sf.lang import JavaLang

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    jl = JavaLang('.')
    result = jl.run(argv[1:])
    if result.exception:
        print result.exception
    elif result.returncode:
        print result.stderr
    else:
        print result.stdout
