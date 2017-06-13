from unittest import TestCase

from mapi.endpoints import *

RANDOM_JUNK = 'asdf#$@#g9765sdfg54hggaw'


class TestImdbMainDetails(TestCase):
    def test_success(self):
        response = imdb_main_details('tt0089218')

        self.assertTrue(response)
        self.assertIn('data', response)

        self.assertIn('tconst', response['data'])
        self.assertEqual('tt0089218', response['data']['tconst'])

        self.assertIn('title', response['data'])
        self.assertEqual('The Goonies', response['data']['title'])

        self.assertIn('type', response['data'])
        self.assertEqual('feature', response['data']['type'])

        self.assertIn('year', response['data'])
        self.assertEqual('1985', response['data']['year'])

        self.assertIn('plot', response['data'])
        self.assertIn('outline', response['data']['plot'])

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            imdb_main_details(RANDOM_JUNK)
        with self.assertRaises(MapiNotFoundException):
            imdb_main_details('')
        with self.assertRaises(MapiNotFoundException):
            imdb_main_details('The Goonies')


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

        response = imdb_mobile_find('The Goonies')
        self.assertTrue(response)
        for field, sub_fields in expected_field_mappings.items():
            self.assertIn(field, response)
            self.assertTrue(response[field])
            for subfield in sub_fields:
                self.assertIn(subfield, response[field][0])

    def test_not_found(self):
        with self.assertRaises(MapiNotFoundException):
            imdb_mobile_find(RANDOM_JUNK)
        with self.assertRaises(MapiNotFoundException):
            imdb_mobile_find('')
        with self.assertRaises(MapiNotFoundException):
            imdb_mobile_find('tt0089218')
