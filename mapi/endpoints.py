# coding=utf-8

""" Stand-alone functions which have a 1:1 mapping to that of API endpoints
"""

from re import match
from time import sleep
from mapi.constants import TVDB_LANGUAGE_CODES
from mapi.exceptions import *
from mapi.utilities import request_json


def imdb_main_details(id_imdb):
    """ Lookup a media item using the Internet Movie Database's internal API

    This endpoint is more detailed than the mobile endpoint but has a tenancy to
    unpredictably return 503 status codes when hit frequently

    :param str id_imdb: Internet Movie Database's primary key; prefixed w/ 'tt'
    :return: dict
    """
    if not match(r'tt\d+', id_imdb):
        raise MapiProviderException('invalid imdb tt-const value')
    url = 'https://app.imdb.com/title/maindetails'
    parameters = {
        'tconst': id_imdb,
    }
    status = content = None
    for i in range(50):  # retry when service unavailable
        status, content = request_json(url, parameters)
        if status == 503:
            sleep((i + 1) * .025)  # .025 to 1.25 secs, total ~32
        else:
            break
    assert status != 400
    if status == 404 or not content:
        raise MapiNotFoundException
    assert status == 200
    assert any(content.keys())
    return content


def imdb_mobile_find(title, nr=False, tt=False):
    """ Search the Internet Movie Database using its undocumented iOS API

    :param str title: Movie title used for searching
    :param bool nr: ???
    :param bool tt: ???
    :return: status, data
    :rtype: dict
    """
    url = 'http://www.imdb.com/xml/find'
    parameters = {'json': True, 'nr': nr, 'tt': tt, 'q': title}
    status = content = None
    for i in range(50):  # retry when service unavailable
        status, content = request_json(url, parameters)
        if status == 503:
            sleep((i + 1) * .025)  # wait from .025 to 1.25 secs
        else:
            break

    if status == 400 or not content:
        raise MapiNotFoundException
    assert status == 200
    assert any(content.keys())
    return content


def tmdb_find(api_key, external_source, external_id, language='en-US'):
    """ Search for The Movie Database objects using another DB's foreign key

    Note: language codes aren't checked on this end or by TMDb, so if you
        enter an invalid language code your search itself will succeed, but
        certain fields like synopsis will just be empty

    Online docs: developers.themoviedb.org/3/find

    :param str api_key: A Movie Database API key
    :param str external_source: one of imdb_id, freebase_mid, freebase_id,
        tvdb_id, tvrage_id
    :param str external_id: id number corresponding to external_source
    :param str language: IETF language tag
    :raises MapiNotFoundException: No matches for request.
    :return: Returned json data
    :rtype: dict
    """
    sources = ['imdb_id', 'freebase_mid', 'freebase_id', 'tvdb_id', 'tvrage_id']
    if external_source not in sources:
        raise MapiProviderException('external_source must be in %s' % sources)
    if external_source == 'imdb_id' and not match(r'tt\d+', external_id):
        raise MapiProviderException('invalid imdb tt-const value')
    url = 'https://api.themoviedb.org/3/find/' + external_id or ''
    parameters = {
        'api_key': api_key,
        'external_source': external_source,
        'language': language
    }
    keys = [
        'movie_results',
        'person_results',
        'tv_episode_results',
        'tv_results',
        'tv_season_results'
    ]
    status, content = request_json(url, parameters)
    if status == 401:
        raise MapiProviderException('invalid API key')
    if status == 404 or not any(content.get(k, {}) for k in keys):
        raise MapiNotFoundException
    assert status == 200
    assert any(content.keys())
    return content


