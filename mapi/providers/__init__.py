# coding=utf-8

"""Provides a high-level interface for metadata media providers."""

from mapi import log
from mapi.exceptions import MapiException
from mapi.providers._provider import Provider
from mapi.providers.omdb import OMDb
from mapi.providers.tmdb import TMDb
from mapi.providers.tvdb import TVDb

__all__ = [
    "API_TELEVISION",
    "API_MOVIE",
    "API_ALL",
    "OMDb",
    "TMDb",
    "TVDb",
    "has_provider",
    "has_provider_support",
    "provider_factory",
]


API_TELEVISION = {"tvdb"}
API_MOVIE = {"tmdb", "omdb"}
API_ALL = API_TELEVISION | API_MOVIE


def has_provider(provider):
    """Verifies that module has support for requested API provider."""
    return provider.lower() in API_ALL


def has_provider_support(provider, media_type):
    """Verifies if API provider has support for requested media type."""
    if provider.lower() not in API_ALL:
        return False
    provider_const = "API_" + media_type.upper()
    return provider in globals().get(provider_const, {})


def provider_factory(provider, **options):
    """Factory function for DB Provider concrete classes."""
    providers = {"tmdb": TMDb, "tvdb": TVDb, "omdb": OMDb}
    try:
        return providers[provider.lower()](**options)
    except KeyError:
        msg = "Attempted to initialize non-existing DB Provider"
        log.error(msg)
        raise MapiException(msg)
