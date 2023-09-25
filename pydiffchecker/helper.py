import subprocess
from typing import Iterator


def subprocess_readlines(cmd, cwd=None) -> Iterator[str]:
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, text=True)

    for line in process.stdout:
        line = line.rstrip('\n')
        yield line

    process.communicate()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)


def get_changed_files(since, until, diff_filter=None, cwd=None):
    command = ['git', 'diff-tree', '-r']
    if diff_filter:
        command.extend([f'--diff-filter={diff_filter}'])
    command.extend([since, until])

    raw_diff = subprocess_readlines(command, cwd=cwd)
    return [parse_raw_file_info(raw_diff_entry)
            for raw_diff_entry in raw_diff]


def parse_raw_file_info(raw_diff_entry):
    diff_entry = raw_diff_entry.lstrip(':').split()

    mode_src = diff_entry[0]
    mode_dst = diff_entry[1]
    sha1_src = diff_entry[2]
    sha1_dst = diff_entry[3]
    status = diff_entry[4]
    src = diff_entry[5]
    dst = diff_entry[6] if len(diff_entry) > 6 else src

    return {
        'mode_src': mode_src,
        'mode_dst': mode_dst,
        'sha1_src': sha1_src,
        'sha1_dst': sha1_dst,
        'status': status,
        'src': src,
        'dst': dst
    }
