# coding=utf-8

""" Unit tests for metadata.py
"""

from mapi.metadata import MetadataMovie, MetadataTelevision
from . import *


class TestMetadataMovie(TestCase):
    def setUp(self):
        self.metadata = MetadataMovie(
            media="movie", title="saw iii", date="2006-01-01"
        )

    def test_format__default(self):
        s = self.metadata.format()
        self.assertEqual("Saw III (2006)", s)

    def test_format__override(self):
        s = self.metadata.format("TITLE:<$title>")
        self.assertEqual("TITLE:Saw III", s)

    def test_format__missing(self):
        self.metadata["date"] = None
        s = self.metadata.format()
        self.assertEqual("Saw III", s)

    def test_format__apostrophes(self):
        self.metadata["title"] = "a bug's life"
        s = self.metadata.format("<$title>")
        self.assertEquals("A Bug's Life", s)

    def test_invalid__media(self):
        with self.assertRaises(ValueError):
            self.metadata["media"] = "yolo"

    def test_invalid__field(self):
        with self.assertRaises(KeyError):
            self.metadata["yolo"] = "hi"

    def test_set_extension__dot(self):
        self.metadata["extension"] = ".mkv"
        self.assertEqual(self.metadata["extension"], ".mkv")

    def test_set_extension__no_dot(self):
        self.metadata["extension"] = "mkv"
        self.assertEqual(self.metadata["extension"], ".mkv")


class TestMetadataTelevision(TestCase):
    def setUp(self):
        self.metadata = MetadataTelevision(
            media="television",
            series="adventure time",
            season=5,
            episode=3,
            title="Five More Short Graybles",
        )

    def test_format_default(self):
        s = self.metadata.format()
        self.assertEqual("Adventure Time - 05x03 - Five More Short Graybles", s)

    def test_format_override(self):
        s = self.metadata.format(
            "<$series - >< - S$season><E$episode - >< - $title>"
        )
        self.assertEqual(
            "Adventure Time - S05E03 - Five More Short Graybles", s
        )

    def test_format_missing_episode(self):
        self.metadata["episode"] = None
        s = self.metadata.format()
        self.assertEqual("Adventure Time - 5 - Five More Short Graybles", s)

    def test_format_missing_title(self):
        self.metadata["title"] = None
        s = self.metadata.format()
        self.assertEqual("Adventure Time - 05x03", s)

    def test_invalid_media(self):
        with self.assertRaises(ValueError):
            self.metadata["media"] = "yolo"

    def test_invalid_field(self):
        with self.assertRaises(KeyError):
            self.metadata["yolo"] = "hi"
