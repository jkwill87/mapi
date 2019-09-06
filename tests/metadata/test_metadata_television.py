# coding=utf-8

"""Unit tests for mapi/metadata/television.py."""

import pytest


def test_str(metadata_television):
    s = str(metadata_television)
    assert s == "Adventure Time - 05x03 - Five More Short Graybles"


def test_format(metadata_television):
    s = format(
        metadata_television, "{series} - S{season:02}E{episode:02} - {title}"
    )
    assert s == "Adventure Time - S05E03 - Five More Short Graybles"


def test_format__missing_episode(metadata_television):
    metadata_television["episode"] = None
    s = str(metadata_television)
    assert s == "Adventure Time - 05x - Five More Short Graybles"


def test_format__missing_title(metadata_television):
    metadata_television["title"] = None
    s = str(metadata_television)
    assert s == "Adventure Time - 05x03"


def test_format__multi_episode(metadata_television):
    metadata_television["episode"] = (3, 4)
    assert isinstance(metadata_television["episode"], int)
    s = str(metadata_television)
    assert s == "Adventure Time - 05x03 - Five More Short Graybles"


def test_invalid_media(metadata_television):
    with pytest.raises(ValueError):
        metadata_television["media"] = "yolo"


def test_invalid_field(metadata_television):
    with pytest.raises(KeyError):
        metadata_television["yolo"] = "hi"
