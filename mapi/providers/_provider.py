# coding=utf-8

from abc import abstractmethod
from os import environ

from mapi.compatibility import AbstractClass

__all__ = ["Provider"]


class Provider(AbstractClass):
    """ABC for Providers, high-level interfaces for metadata media providers.
    """

    def __init__(self, **options):
        """Initializes the provider."""
        cls_name = self.__class__.__name__
        self._api_key = options.get(
            "api_key", environ.get("API_KEY_%s" % cls_name.upper())
        )
        self._cache = options.get("cache", True)

    @abstractmethod
    def search(self, id_key=None, **parameters):
        pass

    @property
    def api_key(self):
        return self._api_key

    @property
    def cache(self):
        return self._cache
