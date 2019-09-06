# coding=utf-8

"""Unit tests for mapi/metadata/movie.py."""

import pytest


@pytest.mark.usefixtures("metadata_movie")
def test_str(metadata_movie):
    s = str(metadata_movie)
    assert s == "Saw III (2006)"


@pytest.mark.usefixtures("metadata_movie")
def test_format(metadata_movie):
    s = format(metadata_movie, "TITLE:{title}")
    assert s == "TITLE:Saw III"


@pytest.mark.usefixtures("metadata_movie")
def test_format__missing(metadata_movie):
    metadata_movie["date"] = None
    s = str(metadata_movie)
    assert s == "Saw III"


@pytest.mark.usefixtures("metadata_movie")
def test_format__apostrophes(metadata_movie):
    metadata_movie["title"] = "a bug's life"
    s = format(metadata_movie, "{title}")
    assert s == "A Bug's Life"


@pytest.mark.usefixtures("metadata_movie")
def test_invalid__media(metadata_movie):
    with pytest.raises(ValueError):
        metadata_movie["media"] = "yolo"


@pytest.mark.usefixtures("metadata_movie")
def test_invalid__field(metadata_movie):
    with pytest.raises(KeyError):
        metadata_movie["yolo"] = "hi"


@pytest.mark.usefixtures("metadata_movie")
def test_set_extension__dot(metadata_movie):
    metadata_movie["extension"] = ".mkv"
    assert ".mkv" == metadata_movie["extension"]


@pytest.mark.usefixtures("metadata_movie")
def test_set_extension__no_dot(metadata_movie):
    metadata_movie["extension"] = "mkv"
    assert ".mkv" == metadata_movie["extension"]
