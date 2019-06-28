# coding=utf-8

from abc import abstractmethod
from os import environ
from re import match

from mapi.compatibility import AbstractClass, ustr

__all__ = ["Provider"]


class Provider(AbstractClass):
    """ ABC for Providers, high-level interfaces for metadata media providers
    """

    def __init__(self, **options):
        """ Initializes the provider

        :param options: Optional kwargs; see below..
        """
        cls_name = self.__class__.__name__
        self._api_key = options.get(
            "api_key", environ.get("API_KEY_%s" % cls_name.upper())
        )
        self._cache = options.get("cache", True)

    @staticmethod
    def _year_expand(s):
        """ Parses a year or dash-delimited year range
        """
        regex = r"^((?:19|20)\d{2})?(\s*-\s*)?((?:19|20)\d{2})?$"
        try:
            start, dash, end = match(regex, ustr(s)).groups()
            start = start or 1900
            end = end or 2099
        except AttributeError:
            return 1900, 2099
        return (int(start), int(end)) if dash else (int(start), int(start))

    @abstractmethod
    def search(self, id_key=None, **parameters):
        pass

    @property
    def api_key(self):
        return self._api_key

    @property
    def cache(self):
        return self._cache
