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
