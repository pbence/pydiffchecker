import setuptools

from pydiffchecker.git_version import get_version

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pydiffchecker',
    version=get_version(),
    url='https://git.esoko.eu/bence/pydiffchecker.git',
    author='Bence Pocze',
    author_email='bence@pocze.ch',
    description='Wrappers for git diff',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['pydiffchecker=pydiffchecker.cli:main'],
    },
    python_requires='>=3.8',
    install_requires=[]
)
