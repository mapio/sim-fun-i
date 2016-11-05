from sys import argv

from sf.lang import JavaLang

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    jl = JavaLang('.')
    print jl.test()
