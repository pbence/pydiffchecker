import subprocess

GIT_DESCRIBE_COMMAND = ['git', 'describe', '--tags', '--long', '--dirty']
VERSION_FORMAT = '{tag}.dev{commitcount}+{gitsha}{dirty}'


def get_version() -> str:
    version = subprocess.check_output(GIT_DESCRIBE_COMMAND).decode().strip()
    return format_version(version=version)


def format_version(version: str) -> str:
    parts = version.split('-')
    dirty = len(parts) == 4
    tag, count, sha = parts[:3]
    tag = tag.lstrip('v')
    if count == '0' and not dirty:
        return tag
    return VERSION_FORMAT.format(
        tag=tag,
        commitcount=count,
        gitsha=sha.lstrip('g'),
        dirty='dirty' if dirty else ''
    )


if __name__ == '__main__':
    print(get_version())
