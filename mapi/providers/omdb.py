# coding=utf-8

from mapi.endpoints.omdb import *
from mapi.exceptions import (
    MapiException,
    MapiNotFoundException,
    MapiProviderException,
)
from mapi.providers import Provider

__all__ = ["OMDb"]


class OMDb(Provider):
    """
    Queries the OMDb API
    """

    def __init__(self, **options):
        super(OMDb, self).__init__(**options)
        if not self.api_key:
            raise MapiProviderException("OMDb require API key")

    def search(self, id_key=None, **parameters):
        title = parameters.get("title")
        series = parameters.get("series")
        season = parameters.get("season")
        episode = parameters.get("episode")
        year = parameters.get("year")

        if id_key:
            # simple lookup
            yield self._lookup_id_imdb(id_key)
        elif title:
            # search
            for hit in self._search_movie(title, year):
                yield hit
        elif season:
            # search
            for hit in self._search_television(series, season, episode, year):
                yield hit
        else:
            # not enough information provided to find anything
            raise MapiNotFoundException()

    def _lookup(self, id_imdb):
        response = omdb_title(self.api_key, id_imdb, cache=self._cache)
        # determine media type based on response
        media_type = response.get("Type")
        if media_type == "episode":
            pass
        elif media_type == "movie":
            pass
        else:
            raise MapiException("could not determine media type")
        # create response

    def _search_movie(self, title, year):
        pass

    def _search_television(self, series, season, episode, year):
        pass
