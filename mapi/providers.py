# coding=utf-8

""" Provides a high-level interface for metadata media providers
"""
from abc import ABCMeta, abstractmethod
from os import environ
from re import match

from mapi import *
from mapi import endpoints
from mapi.exceptions import *
from mapi.metadata import MetadataMovie, MetadataTelevision

# Compatibility for Python 2.7/3+
_AbstractClass = ABCMeta('ABC', (object,), {'__slots__': ()})


API_TELEVISION = {'tvdb'}
API_MOVIE = {'imdb', 'tmdb'}
API_ALL = API_TELEVISION | API_MOVIE


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
    :return: One of this module's provider objects
    """
    try:
        return {
            'imdb': IMDb,
            'tmdb': TMDb,
            'tvdb': TVDb,
        }[provider.lower()](**options)
    except KeyError:
        msg = 'Attempted to initialize non-existing DB Provider'
        log.error(msg)
        raise MapiException(msg)


class Provider(_AbstractClass):
    """ 
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

    @staticmethod
    def _year_expand(s):
        """ Parses a year or dash-delimeted year range

        :param optional str or int s: Year or year range to be parsed
        :rtype: tuple of int or None
        :return: The first integer in the tuple is the from year, the second is
            the to year. If either field was omitted or invalid, it will be
            represented as None.
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
    def search(self, **parameters):
        pass

    @property
    def api_key(self):
        return self._api_key


class IMDb(Provider):
    """ Queries the unofficial IMDb mobile API
    """

    def search(self, **parameters):
        """ Searches IMDb for movie metadata

        :param kwargs parameters: Search parameters
        :keyword str title: Feature title
        :keyword optional str or int year: Feature year
        :raises MapiException: Or one of its subclasses; see mapi/exceptions.py
        :return list of dict: Movie metadata; see readme for mapping details
        :rtype: dict
        """

        # Process parameters
        title = parameters.get('title')
        year = parameters.get('year')
        id_imdb = parameters.get('id_imdb')

        # Search by IMDb 'tt-const' ID
        if id_imdb:
            yield self._search_id_imdb(id_imdb)

        # Search by title / year
        elif title:
            for result in self._search_title(title, year):
                yield result
        else:
            raise MapiNotFoundException

    def _search_id_imdb(self, id_imdb):
        assert id_imdb
        response = endpoints.imdb_main_details(id_imdb)['data']

        try:
            return MetadataMovie(
                id_imdb=response['tconst'],
                media='movie',
                synopsis=response['plot']['outline'],
                title=response['title'],
                date=response['release_date']['normal']
            )

        # Ignore hits with missing fields
        except (KeyError, ValueError):
            raise MapiNotFoundException

    def _search_title(self, title, year):
        assert title
        found = False
        year_from, year_to = self._year_expand(year)
        response = endpoints.imdb_mobile_find(title)

        # Ranking: popular, exact, approx, then substring; not intuitive but w/e
        ids = list()
        ids += [entry['id'] for entry in response.get('title_popular', [])]
        ids += [entry['id'] for entry in response.get('title_exec', [])]
        ids += [entry['id'] for entry in response.get('title_approx', [])]
        ids += [entry['id'] for entry in response.get('title_substring', [])]

        for id_imdb in ids:
            try:
                meta = self._search_id_imdb(id_imdb)
                if year_from <= int(meta['year']) <= year_to:
                    yield meta
                    found = True
            # Sometimes IMDb gives junk results; omit these
            except MapiNotFoundException:
                continue
        if not found:
            raise MapiNotFoundException


class TMDb(Provider):
    """ Queries the TMDb API
    """

    def __init__(self, **options):
        super(TMDb, self).__init__(**options)
        if not self.api_key:
            raise MapiProviderException('TMDb requires an API key')

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
        id_tmdb = parameters.get('id_tmdb')
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
            self.api_key, 'imdb_id', id_imdb
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
        response = endpoints.tmdb_movies(self.api_key, id_tmdb)
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
                self.api_key, title, year, page=page
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
        episode = parameters.get('episode')
        id_imdb = parameters.get('id_imdb')
        id_tvdb = parameters.get('id_tvdb')
        season = parameters.get('season')
        series = parameters.get('series')

        if id_tvdb:
            for result in self._search_id_tvdb(id_tvdb, season, episode):
                yield result
        elif id_imdb:
            for result in self._search_id_imdb(id_imdb, season, episode):
                yield result
        elif series:
            for result in self._search_series(series, season, episode):
                yield result
        else:
            raise MapiNotFoundException

    def _search_id_imdb(self, id_imdb, season, episode):
        series_data = endpoints.tvdb_search_series(self.token, id_imdb=id_imdb)
        id_tvdb = (series_data['data'][0]['id'])
        return self._search_id_tvdb(id_tvdb, season, episode)

    def _search_id_tvdb(self, id_tvdb, season, episode):
        assert id_tvdb
        found = False
        series_data = endpoints.tvdb_series_id(self.token, id_tvdb)
        page = 1
        page_max = 5
        while True:
            episode_data = endpoints.tvdb_series_episodes_query(self.token,
                id_tvdb, episode, season)
            for entry in episode_data['data']:
                try:
                    yield MetadataTelevision(
                        series=series_data['data']['seriesName'],
                        season=str(entry['airedSeason']),
                        episode=str(entry['airedEpisodeNumber']),
                        date=entry['firstAired'],
                        title=entry['episodeName'],
                        synopsis=str(entry['overview'])
                            .replace('\r\n', '').replace('  ', '').strip(),
                        media='television',
                        id_tvdb=str(id_tvdb),
                    )
                    found = True
                except ValueError:
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
        series_data = endpoints.tvdb_search_series(self.token, series)
        entries = [entry['id'] for entry in series_data['data'][:5]]

        for id_tvdb in entries:
            try:
                return self._search_id_tvdb(id_tvdb, season, episode)
            except MapiNotFoundException:
                continue  # may not have requested episode or may be banned
        if not found:
            raise MapiNotFoundException