def tmdb_movies(api_key, id_tmdb, language='en-US'):
    """ Lookup a movie item using The Movie Database

    Online docs: developers.themoviedb.org/3/movies

    :param str api_key: A Movie Database API key
    :param str or int id_tmdb: The Movie Database id to lookup
    :param str language: IETF language tag
    :raises MapiNotFoundException: No matches for request
    :return: Returned json data
    :rtype: dict
    """
    try:
        url = 'https://api.themoviedb.org/3/movie/%d' % int(id_tmdb)
    except ValueError:
        raise MapiProviderException('id_tmdb must be numeric')
    parameters = {
        'api_key': api_key,
        'language': language
    }
    status, content = request_json(url, parameters)
    if status == 401:
        raise MapiProviderException('invalid API key')
    if status == 404:
        raise MapiNotFoundException
    assert status == 200
    assert any(content.keys())
    return content


def tmdb_search_movies(api_key, title, year=None, adult=False, region=None,
        page=1):
    """ Search for movies using The Movie Database

    Online docs: developers.themoviedb.org/3/search/search-movies

    :param str api_key: A Movie Database API key
    :param str title: Search criteria; i.e. the movie title
    :param optional int or str year: Feature's release year
    :param bool adult: Include adult (pornography) content in the results
    :param optional str region: ISO 3166-1 code
    :param int page: Results are returned paginated; page selection; default 1
    :raises MapiNotFoundException: No matches for request
    :return: Returned json data
    :rtype: dict
    """
    url = 'https://api.themoviedb.org/3/search/movie'
    try:
        if year:
            year = int(year)
    except ValueError:
        raise MapiProviderException('year must be numeric')
    parameters = {
        'api_key': api_key,
        'query': title,
        'page': page,
        'include_adult': adult,
        'region': region,
        'year': year,
    }
    status, content = request_json(url, parameters)
    if status == 401:
        raise MapiProviderException('invalid API key')
    if status == 404 or status == 422 or not content.get('total_results'):
        raise MapiNotFoundException
    assert status == 200
    assert any(content.keys())
    return content


def tvdb_login(api_key):
    """ Logs into TVDb using the provided api key

    Note: You can register for a free TVDb key at thetvdb.com/?tab=apiregister
    Online docs: api.thetvdb.com/swagger#!/Authentication/post_login

    :param str api_key: A Television Database api key
    :return: JWT token required for all other endpoints; expires after 24 hours
    :rtype: str
    """
    url = 'https://api.thetvdb.com/login'
    body = {'apikey': api_key}
    status, content = request_json(url, body=body, cache=False)
    if status == 401:
        raise MapiProviderException('invalid api key')
    assert status == 200 and content.get('token')
    return content['token']


def tvdb_refresh_token(token):
    """ Refreshes JWT token

    Online docs: api.thetvdb.com/swagger#!/Authentication/get_refresh_token

    :param str token: Token to refresh
    :return: JWT token required for all other endpoints; expires after 24 hours
    :rtype: str
    """
    url = 'https://api.thetvdb.com/refresh_token'
    headers = {'Authorization': 'Bearer %s' % token}
    status, content = request_json(url, headers=headers, cache=False)
    if status == 401:
        raise MapiProviderException('invalid token')
    assert status == 200 and content.get('token')
    return content['token']


def tvdb_episodes_id(token, id_tvdb, lang='en'):
    """ Returns the full information for a given episode id

    Online docs: https://api.thetvdb.com/swagger#!/Episodes

    :param str token: TVDb JWT token; generate using login/ reload endpoints
    :param str or int id_tvdb: TVDb episode id
    :param str lang: TVDb language abbreviation code; defaults to 'en' for
        english; see https://api.thetvdb.com/swagger#!/Languages/get_languages
    :return: Returned json data
    :rtype: dict
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ','.join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = 'https://api.thetvdb.com/episodes/%d' % int(id_tvdb)
    except ValueError:
        raise MapiProviderException('id_tvdb must be numeric')
    headers = {
        'Accept-Language': lang,
        'Authorization': 'Bearer %s' % token
    }
    status, content = request_json(url, headers=headers)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    assert status == 200 and content.get('data')
    return content


def tvdb_series_id(token, id_tvdb, lang='en'):
    """ Returns a series records that contains all information known about a
    particular series id

    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id

    :param str token: TVDb JWT token; generate using login/ reload endpoints
    :param str or int id_tvdb: TVDb series id
    :param str lang: TVDb language abbreviation code; defaults to 'en' for
        english; see https://api.thetvdb.com/swagger#!/Languages/get_languages
    :return: Returned json data
    :rtype: dict
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ','.join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = 'https://api.thetvdb.com/series/%d' % int(id_tvdb)
    except ValueError:
        raise MapiProviderException('id_tvdb must be numeric')
    headers = {
        'Accept-Language': lang,
        'Authorization': 'Bearer %s' % token
    }
    status, content = request_json(url, headers=headers)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    assert status == 200
    return content


