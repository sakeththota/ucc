"""
ucccheck.py.

Simple check for correct output on a test for the frontend.

Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
"""

import sys
import re
from termcolor import colored

ERROR_PATTERN = re.compile(r'^Error \((\d*)\) at line (\d*): *')


def extract_info(line):
    """Extract phase and line information from an error message."""
    match = ERROR_PATTERN.match(line)
    return match.group(1, 2) if match else None


def main(filename):
    """Compare result of compiler frontend with expected output.

    filename is the name of the uC file for which to check output.
    """
    output = filename.replace('.uc', '.out')
    with open(output) as result_file,\
            open(output + '.correct') as correct_file:
        results = {extract_info(line)
                   for line in result_file.readlines()
                   if extract_info(line)}
        correct = {extract_info(line)
                   for line in correct_file.readlines()
                   if extract_info(line)}
        missing = correct - results
        extra = results - correct
        failed = len(missing) + len(extra)
        if missing:
            print('Missing errors:')
            for item in missing:
                print(colored('  Phase {}, line {}'.format(*item), 'yellow'))
        if extra:
            print('Extraneous errors:')
            for item in extra:
                print(colored('  Phase {}, line {}'.format(*item), 'blue'))
        if failed:
            print(colored('Test {0} failed.'.format(filename), 'red'))
            sys.exit(1)
        elif correct:
            print(colored('Test {0} passed.'.format(filename), 'green'))
            sys.exit(0)

    types = filename.replace('.uc', '.types')
    with open(types) as result_file, \
            open(types + '.correct') as correct_file:
        if result_file.read() != correct_file.read():
            print('Error: mismatch detected in types output for ' +
                  filename)
            print(('Run "diff {0} {0}.correct" to see ' +
                   'difference').format(types))
            print(colored('Test {0} failed.'.format(filename), 'red'))
            sys.exit(1)
        else:
            print(colored('Test {0} passed.'.format(filename), 'green'))
            sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1])
