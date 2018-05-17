#!/usr/bin/env python
# Jessy Williams (jessy@jessywilliams.com) 2018

from __future__ import print_function
from builtins import input
from os import system as sh, getcwd, sep
from sys import argv

PROJECT = getcwd().split(sep)[-1].lower()
with open('version.txt', 'r') as version_txt:
    VERSION = float(version_txt.read(3))


def help():
    print("usage: ./tasks.py " + '|'.join(sorted(TASKS)))


def clean():
    sh(r'find . | grep -E "(__pycache__|\.pyc|\.pyo$|\.mapi\.sqlite)" | xargs rm -rfv')


def _bump(increment):
    new_version = VERSION + increment
    response = input('Bump from %s to %s? (y/n) ' % (VERSION, new_version))
    if not response.lower().strip().startswith('y'):
        print('aborting')
        return
    with open('version.txt', 'w') as version_txt:
        version_txt.write(str(new_version))
    sh('git commit -am "Minor version bump"')
    sh('git tag %s' % new_version)
    sh('git push --tags')
    sh('./setup.py sdist') # TODO: revise w/ wheel args
    sh('python -m twine upload dis/%s-%s-py2.py3-none-any.whl' % (PROJECT, new_version)) # TODO: revise


def bump_major():
    _bump(1.0)


def bump_minor():
    _bump(0.1)


def install():
    sh('pip install -q .')


def uninstall():
    sh('sudo -H pip -q uninstall -y mapi')

def test():
    sh('python -m unittest discover -v')

def version():
    print('%s version %s ' % (PROJECT, VERSION))


# Determine available tasks (e.g. any defined function not prefixed by an underscore)
def _fx(): pass
TASKS = {f.__name__:f for f in globals().values() if type(f) == type(_fx) and f.__name__[0] != '_'}

# Determine arguments
task_name = argv[1] if len(argv) == 2 else None

# Run task (defaulting to help in undefined)
TASKS.get(task_name, help)()
