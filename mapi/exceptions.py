# coding=utf-8


class MapiException(Exception):
    """ Base exception for the mapi module.
    """


class MapiError(MapiException):
    """ Raised when an endpoint fails, if its response is undefined, or if a
    precondition of the library is not satisfied, i.e. a DB provider changes
    its interface.
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
