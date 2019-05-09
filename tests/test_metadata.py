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

    def test_invalid_media(self):
        with self.assertRaises(ValueError):
            self.metadata["media"] = "yolo"

    def test_invalid_field(self):
        with self.assertRaises(KeyError):
            self.metadata["yolo"] = "hi"
