import subprocess
from typing import Iterator


def subprocess_readlines(cmd, cwd=None) -> Iterator[str]:
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE)

    for line in process.stdout:
        line = line.decode().rstrip(r'\n')

        yield line

    process.wait()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)
