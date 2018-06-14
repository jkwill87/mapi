#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

from mapi.__version__ import VERSION

with open('readme.md', 'r') as fp:
    LONG_DESCRIPTION = fp.read()

with open('requirements.txt', 'r') as fp:
    REQUIREMENTS = fp.read().splitlines()

setup(
    author='Jessy Williams',
    author_email='jessy@jessywilliams.com',
    description=(
        'Python library which provides a high-level interface for media '
        'database providers, allowing users to search for television and movie '
        'metadata using a simple interface'
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
