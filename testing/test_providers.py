# coding=utf-8

from unittest import TestCase

from mapi.providers import *

movie_meta = [{
    'media': 'movie',
    'year': '1985',
    'title': 'The Goonies',
    'id_imdb': 'tt0089218',
    'id_tmdb': '9340'
}, {
    'media': 'movie',
    'year': '1939',
    'title': 'The Wizard of Oz',
    'id_imdb': 'tt0032138',
    'id_tmdb': '630'
}, {
    'media': 'movie',
    'year': '1941',
    'title': 'Citizen Kane',
    'id_imdb': 'tt0033467',
    'id_tmdb': '15'
}, {
    'media': 'movie',
    'year': '2017',
    'title': 'Get Out',
    'id_imdb': 'tt5052448',
    'id_tmdb': '419430'
}, {
    'media': 'movie',
    'year': '2001',
    'title': 'Amélie',
    'id_imdb': 'tt0211915',
    'id_tmdb': '194'
}]

television_meta = [{
    'media': 'television',
    'series': 'The Walking Dead',
    'season': '5',
    'episode': '11',
    'title': 'The Distance',
    'id_imdb': 'tt3853916',
}, {
    'media': 'television',
    'series': 'Adventure Time',
    'season': '7',
    'episode': '39',
    'title': 'Reboot',
    'id_imdb': 'tt6186786',
}, {
    'media': 'television',
    'series': 'Downtown ',
    'season': '1',
    'episode': '13',
    'title': 'Trip or Treat',
    'id_imdb': 'tt1181685',
}, {
    'media': 'television',
    'series': 'Breaking Bad',
    'season': '3',
    'episode': '5',
    'title': 'Más',
    'id_imdb': 'tt1615555',
}, {
    'media': 'television',
    'series': 'The Care Bears',
    'season': '2',
    'episode': '2',
    'title': "Grumpy's Three Wishes",
    'id_imdb': 'tt0789891',
}]


class TestProviderFactory(TestCase):
    def test_imdb(self):
        client = provider_factory(PROVIDER_IMDB)
        self.assertIsInstance(client, IMDb)

    def test_tmdb(self):
        client = provider_factory(PROVIDER_TMDB)
        self.assertIsInstance(client, TMDb)

    def test_non_existant(self):
        with self.assertRaises(MapiException):
            provider_factory('yolo')


class TestImdb(TestCase):
    def test_registrations(self):
        self.assertTrue(PROVIDER_IMDB == 'imdb')
        self.assertTrue(PROVIDER_IMDB in API_ALL)
        self.assertTrue(PROVIDER_IMDB in API_MOVIE)
        self.assertTrue(has_provider(PROVIDER_IMDB))

    def test_movie_support(self):
        self.assertTrue(PROVIDER_IMDB in API_ALL)
        self.assertTrue(has_provider_support(PROVIDER_IMDB, MEDIA_MOVIE))

    def test_search_id_imdb_implicit(self):
        client = IMDb()
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = client.search(**meta)
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_imdb_explicit(self):
        client = IMDb()
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = client.search(id_imdb=meta['id_imdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_title_implicit(self):
        client = IMDb()
        for meta in movie_meta:
            meta_without_id = {k: v for k, v in meta.items() if k != 'id_imdb'}
            with self.subTest(title=meta['title']):
                results = client.search(**meta_without_id)
                has_id = any(meta['id_imdb'] in r['id_imdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_title_explicit(self):
        client = IMDb()
        for meta in movie_meta:
            with self.subTest(title=meta['title']):
                results = client.search(title=meta['title'])
                has_id = any(meta['id_imdb'] in r['id_imdb'] for r in results)
                self.assertTrue(has_id)


class TestTmdb(TestCase):
    def test_registrations(self):
        self.assertTrue(PROVIDER_TMDB == 'tmdb')
        self.assertTrue(PROVIDER_TMDB in API_ALL)
        self.assertTrue(PROVIDER_TMDB in API_MOVIE)
        self.assertTrue(has_provider(PROVIDER_TMDB))

    def test_movie_support(self):
        self.assertTrue(PROVIDER_TMDB in API_ALL)
        self.assertTrue(has_provider_support(PROVIDER_TMDB, MEDIA_MOVIE))

    def test_search_id_imdb_implicit(self):
        client = TMDb()
        for meta in movie_meta:
            meta = {m: meta[m] for m in meta if m != 'id_tmdb'}
            with self.subTest(id_imdb=meta['id_imdb']):
                results = client.search(**meta)
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_imdb_explicit(self):
        client = TMDb()
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = client.search(id_imdb=meta['id_imdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_tmdb_implicit(self):
        client = TMDb()
        for meta in movie_meta:
            with self.subTest(id_tmdb=meta['id_tmdb']):
                results = client.search(**meta)
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_tmdb_explicit(self):
        client = TMDb()
        for meta in movie_meta:
            with self.subTest(id_tmdb=meta['id_tmdb']):
                results = client.search(id_tmdb=meta['id_tmdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_title_implicit(self):
        client = TMDb()
        for meta in movie_meta:
            meta_without_id = {k: v for k, v in meta.items() if k[:2] != 'id'}
            with self.subTest(title=meta['title']):
                results = client.search(**meta_without_id)
                has_id = any(meta['id_tmdb'] in r['id_tmdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_title_explicit(self):
        client = TMDb()
        for meta in movie_meta:
            with self.subTest(title=meta['title']):
                results = client.search(title=meta['title'])
                has_id = any(meta['id_tmdb'] in r['id_tmdb'] for r in results)
                self.assertTrue(has_id)
