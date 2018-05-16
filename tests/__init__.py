import sys
from logging import getLogger
from warnings import catch_warnings, simplefilter

IS_PY2 = sys.version_info[0] == 2

if IS_PY2:
    from unittest2 import TestCase, skip
    from mock import patch
    reload(sys)
    sys.setdefaultencoding('utf-8')
else:
    from unittest import TestCase, skip
    from unittest.mock import patch

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with catch_warnings():
            if not IS_PY2:
                simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test

getLogger('mapi').disabled = True