def tvdb_series_id_episodes(token, id_tvdb, page=1, lang='en'):
    """ All episodes for a given series

    Note: Paginated with 100 results per page
    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id_episodes

    :param str token: TVDb JWT token; generate using login/ reload endpoints
    :param str or int id_tvdb: TVDb series id
    :param int page: Page selection; default 1
    :param str lang: TVDb language abbreviation code; defaults to 'en' for
        english; see https://api.thetvdb.com/swagger#!/Languages/get_languages
    :return: Returned json data
    :rtype: dict
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ','.join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = 'https://api.thetvdb.com/series/%d/episodes' % int(id_tvdb)
    except ValueError:
        raise MapiProviderException('id_tvdb must be numeric')
    headers = {
        'Accept-Language': lang,
        'Authorization': 'Bearer %s' % token
    }
    parameters = {'page': page}
    status, content = request_json(url, parameters, headers=headers)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    assert status == 200
    return content


def tvdb_series_episodes_query(token, id_tvdb, episode=None, season=None,
        page=1, lang='en'):
    """ This route allows the user to query against episodes for the given series

    Note: Paginated with 100 results per page; omitted imdbId, when would you
    ever need to query against both tvdb and imdb series ids??
    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id_episodes_query

    :param str token: TVDb JWT token; generate using login/ reload endpoints
    :param str or int id_tvdb: TVDb series id
    :param optional str or int episode: Series' episode number
    :param optional str or int season: Series' season number
    :param int page: Page selection; default 1
    :param str lang: TVDb language abbreviation code; defaults to 'en' for
        english; see https://api.thetvdb.com/swagger#!/Languages/get_languages
    :return: Returned json data
    :rtype: dict
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ','.join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = 'https://api.thetvdb.com/series/%d/episodes/query' % int(id_tvdb)
    except ValueError:
        raise MapiProviderException('id_tvdb must be numeric')
    headers = {
        'Accept-Language': lang,
        'Authorization': 'Bearer %s' % token
    }
    parameters = {
        'airedSeason': season,
        'airedEpisode': episode,
        'page': page
    }
    status, content = request_json(url, parameters, headers=headers)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    assert status == 200
    return content


def tvdb_search_series(token, series=None, id_imdb=None, id_zap2it=None,
        lang='en'):
    """ Allows the user to search for a series based on the following parameters

    Online docs: https://api.thetvdb.com/swagger#!/Search/get_search_series
    Note: results a maximum of 100 entries per page, no option for pagination

    :param str token: TVDb JWT token; generate using login/ reload endpoints
    :param optional str series: Name of the series
    :param optional str id_imdb: IMDb series id code
    :param optional str id_zap2it: Zap2It series id code
    :param str lang: TVDb language abbreviation code; defaults to 'en' for
        english; see https://api.thetvdb.com/swagger#!/Languages/get_languages
    :return: Returned json data
    :rtype: dict
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ','.join(TVDB_LANGUAGE_CODES)
        )
    url = 'https://api.thetvdb.com/search/series'
    parameters = {
        'name': series,
        'imdbId': id_imdb,
        'zap2itId': id_zap2it
    }
    headers = {
        'Accept-Language': lang,
        'Authorization': 'Bearer %s' % token
    }
    status, content = request_json(url, parameters, headers=headers)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 405:
        raise MapiProviderException(
            'series, id_imdb, id_zap2it parameters are mutually exclusive')
    elif status == 404:
        raise MapiNotFoundException
    assert status == 200
    return content
