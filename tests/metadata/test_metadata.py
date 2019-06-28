# coding=utf-8

""" Unit tests for mapi/metadata/_base.py
"""

import pytest


def test_str__fallback(metadata):
    metadata["title"] = None
    s = str(metadata)
    assert metadata.__class__._fallback_str == s


def test_str(metadata):
    s = str(metadata)
    assert s == "Home Movies"


def test_iter(metadata):
    keys = {key for key, _ in metadata.items()}
    assert 2 == len(keys)
    assert "title" in keys
    assert "date" in keys


def test_iter__no_none(metadata):
    metadata["date"] = None
    keys = {key for key, _ in metadata.items()}
    assert 1 == len(keys)
    assert "title" in keys
    assert "date" not in keys


def test_get(metadata):
    s = metadata.get("title")
    assert s == "Home Movies"
    s = metadata["title"]
    assert s == "Home Movies"


def test_get__case_insensitive(metadata):
    s = metadata.get("TITLE")
    assert s == "Home Movies"
    s = metadata["tItLe"]
    assert s == "Home Movies"


def test_len(metadata):
    l = len(metadata)
    assert l == 2


def test_len__no_none(metadata):
    metadata["title"] = None
    l = len(metadata)
    assert l == 1


def test_format(metadata):
    s = format(metadata, "{title} - {date}")
    assert s == "Home Movies - 2019-05-23"


def test_format__whitespace(metadata):
    s = format(metadata, "{title} - {date}  ")
    assert s == "Home Movies - 2019-05-23"
    s = format(metadata, "  {title} - {date}")
    assert s == "Home Movies - 2019-05-23"
    s = format(metadata, "{title}    -    {date}")
    assert s == "Home Movies - 2019-05-23"
    s = format(metadata, "{title} - - {date}")
    assert s == "Home Movies - 2019-05-23"


def test_deletion__valid_key(metadata):
    del metadata["title"]
    assert metadata["title"] is None


def test_deletion__invalid_key(metadata):
    with pytest.raises(KeyError):
        del metadata["cats"]
