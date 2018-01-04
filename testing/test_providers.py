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
    'year': '2002',
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

API_KEY_TMDB = environ.get('API_KEY_TMDB')
API_KEY_TVDB = environ.get('API_KEY_TVDB')

assert API_KEY_TMDB
assert API_KEY_TVDB


class TestHasProvider(TestCase):
    def test_has_provider(self):
        # TODO: Revisit after IMDb endpoints have been reimplemented
        # self.assertTrue(has_provider('imdb'))
        self.assertTrue(has_provider('tmdb'))
        self.assertTrue(has_provider('tvdb'))

    def test_missing_provider(self):
        self.assertFalse(has_provider('omdb'))


class TestHasProviderSupport(TestCase):
    def test_has_provider_has_support(self):
        # TODO: Revisit after IMDb endpoints have been reimplemented
        # self.assertTrue(has_provider_support('imdb', 'movie'))
        self.assertTrue(has_provider_support('tmdb', 'movie'))
        self.assertTrue(has_provider_support('tvdb', 'television'))

    def test_has_provider_missing_support(self):
        # TODO: Revisit after IMDb endpoints have been reimplemented
        # self.assertFalse(has_provider_support('imdb', 'television'))
        self.assertFalse(has_provider_support('tmdb', 'television'))
        self.assertFalse(has_provider_support('tvdb', 'movie'))

    def test_missing_provider_valid_mtype(self):
        self.assertFalse(has_provider_support('omdb', 'movie'))

    def test_missing_provider_invalid_mtype(self):
        self.assertFalse(has_provider_support('omdb', 'media_type_subtitle'))


class TestProviderFactory(TestCase):
    # TODO: Revisit after IMDb endpoints have been reimplemented
    # def test_imdb(self):
    #     client = provider_factory('imdb')
    #     self.assertIsInstance(client, IMDb)

    def test_tmdb(self):
        client = provider_factory('tmdb', api_key=API_KEY_TMDB)
        self.assertIsInstance(client, TMDb)

    def test_tvdb(self):
        client = provider_factory('tvdb', api_key=API_KEY_TVDB)
        self.assertIsInstance(client, TVDb)

    def test_non_existant(self):
        with self.assertRaises(MapiException):
            provider_factory('yolo')

# TODO: Revisit after IMDb endpoints have been reimplemented
# class TestImdb(TestCase):
#     def setUp(self):
#         self.client = IMDb(api_key=API_KEY_TMDB)
#
#     def test_search_id_imdb(self):
#         for meta in movie_meta:
#             with self.subTest(id_imdb=meta['id_imdb']):
#                 results = list(self.client.search(id_imdb=meta['id_imdb']))
#                 self.assertTrue(results)
#                 result = results[0]
#                 self.assertEqual(result['title'], meta['title'])
#
#     def test_search_title(self):
#         for meta in movie_meta:
#             found = False
#             with self.subTest(title=meta['title']):
#                 results = self.client.search(title=meta['title'])
#                 for result in results:
#                     if result['id_imdb'] == meta['id_imdb']:
#                         found = True
#                         break
#                 self.assertTrue(found)


class TestTmdb(TestCase):
    def setUp(self):
        self.client = TMDb(api_key=API_KEY_TMDB)

    def test_search_id_imdb(self):
        for meta in movie_meta:
            with self.subTest(id_imdb=meta['id_imdb']):
                results = list(self.client.search(id_imdb=meta['id_imdb']))
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(result['title'], meta['title'])

    def test_search_id_tmdb(self):
        for meta in movie_meta:
            with self.subTest(id_tmdb=meta['id_tmdb']):
                results = list(self.client.search(id_tmdb=meta['id_tmdb']))
                self.assertTrue(results)
                result = results[0]
                self.assertEqual(result['title'], meta['title'])

    def test_search_title(self):
        for meta in movie_meta:
            found = False
            with self.subTest(title=meta['title']):
                results = list(self.client.search(title=meta['title']))
                for result in results:
                    if result['id_tmdb'] == meta['id_tmdb']:
                        found = True
                        break
                self.assertTrue(found)


class TestTvdb(TestCase):
    def setUp(self):
        self.client = TVDb(api_key=API_KEY_TVDB)

    def test_search_id_tvdb(self):
        for meta in television_meta:
            with self.subTest(id_tvdb=meta['id_tvdb'], series=meta['series']):
                results = list(self.client.search(id_tvdb=meta['id_tvdb']))
                self.assertEqual(results[0]['id_tvdb'], meta['id_tvdb'])

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
                results = list(self.client.search(
                    id_tvdb=meta['id_tvdb'], 
                    season=1,
                    episode=3
                ))
                self.assertEqual(1, len(results))
                self.assertEqual('1', results[0]['season'])
                self.assertEqual('3', results[0]['episode'])

    def test_search_id_imdb(self):
        for meta in television_meta:
            found = False
            with self.subTest(id_tvdb=meta['id_imdb'], series=meta['series']):
                results = self.client.search(id_imdb=meta['id_imdb'])
                for result in results:
                    if result['id_tvdb'] == meta['id_tvdb']:
                        found = True
                        break
                self.assertTrue(found)

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
                results = list(self.client.search(
                    id_imdb=meta['id_imdb'], season=1, episode=3
                ))
                self.assertEqual('1', results[0]['season'])
                self.assertEqual('3', results[0]['episode'])

    def test_search_series(self):
        for meta in television_meta:
            found = False
            with self.subTest(series=meta['series']):
                results = self.client.search(series=meta['series'])
                for result in results:
                    if result['id_tvdb'] == meta['id_tvdb']:
                        found = True
                        break
                self.assertTrue(found)

    def test_search_title_season(self):
        for meta in television_meta:
            with self.subTest(series=meta['series']):
                results = self.client.search(series=meta['series'], season=1)
                all_season_1 = all(entry['season'] == '1' for entry in results)
                self.assertTrue(all_season_1)

    def test_search_title_season_episode(self):
        for meta in television_meta:
            with self.subTest(series=meta['series']):
                results = list(self.client.search(
                    series=meta['series'], season=1, episode=3
                ))
                self.assertEqual('1', results[0]['season'])
                self.assertEqual('3', results[0]['episode'])

    def test_search_series_date_year(self):
        results = list(self.client.search(
            series='The Daily Show', date='2017-11-01'
        ))
        self.assertEqual(1, len(results))
        self.assertTrue(results[0]['title'] == 'Hillary Clinton')

    def test_search_series_date_partial(self):
        results = list(self.client.search(
            series='The Daily Show', date='2017'
        ))
        self.assertLessEqual(170, len(results))
        self.assertTrue(any(r['title'] == 'Hillary Clinton' for r in results))

    def dest_search_series_date_invalid_format(self):
        with self.assertRaises(MapiProviderException):
            self.client.search(series='The Daily Show', date='13')
