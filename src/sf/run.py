from sys import argv, stderr

from colorama import Fore, Style

from sf.lang import autodetect_language

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    lang = autodetect_language('.')
    result = lang.run(argv[1:])
    if result.exception:
        stderr.write(Fore.RED + _('Exception raised during execution:\n') + Style.RESET_ALL)
        stderr.write(result.exception)
    elif result.returncode:
        stderr.write(Fore.RED + _('Execution returned non-zero exit code:\n') + Style.RESET_ALL)
        stderr.write(result.stderr)
    else:
        print result.stdout,
