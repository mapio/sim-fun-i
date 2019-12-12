# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from sys import stderr, exit

from colorama import Fore, Style

from sf.solution import autodetect_solution

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def detect_and_compile(path, compile = True, quiet = False):
    solution = autodetect_solution(path)
    if solution.main_source is None:
        stderr.write(Fore.RED + _('No main source file found!\n') + Style.RESET_ALL)
        exit(1)
    if not quiet: stderr.write(Fore.BLUE + _('Using processor: {}\n').format(solution.NAME) + Style.RESET_ALL)
    if compile:
        result = solution.compile()
        if result.returncode:
            stderr.write(Fore.RED + _('Compilation errors encountered:\n') + Style.RESET_ALL)
            stderr.write(result.stderr.decode('utf-8'))
            exit(1)
        if not quiet: stderr.write(Fore.BLUE + _('Succesfully compiled sources: {}\n').format(', '.join(solution.sources)) + Style.RESET_ALL)
    return solution

def main():
    parser = ArgumentParser( prog = 'sf compile' )
    parser.add_argument('--solution-dir', '-s', help = 'The directory where the solution is to be found.', default = '.')
    args = parser.parse_args()

    detect_and_compile(args.solution_dir)
