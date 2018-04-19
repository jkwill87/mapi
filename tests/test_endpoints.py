from json import loads
from os import environ

from requests import Session

from mapi import IS_PY2
from mapi.endpoints import *
# noinspection PyProtectedMember
from mapi.endpoints import _clean_dict, _d2l, _get_user_agent, _request_json
from mapi.exceptions import *

if IS_PY2:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from unittest2 import TestCase, skip
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from mock import patch
else:
    from unittest import TestCase, skip
    # noinspection PyCompatibility
    from unittest.mock import patch

""" Unit tests for endpoints.py
"""

JUNK_IMDB_ID = 'tt1234567890'
JUNK_TEXT = 'asdf#$@#g9765sdfg54hggaw'
TMDB_API_KEY = environ.get('API_KEY_TMDB')
TVDB_API_KEY = environ.get('API_KEY_TVDB')
GOONIES_IMDB_ID = 'tt0089218'
GOONIES_TMDB_ID = 9340
LOST_TVDB_ID_EPISODE = 127131
LOST_TVDB_ID_SERIES = 73739
LOST_IMDB_ID_SERIES = 'tt0411008'

assert TVDB_API_KEY
assert TMDB_API_KEY


class MockRequestResponse:
    def __init__(self, status, content):
        self.status_code = status
        self.content = content

    def json(self):
        return loads(self.content)


class TestRequestJson(TestCase):
    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_2xx_status(self, mock_request):
        with self.subTest(code=200):
            mock_response = MockRequestResponse(200, '{}')
            mock_request.return_value = mock_response
            status, _ = _request_json('http://...')
            self.assertEqual(status, 200)
        with self.subTest(code=299):
            mock_response = MockRequestResponse(299, '{}')
            mock_request.return_value = mock_response
            status, _ = _request_json('http://...')
            self.assertEqual(status, 299)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_4xx_status(self, mock_request):
        mock_response = MockRequestResponse(400, '{}')
        mock_request.return_value = mock_response
        status, _ = _request_json('http://...')
        self.assertEqual(status, 400)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_5xx_status(self, mock_request):
        mock_response = MockRequestResponse(500, '{}')
        mock_request.return_value = mock_response
        status, _ = _request_json('http://...')
        self.assertEqual(status, 500)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_2xx_data(self, mock_request):
        with self.subTest(code=200):
            mock_response = MockRequestResponse(200, '{"status":true}')
            mock_request.return_value = mock_response
            _, content = _request_json('http://...')
            self.assertTrue(content)
        with self.subTest(code=299):
            mock_response = MockRequestResponse(299, '{"status":true}')
            mock_request.return_value = mock_response
            _, content = _request_json('http://...')
            self.assertTrue(content)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_4xx_data(self, mock_request):
        mock_response = MockRequestResponse(400, '{"status":false}')
        mock_request.return_value = mock_response
        _, content = _request_json('http://...')
        self.assertIsNone(content)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_5xx_data(self, mock_request):
        mock_response = MockRequestResponse(500, '{"status":false}')
        mock_request.return_value = mock_response
        _, content = _request_json('http://...')
        self.assertIsNone(content)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_json_data(self, mock_request):
        json_data = """{
            "status": true,
            "data": {
                "title": "The Matrix",
                "year": 1999,
                "genre": null
            }
        }"""
        json_dict = {
            'status': True,
            'data': {
                'title': 'The Matrix',
                'year': 1999,
                'genre': None
            }
        }
        mock_response = MockRequestResponse(200, json_data)
        mock_request.return_value = mock_response
        status, content = _request_json('http://...')
        self.assertEqual(status, 200)
        self.assertDictEqual(content, json_dict)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_xml_data(self, mock_request):
        xml_data = """
            <?xml version="1.0" encoding="UTF-8" ?>
            <status>true</status>
            <data>
                <title>The Matrix</title>
                <year>1999</year>
                <genre />
            </data>
        """

        mock_response = MockRequestResponse(200, xml_data)
        mock_request.return_value = mock_response
        status, content = _request_json('http://...')
        self.assertEqual(200, status)
        self.assertIsNone(content)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_html_data(self, mock_request):
        html_data = """
            <!DOCTYPE html>
            <html>
                <body>   
                    <h1>Data</h1>
                    <ul>
                    <li>Title: The Matrix</li>
                    <li>Year: 1999</li>
                    <li>Genre: ???</li>
                    </ul>
                </body>
            </html>
        """
        mock_response = MockRequestResponse(200, html_data)
        mock_request.return_value = mock_response
        status, content = _request_json('http://...')
        self.assertEqual(200, status)
        self.assertIsNone(content)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_get_headers(self, mock_request):
        mock_request.side_effect = Session().request
        _request_json(
            url='http://google.com',
            headers={'apple': 'pie', 'orange': None}
        )
        _, kwargs = mock_request.call_args
        self.assertEqual('GET', kwargs['method'])
        self.assertEqual(2, len(kwargs['headers']))
        self.assertEqual('pie', kwargs['headers']['apple'])
        self.assertIn('user-agent', kwargs['headers'])

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_get_parameters(self, mock_request):
        test_parameters = {'apple': 'pie'}
        mock_request.side_effect = Session().request
        _request_json(
            url='http://google.com',
            parameters=test_parameters
        )
        _, kwargs = mock_request.call_args
        self.assertEqual('GET', kwargs['method'])
        self.assertTrue(kwargs['params'] == _d2l(test_parameters))

    def test_get_invalid_url(self):
        status, content = _request_json('mapi rulez')
        self.assertEqual(400, status)
        self.assertIsNone(content)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_post_body(self, mock_request):
        data = {'apple': 'pie'}
        mock_request.side_effect = Session().request
        _request_json(
            url='http://google.com',
            body=data
        )
        _, kwargs = mock_request.call_args
        self.assertEqual('POST', kwargs['method'])
        self.assertDictEqual(kwargs['json'], data)

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_post_parameters(self, mock_request):
        mock_request.side_effect = Session().request
        data = {'apple': 'pie', 'orange': None}
        _request_json(
            url='http://google.com',
            body=data,
            parameters=data
        )
        _, kwargs = mock_request.call_args
        self.assertEqual('POST', kwargs['method'])
        self.assertListEqual(_d2l(_clean_dict(data)), kwargs['params'])

    @patch('mapi.endpoints.requests_cache.CachedSession.request')
    def test_post_headers(self, mock_request):
        mock_request.side_effect = Session().request
        data = {'apple': 'pie', 'orange': None}
        _request_json(
            url='http://google.com',
            body=data,
            headers=data
        )
        _, kwargs = mock_request.call_args
        self.assertEqual('POST', kwargs['method'])
        self.assertIn('apple', kwargs['headers'])
        self.assertNotIn('orange', kwargs['headers'])


