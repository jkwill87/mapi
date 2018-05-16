#!/usr/bin/env python
# coding=utf-8

from unittest import TestLoader

from setuptools import setup

with open('readme.md', 'r') as fp:
    LONG_DESCRIPTION = fp.read()

with open('requirements.txt', 'r') as fp:
    REQUIREMENTS = fp.read().splitlines()

with open('version.txt', 'r') as fp:
    VERSION = float(fp.read())

setup(
    author='Jessy Williams',
    author_email='jessy@jessywilliams.com',
    description=(
        'An API for media database APIs which allows you to search for '
        'metadata using a simple, common interface'
    ),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='MIT',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    name='mapi',
    packages=['mapi'],
    url='https://github.com/jkwill87/mapi',
    version=VERSION
)
