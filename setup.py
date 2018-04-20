#!/usr/bin/env python
# coding=utf-8

from unittest import TestLoader

from setuptools import setup

from mapi import IS_PY2

with open('readme.md', 'r') as fp:
    LONG_DESCRIPTION = fp.read()


def test_suite():
    test_loader = TestLoader()
    return test_loader.discover('tests', pattern='test_*.py')


setup(
    author='Jessy Williams',
    author_email='jessy@jessywilliams.com',
    description=(
        'An API for media database APIs which allows you to search for metadata'
        'using a simple, common interface'
    ),
    include_package_data=True,
    install_requires=[
        'appdirs>=1.4',
        'requests>=2.18',
        'requests_cache>=0.4'
    ],
    license='MIT',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    name='mapi',
    packages=['mapi'],
    tests_require=['mock>=2', 'unittest2>=1.1'] if IS_PY2 else [],
    test_suite="setup.test_suite",
    url='https://github.com/jkwill87/mapi',
    version='3.1.1'
)
