import argparse
import json
from .version import get_version
from .line_shift_checker import LineShiftChecker


def main():
    parser = argparse.ArgumentParser(description='Diff checker')

    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=f'v{get_version()}')
    parser.add_argument('revision_since')
    parser.add_argument('revision_until')

    args = parser.parse_args()

    line_shift_checker = LineShiftChecker(args.revision_since, args.revision_until)
    out = line_shift_checker.get_shifted_lines()

    print(json.dumps(out, indent=4))
