# coding=utf-8

""" Unit tests for providers.py
"""

import sys
from mapi.providers import *

if sys.version_info.major == 3:
    from unittest import TestCase
else:
    # Sidesteps python2 str/unicode/encode/decode stupidity
    reload(sys)
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    sys.setdefaultencoding('utf-8')
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from unittest2 import TestCase


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
    'id_imdb': 'tt1520211',
    'id_tvdb': '153021'
}, {
    'media': 'television',
    'series': 'Adventure Time',
    'season': '7',
    'episode': '39',
    'title': 'Reboot',
    'id_imdb': 'tt1305826',
    'id_tvdb': '152831'
}, {
    'media': 'television',
    'series': 'Downtown',
    'season': '1',
    'episode': '13',
    'title': 'Trip or Treat',
    'id_imdb': 'tt0208616',
    'id_tvdb': '78342'
}, {
    'media': 'television',
    'series': 'Breaking Bad',
    'season': '3',
    'episode': '5',
    'title': 'Más',
    'id_imdb': 'tt0903747',
    'id_tvdb': '81189'
}, {
    'media': 'television',
    'series': 'The Care Bears',
    'season': '2',
    'episode': '2',
    'title': "Grumpy's Three Wishes",
    'id_imdb': 'tt0284713',
    'id_tvdb': '76079'
}]

API_KEY_TMDB = environ.get(API_KEY_ENV_TMDB)
API_KEY_TVDB = environ.get(API_KEY_ENV_TVDB)

assert API_KEY_TMDB
assert API_KEY_TVDB


class TestHasProvider(TestCase):
    def test_has_provider(self):
        self.assertTrue(has_provider(PROVIDER_IMDB))
        self.assertTrue(has_provider(PROVIDER_TMDB))
        self.assertTrue(has_provider(PROVIDER_TVDB))

    def test_missing_provider(self):
        self.assertFalse(has_provider('omdb'))


class TestHasProviderSupport(TestCase):
    def test_has_provider_has_support(self):
        self.assertTrue(has_provider_support(PROVIDER_IMDB, MEDIA_MOVIE))
        self.assertTrue(has_provider_support(PROVIDER_TMDB, MEDIA_MOVIE))
        self.assertTrue(has_provider_support(PROVIDER_TVDB, MEDIA_TELEVISION))

    def test_has_provider_missing_support(self):
        self.assertFalse(has_provider_support(PROVIDER_IMDB, MEDIA_TELEVISION))
        self.assertFalse(has_provider_support(PROVIDER_TMDB, MEDIA_TELEVISION))
        self.assertFalse(has_provider_support(PROVIDER_TVDB, MEDIA_MOVIE))

    def test_missing_provider_valid_mtype(self):
        self.assertFalse(has_provider_support('omdb', MEDIA_MOVIE))

    def test_missing_provider_invalid_mtype(self):
        self.assertFalse(has_provider_support('omdb', 'media_type_subtitle'))


class TestProviderFactory(TestCase):
    def test_imdb(self):
        client = provider_factory(PROVIDER_IMDB)
        self.assertIsInstance(client, IMDb)

    def test_tmdb(self):
        client = provider_factory(PROVIDER_TMDB, api_key=API_KEY_TMDB)
        self.assertIsInstance(client, TMDb)

    def test_tvdb(self):
        client = provider_factory(PROVIDER_TVDB, api_key=API_KEY_TVDB)
        self.assertIsInstance(client, TVDb)

    def test_non_existant(self):
        with self.assertRaises(MapiException):
            provider_factory('yolo')