class TestCleanDict(TestCase):
    def test_str_values(self):
        dict_in = {
            'apple': 'pie',
            'candy': 'corn',
            'bologna': 'sandwich'
        }
        dict_out = _clean_dict(dict_in)
        self.assertDictEqual(dict_out, dict_in)

    def test_some_none(self):
        dict_in = {
            'super': 'mario',
            'sonic': 'hedgehog',
            'samus': None,
            'princess': 'zelda',
            'bowser': None
        }
        dict_expect = {
            'super': 'mario',
            'sonic': 'hedgehog',
            'princess': 'zelda',
        }
        dict_out = _clean_dict(dict_in)
        self.assertDictEqual(dict_expect, dict_out)

    def test_all_falsy(self):
        dict_in = {
            'who': None,
            'let': 0,
            'the': False,
            'dogs': [],
            'out': ()
        }
        dict_expect = {
            'let': '0',
            'the': 'False'
        }
        dict_out = _clean_dict(dict_in)
        self.assertDictEqual(dict_expect, dict_out)

    def test_int_values(self):
        dict_in = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4
        }
        dict_expect = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }
        dict_out = _clean_dict(dict_in)
        self.assertDictEqual(dict_expect, dict_out)

    def test_not_a_dict(self):
        with self.assertRaises(AssertionError):
            # noinspection PyTypeChecker
            _clean_dict('mama mia pizza pie')

    def test_str_strip(self):
        dict_in = {
            'please': '.',
            'fix ': '.',
            ' my spacing': '.',
            '  issues  ': '.',
        }
        dict_expect = {
            'please': '.',
            'fix': '.',
            'my spacing': '.',
            'issues': '.',
        }
        dict_out = _clean_dict(dict_in)
        self.assertDictEqual(dict_expect, dict_out)

    def test_whitelist(self):
        whitelist = {'apple', 'raspberry', 'pecan'}
        dict_in = {'apple': 'pie', 'pecan': 'pie', 'pumpkin': 'pie'}
        dict_out = {'apple': 'pie', 'pecan': 'pie'}
        self.assertDictEqual(dict_out, _clean_dict(dict_in, whitelist))


