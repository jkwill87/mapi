# coding=utf-8

from mapi.exceptions import (
    MapiNetworkException,
    MapiNotFoundException,
    MapiProviderException,
)
from mapi.utils import request_json

TVDB_LANGUAGE_CODES = [
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "fi",
    "fr",
    "he",
    "hr",
    "hu",
    "it",
    "ja",
    "ko",
    "nl",
    "no",
    "pl",
    "pt",
    "ru",
    "sl",
    "sv",
    "tr",
    "zh",
]


def tvdb_login(api_key):
    """
    Logs into TVDb using the provided api key.

    Note: You can register for a free TVDb key at thetvdb.com/?tab=apiregister
    Online docs: api.thetvdb.com/swagger#!/Authentication/post_login.
    """
    url = "https://api.thetvdb.com/login"
    body = {"apikey": api_key}
    status, content = request_json(url, body=body, cache=False)
    if status == 401:
        raise MapiProviderException("invalid api key")
    elif status != 200 or not content.get("token"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content["token"]


def tvdb_refresh_token(token):
    """
    Refreshes JWT token.

    Online docs: api.thetvdb.com/swagger#!/Authentication/get_refresh_token.
    """
    url = "https://api.thetvdb.com/refresh_token"
    headers = {"Authorization": "Bearer %s" % token}
    status, content = request_json(url, headers=headers, cache=False)
    if status == 401:
        raise MapiProviderException("invalid token")
    elif status != 200 or not content.get("token"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content["token"]


def tvdb_episodes_id(token, id_tvdb, lang="en", cache=True):
    """
    Returns the full information for a given episode id.

    Online docs: https://api.thetvdb.com/swagger#!/Episodes.
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ",".join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = "https://api.thetvdb.com/episodes/%d" % int(id_tvdb)
    except ValueError:
        raise MapiProviderException("id_tvdb must be numeric")
    headers = {"Accept-Language": lang, "Authorization": "Bearer %s" % token}
    status, content = request_json(url, headers=headers, cache=cache)
    if status == 401:
        raise MapiProviderException("invalid token")
    elif status == 404:
        raise MapiNotFoundException
    elif status == 200 and "invalidLanguage" in content.get("errors", {}):
        raise MapiNotFoundException
    elif status != 200 or not content.get("data"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content


def tvdb_series_id(token, id_tvdb, lang="en", cache=True):
    """
    Returns a series records that contains all information known about a
    particular series id.

    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id.
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ",".join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = "https://api.thetvdb.com/series/%d" % int(id_tvdb)
    except ValueError:
        raise MapiProviderException("id_tvdb must be numeric")
    headers = {"Accept-Language": lang, "Authorization": "Bearer %s" % token}
    status, content = request_json(url, headers=headers, cache=cache)
    if status == 401:
        raise MapiProviderException("invalid token")
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get("data"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content


def tvdb_series_id_episodes(token, id_tvdb, page=1, lang="en", cache=True):
    """
    All episodes for a given series.

    Note: Paginated with 100 results per page.
    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id_episodes.
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ",".join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = "https://api.thetvdb.com/series/%d/episodes" % int(id_tvdb)
    except ValueError:
        raise MapiProviderException("id_tvdb must be numeric")
    headers = {"Accept-Language": lang, "Authorization": "Bearer %s" % token}
    parameters = {"page": page}
    status, content = request_json(
        url, parameters, headers=headers, cache=cache
    )
    if status == 401:
        raise MapiProviderException("invalid token")
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get("data"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content


def tvdb_series_id_episodes_query(
    token, id_tvdb, episode=None, season=None, page=1, lang="en", cache=True
):
    """
    Allows the user to query against episodes for the given series.

    Note: Paginated with 100 results per page; omitted imdbId-- when would you
    ever need to query against both tvdb and imdb series ids?
    Online docs: api.thetvdb.com/swagger#!/Series/get_series_id_episodes_query.
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ",".join(TVDB_LANGUAGE_CODES)
        )
    try:
        url = "https://api.thetvdb.com/series/%d/episodes/query" % int(id_tvdb)
    except ValueError:
        raise MapiProviderException("id_tvdb must be numeric")
    headers = {"Accept-Language": lang, "Authorization": "Bearer %s" % token}
    parameters = {"airedSeason": season, "airedEpisode": episode, "page": page}
    status, content = request_json(
        url, parameters, headers=headers, cache=cache
    )
    if status == 401:
        raise MapiProviderException("invalid token")
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200 or not content.get("data"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content


def tvdb_search_series(
    token, series=None, id_imdb=None, id_zap2it=None, lang="en", cache=True
):
    """
    Allows the user to search for a series based on the following parameters.

    Online docs: https://api.thetvdb.com/swagger#!/Search/get_search_series
    Note: results a maximum of 100 entries per page, no option for pagination.
    """
    if lang not in TVDB_LANGUAGE_CODES:
        raise MapiProviderException(
            "'lang' must be one of %s" % ",".join(TVDB_LANGUAGE_CODES)
        )
    url = "https://api.thetvdb.com/search/series"
    parameters = {"name": series, "imdbId": id_imdb, "zap2itId": id_zap2it}
    headers = {"Accept-Language": lang, "Authorization": "Bearer %s" % token}
    status, content = request_json(
        url, parameters, headers=headers, cache=cache
    )
    if status == 401:
        raise MapiProviderException("invalid token")
    elif status == 405:
        raise MapiProviderException(
            "series, id_imdb, id_zap2it parameters are mutually exclusive"
        )
    elif status == 404:  # pragma: no cover
        raise MapiNotFoundException
    elif status != 200 or not content.get("data"):  # pragma: no cover
        raise MapiNetworkException("TVDb down or unavailable?")
    return content
