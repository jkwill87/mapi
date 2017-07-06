# coding=utf-8

from re import match
from time import sleep

from mapi.constants import PLATFORM_IOS
from mapi.exceptions import *
from mapi.utilities import request_json


def imdb_main_details(id_imdb):
    """ Lookup a media item using the Internet Movie Database's internal API

    :param str id_imdb: Internet Movie Database's primary key; prefixed w/ 'tt'
    :return: dict
    """
    if not match(r'tt\d+', id_imdb):
        raise MapiNotFoundException
    url = 'http://app.imdb.com/title/maindetails'
    parameters = {'tconst': id_imdb}
    status = content = None
    for i in range(50):  # retry when service unavailable
        status, content = request_json(url, parameters, agent=PLATFORM_IOS)
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


def imdb_mobile_find(title, nr=True, tt=True):
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

    :param str api_key: The Movie Database API key
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

    :param str api_key: The Movie Database API key.
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

    :param str api_key: The Movie Database API key
    :param str title: Search criteria; i.e. the movie title
    :param optional int or str year: Feature's release year
    :param bool adult: Include adult (pornography) content in the results
    :param optional str region: ISO 3166-1 code
    :param int page: Results are returned paginated; page selection
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
    if status == 404 or not content.get('total_results'):
        raise MapiNotFoundException
    assert status == 200
    assert any(content.keys())
    return content
