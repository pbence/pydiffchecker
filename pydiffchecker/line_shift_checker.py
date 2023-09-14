import re
from typing import List, Dict
from .helper import subprocess_readlines


class LineShiftChecker:
    DIFF_BLOCK_REGEX = r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@'

    def __init__(self, revision_since, revision_until) -> None:
        self.revision_since = revision_since
        self.revision_until = revision_until

    def get_shifted_lines(self) -> Dict[str, Dict]:
        shifted_lines = {}

        for file_info in self.__get_changed_files():
            shifted_lines[file_info['src']] = self.__get_shifted_lines_in_file(file_info)

        return shifted_lines

    def __get_changed_files(self) -> List[Dict]:
        process_output = subprocess_readlines(['git', 'diff', '--name-status', '--diff-filter=MR',
                                               self.revision_since, self.revision_until])

        file_list = []
        for line in process_output:
            raw_file_info = line.split()
            file_list.append({
                'src': raw_file_info[1],
                'dst': raw_file_info[2] if len(raw_file_info) > 2 else raw_file_info[1],
            })

        return file_list

    def __get_shifted_lines_in_file(self, file_info) -> 'Dict[str, str | None]':
        process_output = subprocess_readlines(['git', 'diff',
                                               self.revision_since, self.revision_until, '--',
                                               file_info['src'], file_info['dst']])

        diff_started = False
        shifted_lines = {}
        old_start = 1
        new_start = 1
        for line in process_output:
            matches = re.search(LineShiftChecker.DIFF_BLOCK_REGEX, line)
            if matches:
                diff_block_src_start = int(matches.group(1))
                diff_block_dst_start = int(matches.group(3))

                # fill shifted lines between 2 diff blocks
                for i in range(0, diff_block_src_start - old_start):
                    shifted_lines[f'{file_info["src"]}:{old_start+i}'] = f'{file_info["dst"]}:{new_start+i}'

                old_start = diff_block_src_start
                new_start = diff_block_dst_start
                diff_started = True
                continue

            if not diff_started:
                continue

            if line.startswith(' '):
                shifted_lines[f'{file_info["src"]}:{old_start}'] = f'{file_info["dst"]}:{new_start}'
                old_start += 1
                new_start += 1
            elif line.startswith('+'):
                new_start += 1
            elif line.startswith('-'):
                shifted_lines[f'{file_info["src"]}:{old_start}'] = None
                old_start += 1

        # fill shifted lines until end of file
        lines_in_source_file = self.__count_lines_in_source_file(file_info['src'])
        for i in range(0, lines_in_source_file - old_start + 1):
            shifted_lines[f'{file_info["src"]}:{old_start+i}'] = f'{file_info["dst"]}:{new_start+i}'

        assert lines_in_source_file == len(shifted_lines)

        return shifted_lines

    def __count_lines_in_source_file(self, file) -> int:
        process_output = subprocess_readlines(['git', 'show', f'{self.revision_since}:{file}'])
        return sum(1 for _ in process_output)