class TestImdb(TestCase):
    def setUp(self):
        self.client = IMDb(api_key=API_KEY_TMDB, max_hits=10)

    def test_registrations(self):
        self.assertTrue(PROVIDER_IMDB == 'imdb')
        self.assertTrue(PROVIDER_IMDB in API_ALL)
        self.assertTrue(PROVIDER_IMDB in API_MOVIE)
        self.assertTrue(has_provider(PROVIDER_IMDB))

    def test_movie_support(self):
        self.assertTrue(PROVIDER_IMDB in API_ALL)
        self.assertTrue(has_provider_support(PROVIDER_IMDB, MEDIA_MOVIE))

    def test_search_id_imdb_implicit(self):
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = self.client.search(**meta)
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_imdb_explicit(self):
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = self.client.search(id_imdb=meta['id_imdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_title_implicit(self):
        for meta in movie_meta:
            meta_without_id = {k: v for k, v in meta.items() if k != 'id_imdb'}
            with self.subTest(title=meta['title']):
                results = self.client.search(**meta_without_id)
                has_id = any(meta['id_imdb'] in r['id_imdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_title_explicit(self):
        for meta in movie_meta:
            with self.subTest(title=meta['title']):
                results = self.client.search(title=meta['title'])
                has_id = any(meta['id_imdb'] in r['id_imdb'] for r in results)
                self.assertTrue(has_id)


class TestTmdb(TestCase):
    def setUp(self):
        self.client = TMDb(api_key=API_KEY_TMDB, max_hits=5)

    def test_registrations(self):
        self.assertTrue(PROVIDER_TMDB == 'tmdb')
        self.assertTrue(PROVIDER_TMDB in API_ALL)
        self.assertTrue(PROVIDER_TMDB in API_MOVIE)
        self.assertTrue(has_provider(PROVIDER_TMDB))

    def test_movie_support(self):
        self.assertTrue(PROVIDER_TMDB in API_ALL)
        self.assertTrue(has_provider_support(PROVIDER_TMDB, MEDIA_MOVIE))

    def test_search_id_imdb_implicit(self):
        for meta in movie_meta:
            meta = {m: meta[m] for m in meta if m != 'id_tmdb'}
            with self.subTest(id_imdb=meta['id_imdb']):
                results = self.client.search(**meta)
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_imdb_explicit(self):
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = self.client.search(id_imdb=meta['id_imdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_tmdb_implicit(self):
        for meta in movie_meta:
            with self.subTest(id_tmdb=meta['id_tmdb']):
                results = self.client.search(**meta)
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_id_tmdb_explicit(self):
        for meta in movie_meta:
            with self.subTest(id_tmdb=meta['id_tmdb']):
                results = self.client.search(id_tmdb=meta['id_tmdb'])
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(meta['title'], result['title'])
                self.assertEqual(meta['year'], result['year'])

    def test_search_title_implicit(self):
        for meta in movie_meta:
            meta_without_id = {k: v for k, v in meta.items() if k[:2] != 'id'}
            with self.subTest(title=meta['title']):
                results = self.client.search(**meta_without_id)
                has_id = any(meta['id_tmdb'] in r['id_tmdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_title_explicit(self):
        for meta in movie_meta:
            with self.subTest(title=meta['title']):
                results = self.client.search(title=meta['title'])
                has_id = any(meta['id_tmdb'] in r['id_tmdb'] for r in results)
                self.assertTrue(has_id)


class TestTvdb(TestCase):
    def setUp(self):
        self.client = TVDb(api_key=API_KEY_TVDB, max_hits=5)

    def test_registrations(self):
        self.assertTrue(PROVIDER_TVDB == 'tvdb')
        self.assertTrue(PROVIDER_TVDB in API_ALL)
        self.assertTrue(PROVIDER_TVDB in API_TELEVISION)
        self.assertTrue(has_provider(PROVIDER_TVDB))

    def test_television_support(self):
        self.assertTrue(PROVIDER_TVDB in API_ALL)
        self.assertTrue(has_provider_support(PROVIDER_TVDB, MEDIA_TELEVISION))

    def test_search_id_tvdb(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_tvdb'], series=meta['series']):
                results = self.client.search(id_tvdb=meta['id_tvdb'])
                has_id = any(meta['id_tvdb'] in r['id_tvdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_id_tvdb_season(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_tvdb'], series=meta['series']):
                results = self.client.search(id_tvdb=meta['id_tvdb'], season=1)
                all_season_1 = all(entry['season'] == '1' for entry in results)
                self.assertTrue(all_season_1)

    def test_search_id_tvdb_episode(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_tvdb'], series=meta['series']):
                results = self.client.search(id_tvdb=meta['id_tvdb'], episode=2)
                all_episode_2 = all(
                    entry['episode'] == '2' for entry in results
                )
                self.assertTrue(all_episode_2)

    def test_search_id_tvdb_season_episode(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_tvdb'], series=meta['series']):
                results = self.client.search(id_tvdb=meta['id_tvdb'], season=1,
                    episode=3)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['season'], '1')
                self.assertEqual(results[0]['episode'], '3')

    def test_search_id_imdb(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_imdb'], series=meta['series']):
                results = self.client.search(id_imdb=meta['id_imdb'])
                has_id = any(meta['id_tvdb'] in r['id_tvdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_id_imdb_season(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_imdb'], series=meta['series']):
                results = self.client.search(id_imdb=meta['id_imdb'], season=1)
                all_season_1 = all(entry['season'] == '1' for entry in results)
                self.assertTrue(all_season_1)

    def test_search_id_imdb_episode(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_imdb'], series=meta['series']):
                results = self.client.search(id_imdb=meta['id_imdb'], episode=2)
                all_episode_2 = all(
                    entry['episode'] == '2' for entry in results
                )
                self.assertTrue(all_episode_2)

    def test_search_id_imdb_season_episode(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_imdb'], series=meta['series']):
                results = self.client.search(id_imdb=meta['id_imdb'], season=1,
                    episode=3)
                self.assertEqual(results[0]['season'], '1')
                self.assertEqual(results[0]['episode'], '3')

    def test_search_series(self):
        self.client.max_hits = 5
        for meta in television_meta:
            with self.subTest(series=meta['series']):
                results = self.client.search(series=meta['series'])
                has_id = any(meta['id_tvdb'] in r['id_tvdb'] for r in results)
                self.assertTrue(has_id)

    def test_search_title_season(self):
        for meta in television_meta:
            with self.subTest(series=meta['series']):
                results = self.client.search(series=meta['series'], season=1)
                all_season_1 = all(entry['season'] == '1' for entry in results)
                self.assertTrue(all_season_1)

    def test_search_title_season_episode(self):
        for meta in television_meta:
            with self.subTest(series=meta['series']):
                results = self.client.search(series=meta['series'], season=1,
                    episode=3)
                self.assertEqual(results[0]['season'], '1')
                self.assertEqual(results[0]['episode'], '3')
