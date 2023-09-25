import re
from typing import List, Dict, Tuple, Sized, Iterable, Iterator
from .helper import subprocess_readlines, get_changed_files


class ShiftedLines(Sized, Iterable):
    def __init__(self, src_path: str, dst_path: str) -> None:
        self.src_path = src_path
        self.dst_path = dst_path
        self.__lines: 'Dict[int, int | None]' = {}

    def __setitem__(self, src_line_index, dst_line_index) -> None:
        self.__lines[src_line_index] = dst_line_index

    def __contains__(self, src_line_index) -> bool:
        return src_line_index in self.__lines and self.__lines[src_line_index] is not None

    def __getitem__(self, src_line_index) -> 'int | None':
        if src_line_index not in self.__lines:
            return None
        return self.__lines[src_line_index]

    def __iter__(self) -> 'Iterator[Tuple[int, int | None]]':
        return iter(self.__lines.items())

    def __len__(self) -> int:
        return len(self.__lines)


class LineShiftChecker:
    SUBMODULE_MODE = '160000'
    DIFF_BLOCK_REGEX = r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@'

    def __init__(self, revision_since: str, revision_until: str) -> None:
        self.revision_since = revision_since
        self.revision_until = revision_until

    def get_all_shifted_lines(self) -> Dict[str, ShiftedLines]:
        return {file_info['src']: self.__get_shifted_lines_in_file(file_info)
                for file_info in self.__get_changed_files()}

    def __get_changed_files(self) -> List[Dict]:
        return [file_info for file_info in get_changed_files(self.revision_since, self.revision_until, diff_filter='MR')
                if file_info['mode_src'] != LineShiftChecker.SUBMODULE_MODE]

    def __get_shifted_lines_in_file(self, file_info: Dict[str, str]) -> ShiftedLines:
        process_output = subprocess_readlines(['git', 'diff',
                                               self.revision_since, self.revision_until, '--',
                                               file_info['src'], file_info['dst']])

        shifted_lines = ShiftedLines(file_info['src'], file_info['dst'])
        src_line_index = 1
        dst_line_index = 1
        diff_started = False
        for line in process_output:
            matches = re.search(LineShiftChecker.DIFF_BLOCK_REGEX, line)
            if matches:
                diff_block_src_start = int(matches.group(1))
                diff_block_dst_start = int(matches.group(3))

                # fill shifted lines between 2 diff blocks
                for i in range(0, diff_block_src_start - src_line_index):
                    shifted_lines[src_line_index+i] = dst_line_index+i

                src_line_index = diff_block_src_start
                dst_line_index = diff_block_dst_start
                diff_started = True
                continue

            if not diff_started:
                continue

            if line.startswith(' '):
                shifted_lines[src_line_index] = dst_line_index
                src_line_index += 1
                dst_line_index += 1
            elif line.startswith('+'):
                dst_line_index += 1
            elif line.startswith('-'):
                shifted_lines[src_line_index] = None
                src_line_index += 1

        # fill shifted lines until end of file
        lines_in_source_file = self.__count_lines_in_source_file(file_info['src'])
        for i in range(0, lines_in_source_file - src_line_index + 1):
            shifted_lines[src_line_index+i] = dst_line_index+i

        assert lines_in_source_file == len(shifted_lines)

        return shifted_lines

    def __count_lines_in_source_file(self, file: str) -> int:
        process_output = subprocess_readlines(['git', 'show', f'{self.revision_since}:{file}'])
        return sum(1 for _ in process_output)
