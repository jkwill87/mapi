# coding=utf-8

from distutils.core import setup
from io import open

about = {
    'author': 'Jessy Williams',
    'author_email': 'jessy@jessywilliams.com',
    'description': 'An API for media database APIs which allows you to search '
        + 'for metadata using a simple, common interface',
    'license': 'MIT',
    'long_description': open('readme.rst', 'r').read(),
    'name': 'mapi',
    'packages': ['mapi'],
    'install_requires': [
        'appdirs',
        'requests',
        'requests_cache',
        'mock;python_version<"3"',
        'unittest2;python_version<"3"'
    ],
    'url': 'https://github.com/jkwill87/mapi',
    'version': '1.0.2'
}

setup(**about)
