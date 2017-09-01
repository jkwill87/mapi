# coding=utf-8

from distutils.core import setup
from io import open

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('readme.rst', 'r').read() as fp:
    long_description = fp.read()

about = {
    'author': 'Jessy Williams',
    'author_email': 'jessy@jessywilliams.com',
    'description': 'An API for media database APIs which allows you to search '
        + 'for metadata using a simple, common interface',
    'license': 'MIT',
    'long_description': long_description,
    'name': 'mapi',
    'packages': ['mapi'],
    'install_requires': required,
    'url': 'https://github.com/jkwill87/mapi',
    'version': '1.0.2'
}

setup(**about)
