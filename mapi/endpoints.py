# coding=utf-8

""" Stand-alone functions which have a 1:1 mapping to that of API endpoints
"""
import random
from re import match
from sys import version_info

import requests_cache
from appdirs import user_cache_dir
from requests import RequestException

from mapi import log, ustr
from mapi.exceptions import (
    MapiNetworkException,
    MapiNotFoundException,
    MapiProviderException
)

TVDB_LANGUAGE_CODES = [
    'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it',
    'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'ru', 'sl', 'sv', 'tr', 'zh'
]

# User agent constants
AGENT_CHROME = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/601.1'
    ' (KHTML, like Gecko) CriOS/53.0.2785.86 Mobile/14A403 Safari/601.1.46'
)
AGENT_EDGE = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like '
    'Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
)
AGENT_IOS = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) '
    'AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A403 '
    'Safari/602.1'
)
AGENT_ALL = (AGENT_CHROME, AGENT_EDGE, AGENT_IOS)

# Setup requests caching
SESSION = requests_cache.CachedSession(
    cache_name=user_cache_dir() + '/mapi-py%d' % version_info.major,
    expire_after=604800,
)


def _clean_dict(target_dict, whitelist=None):
    """ Convenience function that removes a dicts keys that have falsy values
    """
    assert isinstance(target_dict, dict)
    return {
        ustr(k).strip(): ustr(v).strip()
        for k, v in target_dict.items()
        if v not in (None, Ellipsis, [], (), '')
        and (not whitelist or k in whitelist)
    }


def _d2l(d):
    """ Convenience function that converts a dict into a sorted list of tuples
    """
    return sorted([(k, v) for k, v in d.items()])


def _get_user_agent(platform=None):
    """ Convenience function that looks up a user agent string, random if N/A
    """
    if isinstance(platform, ustr):
        platform = platform.upper()
    return {
        'chrome': AGENT_CHROME,
        'edge': AGENT_EDGE,
        'ios': AGENT_IOS
    }.get(platform, random.choice(AGENT_ALL))


def _request_json(url, parameters=None, body=None, headers=None, cache=True,
                  agent=None, reattempt=5):
    """ Queries a url for json data

    Note: Requests are cached using requests_cached for a week, this is done
    transparently by using the package's monkey patching
    """
    assert url
    content = None
    status = 500
    log.info("url: %s" % url)

    if isinstance(headers, dict):
        headers = _clean_dict(headers)
    else:
        headers = dict()
    if isinstance(parameters, dict):
        parameters = _d2l(_clean_dict(parameters))
    if body:
        method = 'POST'
        headers['content-type'] = 'application/json'
        headers['user-agent'] = _get_user_agent(agent)
        headers['content-length'] = ustr(len(body))
    else:
        method = 'GET'
        headers['user-agent'] = _get_user_agent(agent)

    initial_cache_state = SESSION._is_cache_disabled  # yes, i'm a bad person
    try:
        SESSION._is_cache_disabled = not cache
        response = SESSION.request(
            url=url,
            params=parameters,
            json=body,
            headers=headers,
            method=method,
            timeout=1
        )
        status = response.status_code
        content = response.json() if status // 100 == 2 else None
        cache = getattr(response, 'from_cache', False)
    except RequestException as e:
        log.debug(e, exc_info=True)
        return _request_json(
            url, parameters, body, headers, cache, agent, reattempt - 1
        )
    except Exception as e:
        log.error(e, exc_info=True)
        if reattempt > 0:
            SESSION.cache.clear()
            return _request_json(
                url, parameters, body, headers, False, agent, 0
            )
    else:
        log.info("method: %s" % method)
        log.info("headers: %r" % headers)
        log.info("parameters: %r" % parameters)
        log.info("cache: %r" % cache)
        log.info("status: %d" % status)
        log.debug("content: %s" % content)
    finally:
        SESSION._is_cache_disabled = initial_cache_state

    return status, content


