# coding=utf-8

import re

from mapi import *
from mapi import endpoints
from mapi.constants import *
from mapi.exceptions import *
from mapi.utilities import filter_meta


def provider_factory(provider, **options):
    """
    Factory function for DB Provider Concrete Classes.

    :param provider: one of the constants contained within the API_ALL or their
        resolved value.
    :param dict options: Optional kwargs; passed on to class constructor.
    :keyword str api_key: Some API providers require an API key to use their
        service.
    :keyword int year_delta:  If set and a year is provided for a movie query,
        results will be filtered around this value inclusively.
    :keyword int max_hits: Will restrict the maximum number of responses for a
        search. If unset or None, searches yield as many as possible from the
        API provider.
    :raises MapiError: When db_provider is not one of the available classes from
        this module.
    :return object: One of this module's provider objects.
    """
    if not has_provider(provider):
        msg = 'Attempted to initialize non-existing DB Provider'
        log.error(msg)
        raise MapiException(msg)
    return {
        PROVIDER_IMDB: IMDb,
        # DB_TMDB: TMDb  # TODO
        # DB_TVDB: TVDb  # TODO
    }[provider.lower()](**options)


class IMDb:
    """
    Queries the unofficial IMDb mobile API.
    """

    def __init__(self, **options):
        """
        Initializes an IMDb provider.

        :param dict options: Optional kwargs; see below..
        :keyword int year_delta: If set and a year is provided for a movie
            query, results will be filtered around this value inclusively.
        :keyword int max_hits: Will restrict the maximum number of responses for
            a search. If unset or None, searches yield as many as possible from
            the API provider.
        """
        # Retrieve and set relevant parameters
        self.year_delta = options.get('year_delta', 5)
        self.max_hits = options.get('max_hits')

    def search(self, **parameters):
        """
        Searches IMDb for movie metadata.

        :param kwargs parameters: Search parameters.
        :keyword str id_imdb: IMDb primary key; must be prefixed with 'tt'.
        :keyword str title: Feature title.
        :keyword str or int: Feature year.
        :raises MapiException: Or one of its subclasses; see mapi/exceptions.py.
        :return list of dict: Movie metadata; see readme for mapping details.
        """

        # Process parameters
        parameters = {str(k): str(v) for k, v in parameters.items()}
        id_imdb = parameters.get('id_imdb')
        title = parameters.get('title')
        year = parameters.get('year')

        # Perform query for metadata
        if id_imdb:
            hits = self._search_id_imdb(id_imdb)
        elif title:
            hits = self._search_title(title)
            hits = filter_meta(hits, self.max_hits, self.year_delta, year)
        else:
            raise MapiProviderException
        if not hits:
            raise MapiNotFoundException
        return hits

    @staticmethod
    def _search_id_imdb(id_imdb):
        assert id_imdb

        response = endpoints.imdb_main_details(id_imdb)
        try:
            metadata = [{
                META_TITLE: response['data']['title'],
                META_YEAR: response['data']['year'],
                META_SYNOPSIS: response['data']['plot']['outline'],
                META_MEDIA: 'movie',
                META_ID_IMDB: response['data']['tconst']
            }]
        except KeyError:
            raise MapiProviderException
        return metadata

    @staticmethod
    def _search_title(title):
        assert title

        metadata = list()
        response = endpoints.imdb_mobile_find(title)
        entries = [entry for entries in response.values() for entry in entries]

        for entry in entries:
            year_match = re.search(r'(\d{4})', entry['title_description'])
            if not year_match:
                continue
            metadata.append({
                META_TITLE: entry['title'],
                META_YEAR: year_match.group(0),
                META_SYNOPSIS: entry['title_description'],
                META_MEDIA: 'movie',
                META_ID_IMDB: entry['id']
            })
        return metadata
