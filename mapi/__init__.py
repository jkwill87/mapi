# coding=utf-8

""" mapi is an API for media database APIs which allows you to lookup and search
for metadata using simple, common interface.

See https://github.com/jkwill87/mapi for more information.
"""

import logging

from mapi.constants import *

# Set up logging
log = logging.getLogger(__name__)
log.addHandler((logging.StreamHandler()))
log.setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.CRITICAL)


def has_provider(provider):
    """ Verifies that module has support for requested API provider

    :param str provider: API constant or its corresponding value from API_ALL
    :return bool: True if package supports specified db provider, else False
    """
    return provider.lower() in API_ALL


def has_provider_support(provider, media_type):
    """ Verifies if API provider has support for requested media type

    :param str provider: API constant or its corresponding value from API_ALL
    :param str media_type: Media type constant or its corresponding value from
        MEDIA_TYPE_ALL
    :return bool: True if api provider is available and package supports
        media type, else False
    """
    if provider.lower() not in API_ALL:
        return False
    provider_const = 'API_' + media_type.upper()
    return provider in globals().get(provider_const, {})
