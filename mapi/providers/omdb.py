# coding=utf-8

from datetime import datetime as dt

from mapi.endpoints.omdb import *
from mapi.exceptions import MapiNotFoundException, MapiProviderException
from mapi.metadata.metadata_movie import MetadataMovie
from mapi.providers import Provider
from mapi.utils import year_expand

__all__ = ["OMDb"]


class OMDb(Provider):
    """Queries the OMDb API.
    """

    def __init__(self, **options):
        super(OMDb, self).__init__(**options)
        if not self.api_key:
            raise MapiProviderException("OMDb require API key")

    def search(self, id_key=None, **parameters):
        title = parameters.get("title")
        year = parameters.get("year")
        id_imdb = id_key or parameters.get("id_imdb")

        if id_imdb:
            results = self._lookup_movie(id_imdb)
        elif title:
            results = self._search_movie(title, year)
        else:
            raise MapiNotFoundException
        for result in results:
            yield result

    def _lookup_movie(self, id_imdb):
        response = omdb_title(self.api_key, id_imdb, cache=self._cache)
        try:
            date = dt.strptime(response["Released"], "%d %b %Y").strftime(
                "%Y-%m-%d"
            )
        except (KeyError, ValueError):
            if response.get("Year") in (None, "N/A"):
                date = None
            else:
                date = "%s-01-01" % response["Year"]
        meta = MetadataMovie(
            title=response["Title"],
            date=date,
            synopsis=response["Plot"],
            id_imdb=id_imdb,
        )
        if meta["synopsis"] == "N/A":
            del meta["synopsis"]
        yield meta

    def _search_movie(self, title, year):
        year_from, year_to = year_expand(year)
        found = False
        page = 1
        page_max = 10  # each page yields a maximum of 10 results
        while True:
            try:
                response = omdb_search(
                    api_key=self.api_key,
                    media_type="movie",
                    query=title,
                    page=page,
                    cache=self.cache,
                )
            except MapiNotFoundException:
                break
            for entry in response["Search"]:
                if year_from <= int(entry["Year"]) <= year_to:
                    for result in self._lookup_movie(entry["imdbID"]):
                        yield result
                    found = True
            if page >= page_max:
                break
            page += 1
        if not found:
            raise MapiNotFoundException
