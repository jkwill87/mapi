# coding=utf-8

from mapi.exceptions import (
    MapiNetworkException,
    MapiNotFoundException,
    MapiProviderException,
)
from mapi.utils import clean_dict, request_json

__all__ = ["OMDB_PLOT_TYPES", "OMDB_MEDIA_TYPES", "omdb_search", "omdb_title"]


OMDB_MEDIA_TYPES = {"episode", "movie", "series"}
OMDB_PLOT_TYPES = {"short", "long"}


def omdb_title(
    api_key,
    id_imdb=None,
    media_type=None,
    title=None,
    season=None,
    episode=None,
    year=None,
    plot=None,
    cache=True,
):
    """
    Lookup media using the Open Movie Database.

    Online docs: http://www.omdbapi.com/#parameters
    """
    if (not title and not id_imdb) or (title and id_imdb):
        raise MapiProviderException("either id_imdb or title must be specified")
    elif media_type and media_type not in OMDB_MEDIA_TYPES:
        raise MapiProviderException(
            "media_type must be one of %s" % ",".join(OMDB_MEDIA_TYPES)
        )
    elif plot and plot not in OMDB_PLOT_TYPES:
        raise MapiProviderException(
            "plot must be one of %s" % ",".join(OMDB_PLOT_TYPES)
        )
    url = "http://www.omdbapi.com"
    parameters = {
        "apikey": api_key,
        "i": id_imdb,
        "t": title,
        "y": year,
        "season": season,
        "episode": episode,
        "type": media_type,
        "plot": plot,
    }
    parameters = clean_dict(parameters)
    status, content = request_json(url, parameters, cache=cache)
    error = content.get("Error") if isinstance(content, dict) else None
    if status == 401:
        raise MapiProviderException("invalid API key")
    elif status != 200 or not isinstance(content, dict):
        raise MapiNetworkException("OMDb down or unavailable?")
    elif error:
        raise MapiNotFoundException(error)
    return content


def omdb_search(api_key, query, year=None, media_type=None, page=1, cache=True):
    """
    Search for media using the Open Movie Database.

    Online docs: http://www.omdbapi.com/#parameters.
    """
    if media_type and media_type not in OMDB_MEDIA_TYPES:
        raise MapiProviderException(
            "media_type must be one of %s" % ",".join(OMDB_MEDIA_TYPES)
        )
    if 1 > page > 100:
        raise MapiProviderException("page must be between 1 and 100")
    url = "http://www.omdbapi.com"
    parameters = {
        "apikey": api_key,
        "s": query,
        "y": year,
        "type": media_type,
        "page": page,
    }
    parameters = clean_dict(parameters)
    status, content = request_json(url, parameters, cache=cache)
    if status == 401:
        raise MapiProviderException("invalid API key")
    elif content and not content.get("totalResults"):
        raise MapiNotFoundException()
    elif not content or status != 200:  # pragma: no cover
        raise MapiNetworkException("OMDb down or unavailable?")
    return content
