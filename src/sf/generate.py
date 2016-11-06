from sys import argv, stderr

from colorama import Fore, Style

from sf.lang import autodetect_language

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    lang = autodetect_language('.')
    stderr.write(Fore.BLUE + _('Using {} processor…\n').format(lang.NAME) + Style.RESET_ALL)
    cases = lang.generate('.')
    stderr.write(Fore.BLUE + _('Generated cases: {}\n').format(', '.join(sorted(cases))) + Style.RESET_ALL)
