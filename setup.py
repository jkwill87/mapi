#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup
from mapi import IS_PY2

with open('readme.rst', 'r') as fp:
    LONG_DESCRIPTION = fp.read()

requirements = [
    'appdirs>=1.4',
    'requests>=2.18',
    'requests_cache>=0.4'
]

if IS_PY2:
    tests_require = [
        'mock>=2',
        'unittest2>=1.1'
    ]
else:
    tests_require = []

setup(
    author='Jessy Williams',
    author_email='jessy@jessywilliams.com',
    description=(
        'An API for media database APIs which allows you to search for metadata'
        'using a simple, common interface'
    ),
    install_requires=requirements,
    license='MIT',
    long_description=LONG_DESCRIPTION,
    name='mapi',
    packages=['mapi'],
    tests_require=tests_require,
    url='https://github.com/jkwill87/mapi',
    version='3.0.1'
)
