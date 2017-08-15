# coding=utf-8

""" Exceptions used by mapi
"""


class MapiException(Exception):
    """ Base exception for the mapi package.
    """


class MapiNetworkException(MapiException):
    """ Raised when a network request is unaccepted; ie. no internet connection.
    """


class MapiNotFoundException(MapiException):
    """ Raised when a lookup or search works as expected yet yields no results.
    """


class MapiProviderException(MapiException):
    """ Raised when an endpoint has been used improperly, i.e. invalid API key,
    missing or conflicting parameters.
    """
