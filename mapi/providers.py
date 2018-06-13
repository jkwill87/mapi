# coding=utf-8

""" Provides a high-level interface for metadata media providers
"""

from abc import ABCMeta, abstractmethod
from os import environ
from re import match

from mapi import endpoints, log
from mapi.exceptions import (
    MapiException,
    MapiNotFoundException,
    MapiProviderException
)
from mapi.metadata import MetadataMovie, MetadataTelevision

# Compatibility for Python 2.7/3+
_AbstractClass = ABCMeta('ABC', (object,), {'__slots__': ()})

API_TELEVISION = {'tvdb'}
API_MOVIE = {
    'tmdb'
}
API_ALL = API_TELEVISION | API_MOVIE


def has_provider(provider):
    """ Verifies that module has support for requested API provider
    """
    return provider.lower() in API_ALL


def has_provider_support(provider, media_type):
    """ Verifies if API provider has support for requested media type
    """
    if provider.lower() not in API_ALL:
        return False
    provider_const = 'API_' + media_type.upper()
    return provider in globals().get(provider_const, {})


def provider_factory(provider, **options):
    """ Factory function for DB Provider Concrete Classes
    """
    try:
        return {
            'tmdb': TMDb,
            'tvdb': TVDb,
        }[provider.lower()](**options)
    except KeyError:
        msg = 'Attempted to initialize non-existing DB Provider'
        log.error(msg)
        raise MapiException(msg)


class Provider(_AbstractClass):
    """ ABC for Providers, high-level interfaces for metadata media providers
    """

    def __init__(self, **options):
        """ Initializes the provider

        :param options: Optional kwargs; see below..
        """
        cls_name = self.__class__.__name__
        self._api_key = options.get(
            'api_key',
            environ.get('API_KEY_%s' % cls_name.upper())
        )
        self._cache = options.get('cache', True)

    @staticmethod
    def _year_expand(s):
        """ Parses a year or dash-delimeted year range
        """
        regex = r'^((?:19|20)\d{2})?(\s*-\s*)?((?:19|20)\d{2})?$'
        try:
            start, dash, end = match(regex, str(s)).groups()
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


class TMDb(Provider):
    """ Queries the TMDb API
    """

    def __init__(self, **options):
        super(TMDb, self).__init__(**options)
        if not self.api_key:
            raise MapiProviderException('TMDb requires an API key')

    def search(self, id_key=None, **parameters):
        """ Searches TMDb for movie metadata
        """
        id_tmdb = parameters.get('id_tmdb') or id_key
        id_imdb = parameters.get('id_imdb')
        title = parameters.get('title')
        year = parameters.get('year')

        if id_tmdb:
            yield self._search_id_tmdb(id_tmdb)
        elif id_imdb:
            yield self._search_id_imdb(id_imdb)
        elif title:
            for result in self._search_title(title, year):
                yield result
        else:
            raise MapiNotFoundException

    def _search_id_imdb(self, id_imdb):
        response = endpoints.tmdb_find(
            self.api_key, 'imdb_id', id_imdb, cache=self.cache
        )['movie_results'][0]
        return MetadataMovie(
            title=response['title'],
            date=response['release_date'],
            synopsis=response['overview'],
            media='movie',
            id_tmdb=response['id'],
        )

    def _search_id_tmdb(self, id_tmdb):
        assert id_tmdb
        response = endpoints.tmdb_movies(
            self.api_key, id_tmdb, cache=self.cache
        )
        return MetadataMovie(
            title=response['title'],
            date=response['release_date'],
            synopsis=response['overview'],
            media='movie',
            id_tmdb=str(id_tmdb),
        )

    def _search_title(self, title, year):
        assert title
        found = False
        year_from, year_to = self._year_expand(year)
        page = 1
        page_max = 10  # each page yields max of 20 results

        while True:
            response = endpoints.tmdb_search_movies(
                self.api_key, title, year, page=page, cache=self.cache
            )
            for entry in response['results']:
                try:
                    meta = MetadataMovie(
                        title=entry['title'],
                        date=entry['release_date'],
                        synopsis=entry['overview'],
                        media='movie',
                        id_tmdb=str(entry['id'])
                    )
                except ValueError:
                    continue
                if year_from <= int(meta['year']) <= year_to:
                    yield meta
                    found = True
            if page == response['total_pages']:
                break
            elif page >= page_max:
                break
            page += 1
        if not found:
            raise MapiNotFoundException


