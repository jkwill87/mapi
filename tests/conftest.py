# coding=utf-8

"""Shared fixtures automatically imported by PyTest."""

from os import environ

import pytest


@pytest.fixture
def metadata():
    """Creates a Metadata object."""
    from mapi.metadata.metadata import Metadata

    return Metadata(title="Home Movies", date="2019-05-23")


@pytest.fixture
def metadata_movie():
    """Creates a MetadataMovie object."""
    from mapi.metadata.metadata_movie import MetadataMovie

    return MetadataMovie(media="movie", title="saw iii", date="2006-01-01")


@pytest.fixture
def metadata_television():
    """Creates a MetadataTelevision object."""
    from mapi.metadata.metadata_television import MetadataTelevision

    return MetadataTelevision(
        media="television",
        series="adventure time",
        season=5,
        episode=3,
        title="Five More Short Graybles",
    )


@pytest.fixture
def omdb_api_key():
    """Returns testing API key for OMDb."""
    key = environ.get("API_KEY_OMDB")
    assert key
    return key


@pytest.fixture
@pytest.mark.usefixtures("omdb_api_key")
def omdb_provider(omdb_api_key):
    """Returns a fresh OMDb provider object."""
    from mapi.providers import OMDb

    return OMDb(api_key=omdb_api_key)


@pytest.fixture()
def tmdb_api_key():
    """Returns testing API key for TMDb."""
    key = environ.get("API_KEY_TMDB")
    assert key
    return key


@pytest.fixture()
@pytest.mark.usefixtures("tmdb_api_key")
def tmdb_provider(tmdb_api_key):
    """Returns a fresh TMDb provider object."""
    from mapi.providers import TMDb

    return TMDb(api_key=tmdb_api_key)


@pytest.fixture()
def tvdb_api_key():
    """Returns testing API key for TVDb."""
    key = environ.get("API_KEY_TVDB")
    assert key
    return key


@pytest.fixture()
@pytest.mark.usefixtures("tvdb_api_key")
def tvdb_provider(tvdb_api_key):
    """Returns a fresh TVDb provider object."""
    from mapi.providers import TVDb

    return TVDb(api_key=tvdb_api_key)


@pytest.fixture()
@pytest.mark.usefixtures("tvdb_api_key")
def tvdb_token(tvdb_api_key):
    """Calls mapi.endpoints.tvdb_login then returns cached token."""
    if not hasattr(tvdb_token, "token"):
        from mapi.endpoints.tvdb import tvdb_login

        tvdb_token.token = tvdb_login(tvdb_api_key)
    return tvdb_token.token
