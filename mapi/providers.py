# coding=utf-8

""" Provides a high-level interface for metadata media providers
"""

from os import environ

from mapi import *
from mapi import endpoints
from mapi.constants import *
from mapi.exceptions import *
from mapi.utilities import clean_dict, filter_meta


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


def provider_factory(provider, **options):
    """ Factory function for DB Provider Concrete Classes

    :param provider: one of the constants contained within the API_ALL or their
        resolved value
    :param options: Optional kwargs; passed on to class constructor.
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
        PROVIDER_TMDB: TMDb,
        PROVIDER_TVDB: TVDb
    }[provider.lower()](**options)


class IMDb:
    """ Queries the unofficial IMDb mobile API
    """

    def __init__(self, **options):
        """ Initializes the IMDb provider

        :param options: Optional kwargs; see below..
        :keyword int year_delta: If set and a year is provided for a movie
            query, results will be filtered around this value inclusively.
        :keyword int max_hits: Will restrict the maximum number of responses for
            a search. If unset or None, searches yield as many as possible from
            the API provider.
        """
        self.year_delta = options.get('year_delta', 5)
        self.max_hits = options.get('max_hits', 15)

    def search(self, **parameters):
        """ Searches IMDb for movie metadata

        :param kwargs parameters: Search parameters
        :keyword str id_imdb: IMDb movie id key; must be prefixed with 'tt'
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
            metadata = [self._search_id_imdb(id_imdb)]
        elif title:
            metadata = self._search_title(title)
        else:
            raise MapiNotFoundException
        if not metadata:
            raise MapiNotFoundException
        return filter_meta(metadata, self.max_hits, year, self.year_delta)

    def _search_id_imdb(self, id_imdb):
        assert id_imdb

        response = endpoints.imdb_main_details(id_imdb)['data']
        try:
            metadata = {
                META_TITLE: response['title'],
                META_YEAR: response['year'],
                META_SYNOPSIS: response['plot']['outline'],
                META_MEDIA: 'movie',
                META_ID_IMDB: response['tconst']
            }
            int(metadata[META_YEAR])
        except (KeyError, ValueError):
            raise MapiNotFoundException  # Ignore sketchy hits
        return metadata

    def _search_title(self, title):
        assert title

        metadata = list()
        response = endpoints.imdb_mobile_find(title)

        # Ranking: popular, exact, then approx substring; not intuitive, I know
        ids = list()
        ids += [entry['id'] for entry in response.get('title_popular', [])]
        ids += [entry['id'] for entry in response.get('title_exec', [])]
        ids += [entry['id'] for entry in response.get('title_approx', [])]
        ids += [entry['id'] for entry in response.get('title_substring', [])]

        for id_imdb in ids[:self.max_hits]:
            try:
                metadata.append(self._search_id_imdb(id_imdb))
            except MapiNotFoundException:
                continue
        return metadata


class TMDb:
    """ Queries the TMDb API
    """

    def __init__(self, **options):
        """ Initializes the TMDb provider

        :param options: Optional kwargs; see below..
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
        self.max_hits = options.get('max_hits', 15)
        api_key = options.get('api_key') or environ.get(API_KEY_ENV_TMDB)
        if isinstance(api_key, str):
            self.api_key = api_key
        else:
            raise MapiProviderException('TMDb requires api key')

    def search(self, **parameters):
        """ Searches TMDb for movie metadata

        :param kwargs parameters: Search parameters
        :keyword str id_tmdb: TMDb movie id key; must be numeric
        :keyword str id_imdb: IMDb movie id key; must be prefixed with 'tt'
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
        return filter_meta(metadata, self.max_hits, year, self.year_delta)

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


class TVDb:
    """ Queries the TVDb API
    """

    def __init__(self, **options):
        """ Initializes the TVDb provider

        :param options: Optional kwargs; see below..
        :keyword int year_delta: If set and a year is provided for a movie
            query, results will be filtered around this value inclusively.
        :keyword int max_hits: Will restrict the maximum number of responses for
            a search. If unset or None, searches yield as many as possible from
            the API provider.
        :keyword str api_key: TVDb developer API key; required to either be
            provided or available from the TVDb_API_KEY environment variable
        :raises MapiProviderException: If a TVDb key is not provided or found in
            the environment variables
        """
        self.year_delta = options.get('year_delta', 5)
        self.max_hits = options.get('max_hits', 15)
        api_key = options.get('api_key') or environ.get(API_KEY_ENV_TVDB)
        if isinstance(api_key, str):
            self.token = endpoints.tvdb_login(api_key)
        else:
            raise MapiProviderException('TVDb requires api key')

    def search(self, **parameters):
        """ Searches TVDb for movie metadata

        TODO: Consider making parameters for episode ids

        :param kwargs parameters: Search parameters
        :keyword str id_tvdb: TVDb series id key; must be numeric
        :keyword str id_imdb: IMDb series id key; must be prefixed with 'tt'
        :keyword str series: Series name
        :keyword str or int season: Aired season number
        :keyword str or int episode: Aired episode number
        :raises MapiException: Or one of its subclasses; see mapi/exceptions.py
        :return list of dict: Movie metadata; see readme for mapping details
        :rtype: dict
        """
        parameters = clean_dict(parameters, PARAMS_TELEVISION)
        episode = parameters.get('episode')
        id_imdb = parameters.get('id_imdb')
        id_tvdb = parameters.get('id_tvdb')
        season = parameters.get('season')
        series = parameters.get('series')

        if id_tvdb:
            metadata = self._search_id_tvdb(id_tvdb, season, episode)
        elif id_imdb:
            metadata = self._search_id_imdb(id_imdb, season, episode)
        elif series:
            metadata = self._search_series(series, season, episode)
        else:
            raise MapiNotFoundException
        return filter_meta(metadata, self.max_hits)

    def _search_id_tvdb(self, id_tvdb, season, episode):
        metadata = list()
        series_data = endpoints.tvdb_series_id(self.token, id_tvdb)
        page = 1
        page_max = -(-self.max_hits // 100) if self.max_hits else 5
        while True:
            episode_data = endpoints.tvdb_series_episodes_query(self.token,
                id_tvdb, episode, season)
            for entry in episode_data['data']:
                metadata.append({
                    META_SERIES: series_data['data']['seriesName'],
                    META_SEASON: str(entry['airedSeason']),
                    META_EPISODE: str(entry['airedEpisodeNumber']),
                    META_AIRDATE: entry['firstAired'],
                    META_TITLE: entry['episodeName'],
                    META_SYNOPSIS: str(entry['overview'])
                        .replace('\r\n', '').replace('  ', '').strip(),
                    META_MEDIA: MEDIA_TELEVISION,
                    META_ID_TVDB: str(id_tvdb),
                })
            if page == episode_data['links']['last']:
                break
            elif page >= page_max:
                break
            page += 1
        return metadata

    def _search_id_imdb(self, id_imdb, season, episode):
        series_data = endpoints.tvdb_search_series(self.token, id_imdb=id_imdb)
        id_tvdb = (series_data['data'][0]['id'])
        return self._search_id_tvdb(id_tvdb, season, episode)

    def _search_series(self, series, season, episode):
        metadata = list()
        series_data = endpoints.tvdb_search_series(self.token, series)
        entries = [entry['id'] for entry in series_data['data'][:5]]

        for id_tvdb in entries:
            try:
                metadata += (self._search_id_tvdb(id_tvdb, season, episode))
            except MapiNotFoundException:
                pass  # Entry may not have requested episode or may be banned
        if not metadata:
            raise MapiNotFoundException
        return metadata
