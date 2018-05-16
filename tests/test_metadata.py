# coding=utf-8

""" Unit tests for metadata.py
"""

from . import *
from mapi.metadata import MetadataMovie, MetadataTelevision


class TestMetadataMovieFormat(TestCase):
    def setUp(self):
        self.metadata = MetadataMovie(
            media='movie',
            title='saw iii',
            date='2006-01-01'
        )

    def test_format_default(self):
        s = self.metadata.format()
        self.assertEqual('Saw III (2006)', s)

    def test_format_override(self):
        s = self.metadata.format('TITLE:<$title>')
        self.assertEqual('TITLE:Saw III', s)

    def test_format_missing(self):
        self.metadata['date'] = None
        s = self.metadata.format()
        self.assertEqual('Saw III', s)

    def test_invalid_media(self):
        with self.assertRaises(ValueError):
            self.metadata['media'] = 'yolo'

    def test_invalid_field(self):
        with self.assertRaises(KeyError):
            self.metadata['yolo'] = 'hi'


class TestMetadataTelevisionFormat(TestCase):
    def setUp(self):
        self.metadata = MetadataTelevision(
            media='television',
            series='adventure time',
            season=5,
            episode=3,
            title='Five More Short Graybles'
        )

    def test_format_default(self):
        s = self.metadata.format()
        self.assertEqual('Adventure Time - 05x03 - Five More Short Graybles', s)

    def test_format_override(self):
        s = self.metadata.format(
            '<$series - >< - S$season><E$episode - >< - $title>'
        )
        self.assertEqual(
            'Adventure Time - S05E03 - Five More Short Graybles', s
        )

    def test_format_missing_episode(self):
        self.metadata['episode'] = None
        s = self.metadata.format()
        self.assertEqual('Adventure Time - 5 - Five More Short Graybles', s)

    def test_format_missing_title(self):
        self.metadata['title'] = None
        s = self.metadata.format()
        self.assertEqual('Adventure Time - 05x03', s)

    def test_invalid_media(self):
        with self.assertRaises(ValueError):
            self.metadata['media'] = 'yolo'

    def test_invalid_field(self):
        with self.assertRaises(KeyError):
            self.metadata['yolo'] = 'hi'
