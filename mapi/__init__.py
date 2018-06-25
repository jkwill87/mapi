# coding=utf-8

"""
                       o
  _  _  _    __,    _
 / |/ |/ |  /  |  |/ \_|
   |  |  |_/\_/|_/|__/ |_/
                 /|
                 \|

mapi is an API for media database APIs which allows you to lookup and search for
metadata using simple, common interface.

See https://github.com/jkwill87/mapi for more information.

"""

import logging as _logging
import sys as _sys

# Set up logging
log = _logging.getLogger(__name__)
log.addHandler((_logging.StreamHandler()))
log.setLevel(_logging.DEBUG if 'pydevd' in _sys.modules else _logging.ERROR)
_logging.getLogger('requests').setLevel(_logging.CRITICAL)

ustr = type(u'')  # unicode string type
