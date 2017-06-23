from distutils.core import setup

from mapi.__about__ import *

setup(
    name=ABOUT_TITLE,
    version=ABOUT_VERSION,
    packages=[ABOUT_TITLE],
    url=ABOUT_URL,
    license=ABOUT_LICENSE,
    author=ABOUT_AUTHOR,
    author_email=ABOUT_EMAIL,
    description=ABOUT_DESCRIPTION,
    requires=['requests', 'requests_cache'],
    copyright=ABOUT_COPYRIGHT
)
