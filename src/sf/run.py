from locale import getdefaultlocale

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT.gettext

def main():
    print _( "How fine is run" )
