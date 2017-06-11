# coding=utf-8

from unittest import TestCase

from mapi.providers import *

movie_meta = [{
    'media': 'movie',
    'year': '1985',
    'title': 'The Goonies',
    'id_imdb': 'tt0089218',
}, {
    'media': 'movie',
    'year': '1939',
    'title': 'The Wizard of Oz',
    'id_imdb': 'tt0032138',
}, {
    'media': 'movie',
    'year': '1941',
    'title': 'Citizen Kane',
    'id_imdb': 'tt0033467',
}, {
    'media': 'movie',
    'year': '2017',
    'title': 'Get Out',
    'id_imdb': 'tt5052448',
}, {
    'media': 'movie',
    'year': '1977',
    'title': 'Star Wars: Episode IV - A New Hope',
    'id_imdb': 'tt0076759',
}, {
    'media': 'movie',
    'year': '2001',
    'title': u'Amélie',
    'id_imdb': 'tt0211915',
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


class TestImdb(TestCase):
    def test_registrations(self):
        self.assertTrue(PROVIDER_IMDB == 'imdb')
        self.assertTrue(PROVIDER_IMDB in API_ALL)
        self.assertTrue(PROVIDER_IMDB in API_MOVIE)
        self.assertTrue(has_provider(PROVIDER_IMDB))

    def test_movie_support(self):
        self.assertTrue(PROVIDER_IMDB in API_ALL)
        self.assertTrue(has_provider_support(PROVIDER_IMDB, MEDIA_MOVIE))

    def test_search_id_imdb_static(self):
        client = IMDb()
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = client._search_id_imdb(meta['id_imdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

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

    def test_search_title_static(self):
        client = IMDb()
        for meta in movie_meta:
            with self.subTest(title=meta['title']):
                results = client._search_title(meta['title'])
                has_id = any(meta['id_imdb'] in r['id_imdb'] for r in results)
                self.assertTrue(has_id)

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
