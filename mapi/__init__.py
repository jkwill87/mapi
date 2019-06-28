# coding=utf-8

r"""
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

import logging
import sys

__all__ = ["log"]


log = logging.getLogger(__name__)
log.addHandler((logging.StreamHandler()))
log.setLevel(logging.INFO if "pydevd" in sys.modules else logging.ERROR)
logging.getLogger("requests").setLevel(logging.CRITICAL)
