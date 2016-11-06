from sys import stderr

from colorama import Fore, Style

from sf.lang import autodetect_language

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    lang = autodetect_language('.')
    stderr.write(Fore.BLUE + _('Using {} processor…\n').format(lang.NAME) + Style.RESET_ALL)
    result = lang.compile()
    if result.returncode:
        stderr.write(_('Compilation errors encountered:'))
        print result.stderr,
    else:
        stderr.write(Fore.BLUE + _('Succesfully compiled sources: {}\n').format(', '.join(lang.sources)) + Style.RESET_ALL)
