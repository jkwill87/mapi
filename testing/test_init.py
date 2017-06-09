# coding=utf-8

from unittest import TestCase

from mapi import *


class TestHasProvider(TestCase):
    def test_has_provider(self):
        self.assertTrue(has_provider(DB_IMDB))
        self.assertTrue(has_provider(DB_TMDB))
        self.assertTrue(has_provider(DB_TVDB))

    def test_missing_provider(self):
        self.assertFalse(has_provider('omdb'))


class TestHasProviderSupport(TestCase):
    def test_has_provider_has_support(self):
        self.assertTrue(has_provider_support(DB_IMDB, MEDIA_TYPE_MOVIE))
        self.assertTrue(has_provider_support(DB_TMDB, MEDIA_TYPE_MOVIE))
        self.assertTrue(has_provider_support(DB_TVDB, MEDIA_TYPE_TELEVISION))

    def test_has_provider_missing_support(self):
        self.assertFalse(has_provider_support(DB_IMDB, MEDIA_TYPE_TELEVISION))
        self.assertFalse(has_provider_support(DB_TMDB, MEDIA_TYPE_TELEVISION))
        self.assertFalse(has_provider_support(DB_TVDB, MEDIA_TYPE_MOVIE))

    def test_missing_provider_valid_mtype(self):
        self.assertFalse(has_provider_support('omdb', MEDIA_TYPE_MOVIE))

    def test_missing_provider_invalid_mtype(self):
        self.assertFalse(has_provider_support('omdb', 'media_type_subtitle'))
