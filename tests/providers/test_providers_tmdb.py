# coding=utf-8

""" Unit tests for mapi/providers/tmdb.py
"""

import pytest

from tests import MOVIE_META


@pytest.mark.usefixtures("tmdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_tmdb__search_id_imdb(meta, tmdb_provider):
    results = list(tmdb_provider.search(id_imdb=meta["id_imdb"]))
    assert results
    result = results[0]
    assert meta["title"] == result["title"]


@pytest.mark.usefixtures("tmdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_tmdb__search_id_tmdb(meta, tmdb_provider):
    results = list(tmdb_provider.search(id_tmdb=meta["id_tmdb"]))
    assert results
    result = results[0]
    assert meta["title"] == result["title"]


@pytest.mark.usefixtures("tmdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_tmdb__search_title(meta, tmdb_provider):
    found = False
    results = list(tmdb_provider.search(title=meta["title"]))
    for result in results:
        if result["id_tmdb"] == meta["id_tmdb"]:
            found = True
            break
    assert found is True