def tmdb_find(api_key, external_source, external_id, language='en-US',
        cache=True):
    """ Search for The Movie Database objects using another DB's foreign key

    Note: language codes aren't checked on this end or by TMDb, so if you
        enter an invalid language code your search itself will succeed, but
        certain fields like synopsis will just be empty

    Online docs: developers.themoviedb.org/3/find
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
    status, content = _request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException('invalid API key')
    elif status != 200 or not any(content.keys()):
        raise MapiNetworkException('TMDb down or unavailable?')
    elif status == 404 or not any(content.get(k, {}) for k in keys):
        raise MapiNotFoundException
    return content


def tmdb_movies(api_key, id_tmdb, language='en-US', cache=True):
    """ Lookup a movie item using The Movie Database

    Online docs: developers.themoviedb.org/3/movies
    """
    try:
        url = 'https://api.themoviedb.org/3/movie/%d' % int(id_tmdb)
    except ValueError:
        raise MapiProviderException('id_tmdb must be numeric')
    parameters = {
        'api_key': api_key,
        'language': language
    }
    status, content = _request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException('invalid API key')
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not any(content.keys()):
        raise MapiNetworkException('TMDb down or unavailable?')
    return content


def tmdb_search_movies(api_key, title, year=None, adult=False, region=None,
        page=1, cache=True):
    """ Search for movies using The Movie Database

    Online docs: developers.themoviedb.org/3/search/search-movies
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
    status, content = _request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException('invalid API key')
    elif status != 200 or not any(content.keys()):
        raise MapiNetworkException('TMDb down or unavailable?')
    elif status == 404 or status == 422 or not content.get('total_results'):
        raise MapiNotFoundException
    return content


def tvdb_login(api_key):
    """ Logs into TVDb using the provided api key

    Note: You can register for a free TVDb key at thetvdb.com/?tab=apiregister
    Online docs: api.thetvdb.com/swagger#!/Authentication/post_login=
    """
    url = 'https://api.thetvdb.com/login'
    body = {'apikey': api_key}
    status, content = _request_json(url, body=body, cache=False)
    if status == 401:
        raise MapiProviderException('invalid api key')
    elif status != 200 or not content.get('token'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content['token']


def tvdb_refresh_token(token):
    """ Refreshes JWT token

    Online docs: api.thetvdb.com/swagger#!/Authentication/get_refresh_token=
    """
    url = 'https://api.thetvdb.com/refresh_token'
    headers = {'Authorization': 'Bearer %s' % token}
    status, content = _request_json(url, headers=headers, cache=False)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status != 200 or not content.get('token'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content['token']


def tvdb_episodes_id(token, id_tvdb, lang='en', cache=True):
    """ Returns the full information for a given episode id

    Online docs: https://api.thetvdb.com/swagger#!/Episodes=
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
    status, content = _request_json(url, headers=headers, cache=cache)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    elif status == 200 and 'invalidLanguage' in content.get('errors', {}):
        raise MapiNotFoundException
    elif status != 200 or not content.get('data'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content


def tvdb_series_id(token, id_tvdb, lang='en', cache=True):
    """ Returns a series records that contains all information known about a
    particular series id

    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id=
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
    status, content = _request_json(url, headers=headers, cache=cache)
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get('data'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content


def tvdb_series_id_episodes(token, id_tvdb, page=1, lang='en', cache=True):
    """ All episodes for a given series

    Note: Paginated with 100 results per page
    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id_episodes=
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
    status, content = _request_json(
        url, parameters, headers=headers, cache=cache
    )
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get('data'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content


def tvdb_series_episodes_query(token, id_tvdb, episode=None, season=None,
        page=1, lang='en', cache=True):
    """ This route allows the user to query against episodes for the given series

    Note: Paginated with 100 results per page; omitted imdbId, when would you
    ever need to query against both tvdb and imdb series ids??
    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id_episodes_query=
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
    status, content = _request_json(
        url, parameters, headers=headers, cache=cache
    )
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get('data'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content


def tvdb_search_series(token, series=None, id_imdb=None, id_zap2it=None,
        lang='en', cache=True):
    """ Allows the user to search for a series based on the following parameters

    Online docs: https://api.thetvdb.com/swagger#!/Search/get_search_series
    Note: results a maximum of 100 entries per page, no option for pagination=
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
    status, content = _request_json(
        url, parameters, headers=headers, cache=cache
    )
    if status == 401:
        raise MapiProviderException('invalid token')
    elif status == 405:
        raise MapiProviderException(
            'series, id_imdb, id_zap2it parameters are mutually exclusive')
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get('data'):
        raise MapiNetworkException('TVDb down or unavailable?')
    return content
