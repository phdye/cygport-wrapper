# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from setuptools import setup, find_packages

import re

_version = re.search("^__version__\s*=\s*'(.*)'",
                     open('src/cygport/__init__.py').read(),
                     re.M ).group(1)

with open('README.rst', 'rb') as f:
    _long_description = f.read().decode('utf-8')

setup(
    name = 'cygport',
    version = _version,
    description = "cyport command wrapper : adds '.' & 'build'",
    author = 'Philip Dye',
    author_email = 'phdye@acm.org',
    url = 'http://github.com/phdye/cygport-helper',
    long_description = _long_description,
    packages = find_packages('src'),
    package_dir={'': 'src'},
    entry_points = {
        'console_scripts': ['cygport = cygport:main']
        },
)
