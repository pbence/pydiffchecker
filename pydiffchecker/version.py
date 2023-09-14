from importlib.metadata import version, PackageNotFoundError


def get_version():
    try:
        return version('pydiffchecker')
    except PackageNotFoundError:
        # package is not installed
        return '0.0.0'