class TVDb(Provider):
    """ Queries the TVDb API
    """

    def __init__(self, **options):
        super(TVDb, self).__init__(**options)
        if not self.api_key:
            raise MapiProviderException('TVDb requires an API key')
        self.token = endpoints.tvdb_login(self.api_key)

    def search(self, id_key=None, **parameters):
        """ Searches TVDb for movie metadata

        TODO: Consider making parameters for episode ids
        """
        episode = parameters.get('episode')
        id_tvdb = parameters.get('id_tvdb') or id_key
        id_imdb = parameters.get('id_imdb')
        season = parameters.get('season')
        series = parameters.get('series')
        date = parameters.get('date')

        if id_tvdb:
            for result in self._search_id_tvdb(id_tvdb, season, episode):
                yield result
        elif id_imdb:
            for result in self._search_id_imdb(id_imdb, season, episode):
                yield result
        elif series and date:
            if not match(
                r'(19|20)\d{2}(-(?:0[1-9]|1[012])(-(?:[012][1-9]|3[01]))?)?',
                date
            ):
                raise MapiProviderException('Date must be in YYYY-MM-DD format')
            for result in self._search_series_date(series, date):
                yield result
        elif series:
            for result in self._search_series(series, season, episode):
                yield result
        else:
            raise MapiNotFoundException

    def _search_id_imdb(self, id_imdb, season=None, episode=None):
        series_data = endpoints.tvdb_search_series(
            self.token, id_imdb=id_imdb, cache=self.cache
        )
        id_tvdb = (series_data['data'][0]['id'])
        return self._search_id_tvdb(id_tvdb, season, episode)

    def _search_id_tvdb(self, id_tvdb, season=None, episode=None):
        assert id_tvdb
        found = False
        series_data = endpoints.tvdb_series_id(
            self.token, id_tvdb, cache=self.cache
        )
        page = 1
        page_max = 5
        while True:
            episode_data = endpoints.tvdb_series_episodes_query(
                self.token, id_tvdb, episode, season, cache=self.cache
            )
            for entry in episode_data['data']:
                try:
                    yield MetadataTelevision(
                        series=series_data['data']['seriesName'],
                        season=str(entry['airedSeason']),
                        episode=str(entry['airedEpisodeNumber']),
                        date=entry['firstAired'],
                        title=entry['episodeName'].split(';', 1)[0],
                        synopsis=str(entry['overview'])
                            .replace('\r\n', '').replace('  ', '').strip(),
                        media='television',
                        id_tvdb=str(id_tvdb),
                    )
                    found = True
                except (AttributeError, ValueError):
                    continue
            if page == episode_data['links']['last']:
                break
            elif page >= page_max:
                break
            page += 1
        if not found:
            raise MapiNotFoundException

    def _search_series(self, series, season, episode):
        assert series
        found = False
        series_data = endpoints.tvdb_search_series(
            self.token, series, cache=self.cache
        )

        for series_id in [entry['id'] for entry in series_data['data'][:5]]:
            try:
                for data in self._search_id_tvdb(series_id, season, episode):
                    found = True
                    yield data
            except MapiNotFoundException:
                continue  # may not have requested episode or may be banned
        if not found:
            raise MapiNotFoundException

    def _search_series_date(self, series, date):
        assert series and date
        found = False
        series_data = endpoints.tvdb_search_series(
            self.token, series, cache=self.cache
        )
        series_entries = {
            entry['id']: entry['seriesName']
            for entry in series_data['data'][:5]
        }
        page = 1
        page_max = 100
        for id_tvdb, series_name in series_entries.items():
            while True:
                try:
                    response = endpoints.tvdb_series_id_episodes(
                        self.token, id_tvdb, page, cache=self.cache
                    )
                except MapiNotFoundException:
                    break
                for entry in response['data']:
                    if not entry['firstAired'].startswith(date):
                        continue
                    try:
                        yield MetadataTelevision(
                            series=series_name,
                            season=str(entry['airedSeason']),
                            episode=str(entry['airedEpisodeNumber']),
                            date=entry['firstAired'],
                            title=entry['episodeName'].split(';', 1)[0],
                            synopsis=str(entry['overview']).replace('\r\n', '')
                                .replace('  ', '').strip(),
                            media='television',
                            id_tvdb=str(entry['airedSeasonID']),
                        )
                        found = True
                    except (AttributeError, ValueError):
                        continue
                if page == response['links']['last']:
                    break
                elif page >= page_max:
                    break
                elif found and len(date) == 10:
                    break
                page += 1
        if not found:
            raise MapiNotFoundException
