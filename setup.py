# coding=utf-8

from distutils.core import setup

setup(
    author='Jessy Williams',
    author_email='jessy@jessywilliams.com',
    description='An API for media database APIs which allows you to search ' +
                'for metadata using a simple, common interface',
    license='MIT',
    name='mapi',
    packages=['mapi'],
    install_requires=[
        'mock;python_version<"3"',
        'unittest2;python_version<"3"',
        'requests',
        'requests_cache'
    ],
    url='https://github.com/jkwill87/mapi',
    version='0.1'
)
