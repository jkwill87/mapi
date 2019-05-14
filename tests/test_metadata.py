# coding=utf-8

""" Unit tests for metadata.py
"""

from mapi.metadata import Metadata, MetadataMovie, MetadataTelevision
from . import *


class TestMetadata(TestCase):
    def setUp(self):
        self.metadata = Metadata(title="Home Movies", date="2019-05-23")

    def test_str(self):
        s = str(self.metadata)
        self.assertEqual("Home Movies", s)

    def test_str__fallback(self):
        self.metadata["title"] = None
        s = str(self.metadata)
        self.assertEqual(Metadata._fallback_str, s)

    def test_iter(self):
        keys = {key for key, _ in self.metadata.items()}
        self.assertEqual(len(keys), 2)
        self.assertIn("title", keys)
        self.assertIn("date", keys)

    def test_iter__no_none(self):
        self.metadata["date"] = None
        keys = {key for key, _ in self.metadata.items()}
        self.assertEqual(len(keys), 1)
        self.assertIn("title", keys)
        self.assertNotIn("date", keys)

    def test_get(self):
        s = self.metadata.get("title")
        self.assertEqual("Home Movies", s)
        s = self.metadata["title"]
        self.assertEqual("Home Movies", s)

    def test_get__case_insensitive(self):
        s = self.metadata.get("TITLE")
        self.assertEqual("Home Movies", s)
        s = self.metadata["tItLe"]
        self.assertEqual("Home Movies", s)

    def test_len(self):
        l = len(self.metadata)
        self.assertEqual(2, l)

    def test_len__no_none(self):
        self.metadata["title"] = None
        l = len(self.metadata)
        self.assertEqual(1, l)

    def test_format(self):
        s = format(self.metadata, "{title} - {date}")
        self.assertEqual("Home Movies - 2019-05-23", s)

    def test_format__whitespace(self):
        s = format(self.metadata, "{title} - {date}  ")
        self.assertEqual("Home Movies - 2019-05-23", s)
        s = format(self.metadata, "  {title} - {date}")
        self.assertEqual("Home Movies - 2019-05-23", s)
        s = format(self.metadata, "{title}    -    {date}")
        self.assertEqual("Home Movies - 2019-05-23", s)
        s = format(self.metadata, "{title} - - {date}")
        self.assertEqual("Home Movies - 2019-05-23", s)

    def test_deletion__valid_key(self):
        del self.metadata["title"]
        self.assertIsNone(self.metadata["title"])

    def test_deletion__invalid_kety(self):
        with self.assertRaises(KeyError):
            del self.metadata["cats"]


class TestMetadataMovie(TestCase):
    def setUp(self):
        self.metadata = MetadataMovie(
            media="movie", title="saw iii", date="2006-01-01"
        )

    def test_str(self):
        s = str(self.metadata)
        self.assertEqual("Saw III (2006)", s)

    def test_format(self):
        s = format(self.metadata, "TITLE:{title}")
        self.assertEqual("TITLE:Saw III", s)

    def test_format__missing(self):
        self.metadata["date"] = None
        s = str(self.metadata)
        self.assertEqual("Saw III", s)

    def test_format__apostrophes(self):
        self.metadata["title"] = "a bug's life"
        s = format(self.metadata, "{title}")
        self.assertEqual("A Bug's Life", s)

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

    def test_str(self):
        s = str(self.metadata)
        self.assertEqual("Adventure Time - 05x03 - Five More Short Graybles", s)

    def test_format(self):
        s = format(
            self.metadata, "{series} - S{season:02}E{episode:02} - {title}"
        )
        self.assertEqual(
            "Adventure Time - S05E03 - Five More Short Graybles", s
        )

    def test_format__missing_episode(self):
        self.metadata["episode"] = None
        s = str(self.metadata)
        self.assertEqual("Adventure Time - 05x - Five More Short Graybles", s)

    def test_format__missing_title(self):
        self.metadata["title"] = None
        s = str(self.metadata)
        self.assertEqual("Adventure Time - 05x03", s)

    def test_format__multi_episode(self):
        self.metadata["episode"] = (3, 4)
        self.assertIsInstance(self.metadata["episode"], int)
        s = str(self.metadata)
        self.assertEqual("Adventure Time - 05x03 - Five More Short Graybles", s)

    def test_invalid_media(self):
        with self.assertRaises(ValueError):
            self.metadata["media"] = "yolo"

    def test_invalid_field(self):
        with self.assertRaises(KeyError):
            self.metadata["yolo"] = "hi"
