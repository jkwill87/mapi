# coding=utf-8

import re
from os import environ

from mapi import *
from mapi import endpoints
from mapi.constants import *
from mapi.exceptions import *
from mapi.utilities import filter_meta, clean_dict


def provider_factory(provider, **options):
    """ Factory function for DB Provider Concrete Classes

    :param provider: one of the constants contained within the API_ALL or their
        resolved value
    :param dict options: Optional kwargs; passed on to class constructor.
    :keyword str api_key: Some API providers require an API key to use their
        service
    :keyword int year_delta:  If set and a year is provided for a movie query,
        results will be filtered around this value inclusively
    :keyword int max_hits: Will restrict the maximum number of responses for a
        search. If unset or None, searches yield as many as possible from the
        API provider
    :return: One of this module's provider objects
    """
    if not has_provider(provider):
        msg = 'Attempted to initialize non-existing DB Provider'
        log.error(msg)
        raise MapiException(msg)
    return {
        PROVIDER_IMDB: IMDb,
        PROVIDER_TMDB: TMDb
        # DB_TVDB: TVDb  # TODO
    }[provider.lower()](**options)


class IMDb:
    """ Queries the unofficial IMDb mobile API
    """

    def __init__(self, **options):
        """ Initializes an IMDb provider

        :param dict options: Optional kwargs; see below..
        :keyword int year_delta: If set and a year is provided for a movie
            query, results will be filtered around this value inclusively.
        :keyword int max_hits: Will restrict the maximum number of responses for
            a search. If unset or None, searches yield as many as possible from
            the API provider.
        """
        self.year_delta = options.get('year_delta', 5)
        self.max_hits = options.get('max_hits', 25)

    def search(self, **parameters):
        """ Searches IMDb for movie metadata

        :param kwargs parameters: Search parameters
        :keyword str id_imdb: IMDb primary key; must be prefixed with 'tt'
        :keyword str title: Feature title
        :keyword optional str or int year: Feature year
        :raises MapiException: Or one of its subclasses; see mapi/exceptions.py
        :return list of dict: Movie metadata; see readme for mapping details
        :rtype: dict
        """

        # Process parameters
        parameters = clean_dict(parameters, PARAMS_MOVIE)
        id_imdb = parameters.get('id_imdb')
        title = parameters.get('title')
        year = parameters.get('year')

        # Perform query for metadata
        if id_imdb:
            metadata = self._search_id_imdb(id_imdb)
        elif title:
            metadata = self._search_title(title)
        else:
            raise MapiNotFoundException
        if not metadata:
            raise MapiNotFoundException
        return filter_meta(metadata, self.max_hits, self.year_delta, year)

    def _search_id_imdb(self, id_imdb):
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

    def _search_title(self, title):
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


class TMDb:
    """ Queries the TMDb mobile API
    """

    def __init__(self, **options):
        """ Initializes an TMDb provider

        :param dict options: Optional kwargs; see below..
        :keyword int year_delta: If set and a year is provided for a movie
            query, results will be filtered around this value inclusively.
        :keyword int max_hits: Will restrict the maximum number of responses for
            a search. If unset or None, searches yield as many as possible from
            the API provider.
        :keyword str api_key: TMDb developer API key; required to either be
            provided or available from the TMDb_API_KEY environment variable
        :raises MapiProviderException: If a TMDb key is not provided or found in
            the environment variables
        """
        self.year_delta = options.get('year_delta', 5)
        self.max_hits = options.get('max_hits', 25)
        self.api_key = options.get('api_key') or environ.get(API_KEY_ENV_TMDB)
        if not self.api_key:
            raise MapiProviderException('TMDb requires api key')

    def search(self, **parameters):
        """ Searches TMDb for movie metadata

        :param kwargs parameters: Search parameters
        :keyword str id_tmdb: TMDb primary key; must be numeric
        :keyword str id_imdb: IMDb primary key; must be prefixed with 'tt'
        :keyword str title: Feature title
        :keyword optional str or int year: Feature year
        :raises MapiException: Or one of its subclasses; see mapi/exceptions.py
        :return list of dict: Movie metadata; see readme for mapping details
        :rtype: dict
        """
        parameters = clean_dict(parameters, PARAMS_MOVIE)
        id_tmdb = parameters.get('id_tmdb')
        id_imdb = parameters.get('id_imdb')
        title = parameters.get('title')
        year = parameters.get('year')

        if id_tmdb:
            metadata = self._search_id_tmdb(id_tmdb)
        elif id_imdb:
            metadata = self._search_id_imdb(id_imdb)
        elif title:
            metadata = self._search_title(title, year)
        else:
            raise MapiNotFoundException
        return filter_meta(metadata, self.max_hits, self.year_delta, year)

    def _search_id_imdb(self, id_imdb):
        response = endpoints.tmdb_find(
            self.api_key, 'imdb_id', id_imdb
        )['movie_results'][0]
        return [{
            META_TITLE: response['title'],
            META_YEAR: response['release_date'][:4],
            META_SYNOPSIS: response['overview'],
            META_MEDIA: 'movie',
            META_ID_TMDB: response['id'],
        }]

    def _search_id_tmdb(self, id_tmdb):
        response = endpoints.tmdb_movies(self.api_key, id_tmdb)
        return [{
            META_TITLE: response['title'],
            META_YEAR: response['release_date'][:4],
            META_SYNOPSIS: response['overview'],
            META_MEDIA: 'movie',
            META_ID_TMDB: str(id_tmdb),
        }]

    def _search_title(self, title, year):
        metadata = list()
        page = 1
        # each page yields max of 20 results
        page_max = -(-self.max_hits // 20) if self.max_hits else 10
        while True:
            response = endpoints.tmdb_search_movies(
                self.api_key, title, year, page=page
            )
            for entry in response['results']:
                metadata.append({
                    META_TITLE: entry['title'],
                    META_YEAR: entry['release_date'][:4],
                    META_SYNOPSIS: entry['overview'],
                    META_MEDIA: 'movie',
                    META_ID_TMDB: str(entry['id']),
                })
            if page == response['total_pages']:
                break
            elif page >= page_max:
                break
            page += 1
        return metadata
