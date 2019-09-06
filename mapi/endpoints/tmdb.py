# coding=utf-8

from re import match

from mapi.exceptions import (
    MapiNetworkException,
    MapiNotFoundException,
    MapiProviderException,
)
from mapi.utils import request_json


def tmdb_find(
    api_key, external_source, external_id, language="en-US", cache=True
):
    """
    Search for The Movie Database objects using another DB's foreign key.

    Note: language codes aren't checked on this end or by TMDb, so if you
        enter an invalid language code your search itself will succeed, but
        certain fields like synopsis will just be empty.

    Online docs: developers.themoviedb.org/3/find.
    """
    sources = ["imdb_id", "freebase_mid", "freebase_id", "tvdb_id", "tvrage_id"]
    if external_source not in sources:
        raise MapiProviderException("external_source must be in %s" % sources)
    if external_source == "imdb_id" and not match(r"tt\d+", external_id):
        raise MapiProviderException("invalid imdb tt-const value")
    url = "https://api.themoviedb.org/3/find/" + external_id or ""
    parameters = {
        "api_key": api_key,
        "external_source": external_source,
        "language": language,
    }
    keys = [
        "movie_results",
        "person_results",
        "tv_episode_results",
        "tv_results",
        "tv_season_results",
    ]
    status, content = request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException("invalid API key")
    elif status != 200 or not any(content.keys()):  # pragma: no cover
        raise MapiNetworkException("TMDb down or unavailable?")
    elif status == 404 or not any(content.get(k, {}) for k in keys):
        raise MapiNotFoundException
    return content


def tmdb_movies(api_key, id_tmdb, language="en-US", cache=True):
    """
    Lookup a movie item using The Movie Database.

    Online docs: developers.themoviedb.org/3/movies.
    """
    try:
        url = "https://api.themoviedb.org/3/movie/%d" % int(id_tmdb)
    except ValueError:
        raise MapiProviderException("id_tmdb must be numeric")
    parameters = {"api_key": api_key, "language": language}
    status, content = request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException("invalid API key")
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not any(content.keys()):  # pragma: no cover
        raise MapiNetworkException("TMDb down or unavailable?")
    return content


def tmdb_search_movies(
    api_key, title, year=None, adult=False, region=None, page=1, cache=True
):
    """
    Search for movies using The Movie Database.

    Online docs: developers.themoviedb.org/3/search/search-movies.
    """
    url = "https://api.themoviedb.org/3/search/movie"
    try:
        if year:
            year = int(year)
    except ValueError:
        raise MapiProviderException("year must be numeric")
    parameters = {
        "api_key": api_key,
        "query": title,
        "page": page,
        "include_adult": adult,
        "region": region,
        "year": year,
    }
    status, content = request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException("invalid API key")
    elif status != 200 or not any(content.keys()):  # pragma: no cover
        raise MapiNetworkException("TMDb down or unavailable?")
    elif status == 404 or status == 422 or not content.get("total_results"):
        raise MapiNotFoundException
    return content
