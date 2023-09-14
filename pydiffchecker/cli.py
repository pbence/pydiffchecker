import argparse
from .version import get_version
from .line_shift_checker import LineShiftChecker


def main() -> None:
    parser = argparse.ArgumentParser(description='Diff checker')

    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=f'v{get_version()}')
    parser.add_argument('revision_since')
    parser.add_argument('revision_until')

    args = parser.parse_args()

    line_shift_checker = LineShiftChecker(args.revision_since, args.revision_until)
    all_shifted_lines = line_shift_checker.get_all_shifted_lines()

    for src_path, shifted_lines in all_shifted_lines.items():
        print(f'* {src_path}->{shifted_lines.dst_path}:')
        for src_line_index, dst_line_index in shifted_lines:
            print(f'    {src_line_index}->{dst_line_index}')
