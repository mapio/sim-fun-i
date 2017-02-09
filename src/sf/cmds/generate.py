# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from sys import argv, stderr, exit

from colorama import Fore, Style

from sf.cmds.compile import detect_and_compile
from sf.solution import autodetect_solution, ExecutionException
from sf.testcases import TestCases

from sf.zipgettext import DEFAULT_GETTEXT
_ = DEFAULT_GETTEXT

def main():
    parser = ArgumentParser( prog = 'sf generate' )
    parser.add_argument('--solution-dir', '-s', help = 'The directory where the solution is to be found.', default = '.')
    parser.add_argument('--force-compile', '-f', help = 'Whether to force a compilation before generating the expected outputs.', default = False, action = 'store_true')
    parser.add_argument('--cases-dir', '-c', help = 'The directory where the test cases are to be found.')
    parser.add_argument('--expected-dir', '-o', help = 'The direcotry where to write the generated expected output files.')
    parser.add_argument('--no-overwrite', '-n', help = 'Whether to overwrite the expected output files, if present.', default = False, action = 'store_true')
    parser.add_argument('--timeout', '-t', help = 'The time allowed for a case generation (default: 0 meaning no timeout).', default = 0)
    parser.add_argument('--verbose', '-v', help = 'Whether to give verbose output.', default = False, action = 'store_true')
    args = parser.parse_args()
    if args.cases_dir is None: args.cases_dir = args.solution_dir
    if args.expected_dir is None: args.expected_dir = args.cases_dir

    solution = detect_and_compile(args.solution_dir, args.force_compile)

    cases = TestCases(args.cases_dir)
    try:
        cases.fill_expected(solution, int(args.timeout))
    except ExecutionException as e:
        stderr.write(Fore.RED + _('Execution returned the following errors:\n') + Style.RESET_ALL)
        stderr.write(str(e)+'\n')
        exit(1)
    stderr.write(Fore.BLUE + _('Generated expected output for cases: {}\n').format(', '.join(sorted(cases.keys()))) + Style.RESET_ALL)

    written = cases.write(args.expected_dir, not args.no_overwrite)
    if args.verbose:
        if written:
            stderr.write(Fore.BLUE + _('Modifiled files:\n') + Style.RESET_ALL)
            stderr.write('\t' + '\n\t'.join(written) + '\n')
        else:
            stderr.write(Fore.BLUE + _('No file has been modified!\n') + Style.RESET_ALL)