class TestGetUserAgent(TestCase):
    def test_explicit(self):
        for platform in {'chrome', 'edge', 'ios'}:
            with self.subTest(platform=platform):
                self.assertIn(_get_user_agent(platform), AGENT_ALL)

    def test_random(self):
        for i in range(10):
            self.assertIn(_get_user_agent(), AGENT_ALL)


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
            'poster_path',
            'release_date',
            'title',
            'video',
            'vote_average',
            'vote_count'
        }
        result = tmdb_find(TMDB_API_KEY, 'imdb_id', GOONIES_IMDB_ID)
        self.assertIsInstance(result, dict)
        self.assertSetEqual(expected_top_level_keys, set(result.keys()))
        self.assertGreater(len(result.get('movie_results', {})), 0)
        self.assertSetEqual(
            expected_movie_results_keys,
            set(result.get('movie_results', {})[0].keys())
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
        self.assertSetEqual(expected_top_level_keys, set(result.keys()))
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
        self.assertSetEqual(expected_top_level_keys, set(result.keys()))
        self.assertIsInstance(result['results'], list)
        self.assertSetEqual(
            expected_results_keys,
            set(result.get('results', [{}])[0].keys())
        )
        self.assertEqual(1, len(result['results']))
        self.assertEqual(result['results'][0]['original_title'], 'The Goonies')
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


class TestTvdbLogin(TestCase):
    def test_login_success(self):
        self.assertIsNotNone(tvdb_login(TVDB_API_KEY))

    def test_login_fail(self):
        with self.assertRaises(MapiProviderException):
            tvdb_login(JUNK_TEXT)


class TestTvdbRefreshToken(TestCase):
    def test_refresh_success(self):
        token = tvdb_login(TVDB_API_KEY)
        self.assertIsNotNone(tvdb_refresh_token(token))

    def test_refresh_fail(self):
        with self.assertRaises(MapiProviderException):
            tvdb_refresh_token(JUNK_TEXT)


class TestTvdbEpisodesId(TestCase):
    def setUp(self):
        self.token = tvdb_login(TVDB_API_KEY)

    @skip('Incompatible with requests_cache')
    def test_invalid_token(self):
        with self.assertRaises(MapiProviderException):
            tvdb_episodes_id(JUNK_TEXT, LOST_TVDB_ID_EPISODE)

    def test_invalid_lang(self):
        with self.assertRaises(MapiProviderException):
            tvdb_episodes_id(self.token, LOST_TVDB_ID_EPISODE, lang=JUNK_TEXT)

    def test_invalid_id_imdb(self):
        with self.assertRaises(MapiProviderException):
            tvdb_episodes_id(self.token, JUNK_TEXT)

    def test_no_hits(self):
        with self.assertRaises(MapiNotFoundException):
            tvdb_episodes_id(self.token, LOST_TVDB_ID_EPISODE ** 2)

    def test_success(self):
        expected_top_level_keys = {
            'absoluteNumber',
            'airedEpisodeNumber',
            'airedSeason',
            'airedSeasonID',
            'airsAfterSeason',
            'airsBeforeEpisode',
            'airsBeforeSeason',
            'director',
            'directors',
            'dvdChapter',
            'dvdDiscid',
            'dvdEpisodeNumber',
            'dvdSeason',
            'episodeName',
            'filename',
            'firstAired',
            'guestStars',
            'id',
            'imdbId',
            'language',
            'lastUpdated',
            'lastUpdatedBy',
            'overview',
            'productionCode',
            'seriesId',
            'showUrl',
            'siteRating',
            'siteRatingCount',
            'thumbAdded',
            'thumbAuthor',
            'thumbHeight',
            'thumbWidth',
            'writers'
        }
        result = tvdb_episodes_id(self.token, LOST_TVDB_ID_EPISODE)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        self.assertSetEqual(expected_top_level_keys, set(result['data'].keys()))
        self.assertEqual(LOST_TVDB_ID_SERIES, result['data']['seriesId'])
        self.assertEqual(LOST_TVDB_ID_EPISODE, result['data']['id'])


class TestTvdbSeriesId(TestCase):
    def setUp(self):
        self.token = tvdb_login(TVDB_API_KEY)

    @skip('Incompatible with requests_cache')
    def test_invalid_token(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_id(JUNK_TEXT, LOST_TVDB_ID_SERIES)

    def test_invalid_lang(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_id(self.token, LOST_TVDB_ID_SERIES, lang=JUNK_TEXT)

    def test_invalid_id_imdb(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_id(self.token, JUNK_TEXT)

    def test_no_hits(self):
        with self.assertRaises(MapiNotFoundException):
            tvdb_series_id(self.token, LOST_TVDB_ID_SERIES * 2)

    def test_success(self):
        expected_top_level_keys = {
            'added',
            'addedBy',
            'airsDayOfWeek',
            'airsTime',
            'aliases',
            'banner',
            'firstAired',
            'genre',
            'id',
            'imdbId',
            'lastUpdated',
            'network',
            'overview',
            'rating',
            'runtime',
            'seriesId',
            'seriesName',
            'siteRating',
            'siteRatingCount',
            'status',
            'zap2itId',
            'networkId'
        }
        result = tvdb_series_id(self.token, LOST_TVDB_ID_SERIES)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        self.assertSetEqual(expected_top_level_keys, set(result['data'].keys()))
        self.assertEqual(LOST_TVDB_ID_SERIES, result['data']['id'])
        self.assertEqual('Lost', result['data']['seriesName'])


class TestTvdbSeriesIdEpisodes(TestCase):
    def setUp(self):
        self.token = tvdb_login(TVDB_API_KEY)

    @skip('Incompatible with requests_cache')
    def test_invalid_token(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_id_episodes(JUNK_TEXT, LOST_TVDB_ID_SERIES)

    def test_invalid_lang(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_id_episodes(self.token, LOST_TVDB_ID_SERIES, lang='xyz')

    def test_invalid_id_imdb(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_id_episodes(self.token, JUNK_TEXT)

    def test_no_hits(self):
        with self.assertRaises(MapiNotFoundException):
            tvdb_series_id_episodes(self.token, LOST_TVDB_ID_SERIES * 2)

    def test_success(self):
        expected_top_level_keys = {
            'absoluteNumber',
            'airedEpisodeNumber',
            'airedSeason',
            'airedSeasonID',
            'dvdEpisodeNumber',
            'dvdSeason',
            'episodeName',
            'firstAired',
            'id',
            'language',
            'lastUpdated',
            'overview'
        }
        result = tvdb_series_id_episodes(self.token, LOST_TVDB_ID_SERIES)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        entry = result['data'][0]
        self.assertSetEqual(expected_top_level_keys, set(entry.keys()))
        self.assertEqual(12, len(entry))
        self.assertEqual(LOST_TVDB_ID_EPISODE, entry['id'])


class TestTvdbSeriesEpisodesQuery(TestCase):
    def setUp(self):
        self.token = tvdb_login(TVDB_API_KEY)

    @skip('Incompatible with requests_cache')
    def test_invalid_token(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_episodes_query(JUNK_TEXT, LOST_TVDB_ID_SERIES)

    def test_invalid_lang(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
                                       lang='xyz')

    def test_invalid_id_tvdb(self):
        with self.assertRaises(MapiProviderException):
            tvdb_series_episodes_query(self.token, JUNK_TEXT)

    def test_page_valid(self):
        tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
            page=1)
        tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
            page=1, season=1)
        tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
            page=1, season=1, episode=1)
        with self.assertRaises(MapiNotFoundException):
            tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
                page=11)
        with self.assertRaises(MapiNotFoundException):
            tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
                page=2, season=1)
        with self.assertRaises(MapiNotFoundException):
            tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
                page=2, season=1, episode=1)

    def test_success_id_tvdb(self):
        expected_top_level_keys = {
            'absoluteNumber',
            'airedEpisodeNumber',
            'airedSeason',
            'airedSeasonID',
            'dvdEpisodeNumber',
            'dvdSeason',
            'episodeName',
            'firstAired',
            'id',
            'language',
            'lastUpdated',
            'overview'
        }
        result = tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        data = result['data']
        self.assertIs(100, len(data))
        self.assertSetEqual(expected_top_level_keys, set(data[0].keys()))
        self.assertEqual(LOST_TVDB_ID_EPISODE, data[0]['id'])

    def test_succeess_id_tvdb_season(self):
        expected_top_level_keys = {
            'absoluteNumber',
            'airedEpisodeNumber',
            'airedSeason',
            'airedSeasonID',
            'dvdEpisodeNumber',
            'dvdSeason',
            'episodeName',
            'firstAired',
            'id',
            'language',
            'lastUpdated',
            'overview'
        }
        result = tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
            season=1)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        data = result['data']
        self.assertIs(24, len(data))
        self.assertSetEqual(set(data[0].keys()), expected_top_level_keys)
        self.assertEqual(LOST_TVDB_ID_EPISODE, data[0]['id'])
        self.assertIsNone(result['links']['prev'])
        self.assertIsNone(result['links']['next'])

    def test_succeess_id_tvdb_season_episode(self):
        expected_top_level_keys = {
            'absoluteNumber',
            'airedEpisodeNumber',
            'airedSeason',
            'airedSeasonID',
            'dvdEpisodeNumber',
            'dvdSeason',
            'episodeName',
            'firstAired',
            'id',
            'language',
            'lastUpdated',
            'overview'
        }
        result = tvdb_series_episodes_query(self.token, LOST_TVDB_ID_SERIES,
            season=1, episode=1)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        data = result['data']
        self.assertIs(1, len(data))
        self.assertSetEqual(set(data[0].keys()), expected_top_level_keys)
        self.assertEqual(LOST_TVDB_ID_EPISODE, data[0]['id'])
        self.assertIsNone(result['links']['prev'])
        self.assertIsNone(result['links']['next'])


class TestTvdbSearchSeries(TestCase):
    def setUp(self):
        self.token = tvdb_login(TVDB_API_KEY)

    @skip('Incompatible with requests_cache')
    def test_invalid_token(self):
        with self.assertRaises(MapiProviderException):
            tvdb_search_series(JUNK_TEXT, 'Lost')

    def test_invalid_lang(self):
        with self.assertRaises(MapiProviderException):
            tvdb_search_series(self.token, 'Lost', lang='xyz')

    def test_invalid_id_imdb(self):
        with self.assertRaises(MapiProviderException):
            tvdb_search_series(self.token, 'Lost', id_imdb='xyz')

    def test_success_series(self):
        expected_top_level_keys = {
            'aliases',
            'banner',
            'firstAired',
            'id',
            'network',
            'overview',
            'seriesName',
            'status'
        }
        result = tvdb_search_series(self.token, 'Lost')
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        data = result['data']
        self.assertIs(100, len(data))
        self.assertSetEqual(set(data[0].keys()), expected_top_level_keys)

    def test_success_series_id_imdb(self):
        expected_top_level_keys = {
            'aliases',
            'banner',
            'firstAired',
            'id',
            'network',
            'overview',
            'seriesName',
            'status'
        }
        result = tvdb_search_series(self.token, id_imdb=LOST_IMDB_ID_SERIES)
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        data = result['data']
        self.assertIs(1, len(data))
        self.assertSetEqual(expected_top_level_keys, set(data[0].keys()))

    def test_success_series_id_zap2it(self):
        pass  # TODO -- not currently used by mapi
