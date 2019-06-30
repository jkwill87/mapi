# coding=utf-8

""" Unit tests for mapi/providers/omdb.py
"""

import pytest

from tests import MOVIE_META


@pytest.mark.usefixtures("omdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_omdb__search_id_imdb(meta, omdb_provider):
    results = list(omdb_provider.search(id_imdb=meta["id_imdb"]))
    assert results
    result = results[0]
    assert meta["title"] == result["title"]


@pytest.mark.usefixtures("omdb_provider")
@pytest.mark.parametrize("meta", MOVIE_META)
def test_omdb__search_title(meta, omdb_provider):
    found = False
    results = list(omdb_provider.search(title=meta["title"]))
    for result in results:
        if result["id_imdb"] == meta["id_imdb"]:
            found = True
            break
    assert found is True
