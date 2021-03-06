# coding=utf-8

"""Unit tests for mapi/providers/tmdb.py."""

import pytest
from mock import patch

from mapi.exceptions import MapiProviderException
from mapi.providers import TMDb
from tests import JUNK_TEXT, MOVIE_META


def test_tmdb_provider__api_key__missing():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(MapiProviderException):
            TMDb()


def test_tmdb_provider__api_key__env_fallback_ok():
    with patch.dict("os.environ", {"API_KEY_TMDB": JUNK_TEXT}, clear=True):
        TMDb()  # should not raise exception


@pytest.mark.usefixtures("tmdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_tmdb_provider__search_id_imdb(meta, tmdb_provider):
    results = list(tmdb_provider.search(id_imdb=meta["id_imdb"]))
    assert results
    result = results[0]
    assert meta["title"] == result["title"]


@pytest.mark.usefixtures("tmdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_tmdb_provider__search_id_tmdb(meta, tmdb_provider):
    results = list(tmdb_provider.search(id_tmdb=meta["id_tmdb"]))
    assert results
    result = results[0]
    assert meta["title"] == result["title"]


@pytest.mark.usefixtures("tmdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_tmdb_provider__search_title(meta, tmdb_provider):
    found = False
    results = list(tmdb_provider.search(title=meta["title"]))
    for result in results:
        if result["id_tmdb"] == meta["id_tmdb"]:
            found = True
            break
    assert found is True
