from os import environ
from unittest import TestCase

from mapi.constants import *
from mapi.endpoints import *
from mapi.utilities import session

JUNK_IMDB_ID = 'tt1234567890'
JUNK_TEXT = 'asdf#$@#g9765sdfg54hggaw'
TMDB_API_KEY = environ.get(API_KEY_ENV_TMDB)
TVDB_API_KEY = environ.get(API_KEY_ENV_TVDB)
GOONIES_IMDB_ID = 'tt0089218'
GOONIES_TMDB_ID = 9340
LOST_TVDB_ID_EPISODE = 407452
LOST_TVDB_ID_SERIES = 73739

session.cache.clear()  # clear caches


class TestImdbMainDetails(TestCase):
    def test_success(self):
        result = imdb_main_details(GOONIES_IMDB_ID)

        self.assertTrue(result)
        self.assertIn('data', result)

        self.assertIn('tconst', result['data'])
        self.assertEqual(GOONIES_IMDB_ID, result['data']['tconst'])

        self.assertIn('title', result['data'])
        self.assertEqual('The Goonies', result['data']['title'])

        self.assertIn('type', result['data'])
        self.assertEqual('feature', result['data']['type'])

        self.assertIn('year', result['data'])
        self.assertEqual('1985', result['data']['year'])

        self.assertIn('plot', result['data'])
        self.assertIn('outline', result['data']['plot'])

    def test_invalid_id_imdb(self):
        with self.assertRaises(MapiProviderException):
            imdb_main_details(JUNK_TEXT)
        with self.assertRaises(MapiProviderException):
            imdb_main_details('')
        with self.assertRaises(MapiProviderException):
            imdb_main_details('The Goonies')

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            imdb_main_details(JUNK_IMDB_ID)


class TestImdbMobileFind(TestCase):
    def test_success(self):
        expected_field_mappings = {
            'title_approx': {
                'description',
                'episode_title',
                'id',
                'title',
                'title_description'
            },
            'title_exact': {
                'description',
                'episode_title',
                'id',
                'title',
                'title_description'
            },
            'title_popular': {
                'description',
                'episode_title',
                'id',
                'title',
                'title_description'
            },
            'title_substring': {
                'description',
                'episode_title',
                'name',
                'title',
                'title_description'
            }
        }

        result = imdb_mobile_find('The Goonies')
        self.assertTrue(result)
        for field, sub_fields in expected_field_mappings.items():
            self.assertIn(field, result)
            self.assertTrue(result[field])
            for subfield in sub_fields:
                self.assertIn(subfield, result[field][0])

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            imdb_mobile_find(JUNK_TEXT)
        with self.assertRaises(MapiNotFoundException):
            imdb_mobile_find('')
        with self.assertRaises(MapiNotFoundException):
            imdb_mobile_find(GOONIES_IMDB_ID)


class TestTmdbFind(TestCase):
    def test_imdb_success(self):
        self.assertIsNotNone(TMDB_API_KEY)
        expected_top_level_keys = {
            'movie_results',
            'person_results',
            'tv_episode_results',
            'tv_results',
            'tv_season_results',
        }
        expected_movie_results_keys = {
            'adult',
            'backdrop_path',
            'genre_ids',
            'id',
            'original_language',
            'original_title',
            'overview',
            'release_date',
            'poster_path',
            'popularity',
            'title',
            'video',
            'vote_average',
            'vote_count'
        }
        result = tmdb_find(TMDB_API_KEY, 'imdb_id', GOONIES_IMDB_ID)
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), expected_top_level_keys)
        self.assertGreater(len(result.get('movie_results', {})), 0)
        self.assertSetEqual(
            set(result.get('movie_results', {})[0].keys()),
            expected_movie_results_keys
        )

    def test_api_key_fail(self):
        with self.assertRaises(MapiProviderException):
            tmdb_find(JUNK_TEXT, 'imdb_id', GOONIES_IMDB_ID)

    def test_invalid_id_imdb(self):
        with self.assertRaises(MapiProviderException):
            tmdb_find(TMDB_API_KEY, 'imdb_id', JUNK_TEXT)

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            tmdb_find(TMDB_API_KEY, 'imdb_id', JUNK_IMDB_ID)

    def test_invalid_provider(self):
        with self.assertRaises(MapiProviderException):
            tmdb_find(TMDB_API_KEY, JUNK_TEXT, GOONIES_IMDB_ID)


class TestTmdbMovies(TestCase):
    def test_success(self):
        expected_top_level_keys = {
            'adult',
            'backdrop_path',
            'belongs_to_collection',
            'budget',
            'genres',
            'homepage',
            'id',
            'imdb_id',
            'original_language',
            'original_title',
            'overview',
            'popularity',
            'poster_path',
            'production_companies',
            'production_countries',
            'release_date',
            'revenue',
            'runtime',
            'spoken_languages',
            'status',
            'tagline',
            'title',
            'video',
            'vote_average',
            'vote_count'
        }
        result = tmdb_movies(TMDB_API_KEY, GOONIES_TMDB_ID)
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), expected_top_level_keys)
        self.assertEqual('The Goonies', result.get('original_title'))

    def test_api_key_fail(self):
        with self.assertRaises(MapiProviderException):
            tmdb_movies(JUNK_TEXT, '')

    def test_id_tmdb_fail(self):
        with self.assertRaises(MapiProviderException):
            tmdb_movies(TMDB_API_KEY, JUNK_TEXT)

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            tmdb_movies(TMDB_API_KEY, '1' * 10)


class TestTmdbSearchMovies(TestCase):
    def test_success(self):
        expected_top_level_keys = {
            'page',
            'results',
            'total_pages',
            'total_results'
        }
        expected_results_keys = {
            'adult',
            'backdrop_path',
            'genre_ids',
            'id',
            'original_language',
            'original_title',
            'overview',
            'popularity',
            'poster_path',
            'release_date',
            'title',
            'video',
            'vote_average',
            'vote_count'
        }
        result = tmdb_search_movies(TMDB_API_KEY, 'the goonies', 1985)
        self.assertIsInstance(result, dict)
        self.assertSetEqual(set(result.keys()), expected_top_level_keys)
        self.assertIsInstance(result['results'], list)
        self.assertSetEqual(
            set(result.get('results', [{}])[0].keys()),
            expected_results_keys
        )
        self.assertEqual(len(result['results']), 1)
        self.assertEqual('The Goonies', result['results'][0]['original_title'])
        result = tmdb_search_movies(TMDB_API_KEY, 'the goonies')
        self.assertGreater(len(result['results']), 1)

    def test_api_key_fail(self):
        with self.assertRaises(MapiProviderException):
            tmdb_search_movies(JUNK_TEXT, 'the goonies')

    def test_year_fail(self):
        with self.assertRaises(MapiProviderException):
            tmdb_search_movies(TMDB_API_KEY, 'the goonies', year=JUNK_TEXT)

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            tmdb_search_movies(TMDB_API_KEY, JUNK_TEXT)
