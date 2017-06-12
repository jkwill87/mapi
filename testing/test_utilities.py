from unittest import TestCase
from unittest.mock import patch

from mapi.utilities import *


class MockHTTPResponse:
    def __init__(self, status, content):
        self.status = status
        self.content = content

    def read(self):
        return self.content


class TestRequestJson(TestCase):
    @patch('mapi.utilities.urlopen')
    def test_2xx_status(self, mock_urlopen):
        mock_response = MockHTTPResponse(200, b'{}')
        mock_urlopen.return_value = mock_response
        status, _ = request_json('http://...')
        self.assertEqual(status, 200)

    @patch('mapi.utilities.urlopen')
    def test_4xx_status(self, mock_urlopen):
        mock_response = MockHTTPResponse(400, b'{}')
        mock_urlopen.return_value = mock_response
        status, _ = request_json('http://...')
        self.assertEqual(status, 400)

    @patch('mapi.utilities.urlopen')
    def test_5xx_status(self, mock_urlopen):
        mock_response = MockHTTPResponse(500, b'{}')
        mock_urlopen.return_value = mock_response
        status, _ = request_json('http://...')
        self.assertEqual(status, 500)

    @patch('mapi.utilities.urlopen')
    def test_2xx_data(self, mock_urlopen):
        mock_response = MockHTTPResponse(200, b'{"status":true}')
        mock_urlopen.return_value = mock_response
        _, content = request_json('http://...')
        self.assertTrue(content)

    @patch('mapi.utilities.urlopen')
    def test_4xx_data(self, mock_urlopen):
        mock_response = MockHTTPResponse(400, b'{"status":false}')
        mock_urlopen.return_value = mock_response
        _, content = request_json('http://...')
        self.assertIsNone(content)

    @patch('mapi.utilities.urlopen')
    def test_5xx_data(self, mock_urlopen):
        mock_response = MockHTTPResponse(500, b'{"status":false}')
        mock_urlopen.return_value = mock_response
        _, content = request_json('http://...')
        self.assertIsNone(content)

    @patch('mapi.utilities.urlopen')
    def test_json_data(self, mock_urlopen):
        json_data = b"""{
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
        mock_response = MockHTTPResponse(200, json_data)
        mock_urlopen.return_value = mock_response
        status, content = request_json('http://...')
        self.assertEqual(status, 200)
        self.assertDictEqual(content, json_dict)

    @patch('mapi.utilities.urlopen')
    def test_xml_data(self, mock_urlopen):
        xml_data = b"""
            <?xml version="1.0" encoding="UTF-8" ?>
            <status>true</status>
            <data>
                <title>The Matrix</title>
                <year>1999</year>
                <genre />
            </data>
        """

        mock_response = MockHTTPResponse(200, xml_data)
        mock_urlopen.return_value = mock_response
        status, content = request_json('http://...')
        self.assertEqual(status, 400)
        self.assertIsNone(content)

    @patch('mapi.utilities.urlopen')
    def test_html_data(self, mock_urlopen):
        html_data = b"""
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
        mock_response = MockHTTPResponse(200, html_data)
        mock_urlopen.return_value = mock_response
        status, content = request_json('http://...')
        self.assertEqual(status, 400)
        self.assertIsNone(content)

    @patch('mapi.utilities.Request')
    def test_get_headers(self, mock_request):
        mock_request.side_effect = Request
        request_json('http://...', headers={'apple': 'pie', 'orange': None})
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['headers'], {'apple': 'pie'})

    @patch('mapi.utilities.Request')
    def test_get_parameters(self, mock_request):
        test_parameters = {'apple': 'pie'}
        mock_request.side_effect = Request
        request_json(url='http://...', parameters=test_parameters)
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertTrue(kwargs['url'].endswith(urlencode(test_parameters)))

    def test_get_invalid_url(self):
        status, content = request_json('mapi rulez')
        self.assertEqual(status, 400)
        self.assertIsNone(content)

    @patch('mapi.utilities.Request')
    def test_post_body(self, mock_request):
        data = {'apple': 'pie'}
        mock_request.side_effect = Request
        request_json(url='http://...', body=data)
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['data'], b'{"apple": "pie"}')

    @patch('mapi.utilities.Request')
    def test_post_parameters(self, mock_request):
        mock_request.side_effect = Request
        data = {'apple': 'pie', 'orange': None}
        request_json('http://...', body=data, parameters=data)
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertIn('apple', kwargs['url'])
        self.assertNotIn('orange', kwargs['url'])

    @patch('mapi.utilities.Request')
    def test_post_headers(self, mock_request):
        mock_request.side_effect = Request
        data = {'apple': 'pie', 'orange': None}
        request_json('http://...', body=data, headers=data)
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertIn('apple', kwargs['headers'])
        self.assertNotIn('orange', kwargs['headers'])


class TestStripDict(TestCase):
    def test_str_values(self):
        dict_in = {
            'apple': 'pie',
            'candy': 'corn',
            'bologna': 'sandwich'
        }
        dict_out = clean_dict(dict_in)
        self.assertDictEqual(dict_in, dict_out)

    def test_some_none(self):
        dict_in = {
            'super': 'mario',
            'sonic': 'hedgehog',
            'samus': None,
            'princess': 'zelda',
            'bowser': None
        }
        dict_want = {
            'super': 'mario',
            'sonic': 'hedgehog',
            'princess': 'zelda',
        }
        dict_out = clean_dict(dict_in)
        self.assertDictEqual(dict_out, dict_want)

    def test_all_falsy(self):
        dict_in = {
            'who': None,
            'let': ...,
            'the': 0,
            'dogs': False,
            'out': [],
            '?': ()
        }
        dict_want = {
            'the': '0',
            'dogs': 'False'
        }
        dict_out = clean_dict(dict_in)
        self.assertDictEqual(dict_out, dict_want)

    def test_int_values(self):
        dict_in = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4
        }
        dict_want = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }
        dict_out = clean_dict(dict_in)
        self.assertDictEqual(dict_out, dict_want)

    def test_not_a_dict(self):
        with self.assertRaises(AssertionError):
            clean_dict('mama mia pizza pie')

    def test_str_strip(self):
        dict_in = {
            'please': '.',
            'fix ': '.',
            ' my spacing': '.',
            '  issues  ': '.',
        }
        dict_want = {
            'please': '.',
            'fix': '.',
            'my spacing': '.',
            'issues': '.',
        }
        dict_out = clean_dict(dict_in)
        self.assertDictEqual(dict_out, dict_want)


class TestGetUserAgent(TestCase):
    def test_explicit(self):
        for platform in PLATFORM_ALL:
            with self.subTest(platform=platform):
                self.assertIn(get_user_agent(platform), USER_AGENT_ALL)

    def test_random(self):
        for i in range(10):
            self.assertIn(get_user_agent(), USER_AGENT_ALL)


class TestFilterMeta(TestCase):
    def test_nop(self):
        entries_in = list(range(20))
        entries_out = filter_meta(entries_in)
        self.assertListEqual(entries_in, entries_out)

    def test_max_hits(self):
        entries_in = list(range(20))
        entries_out = filter_meta(entries_in, max_hits=25)
        self.assertListEqual(entries_in, entries_out)
        entries_out = filter_meta(entries_in, max_hits=10)
        self.assertListEqual(entries_in[:10], entries_out)

    def test_rm_dupes(self):
        entries_in = list(range(20))
        entries_duped = entries_in + entries_in
        entries_out = filter_meta(entries_duped)
        self.assertListEqual(entries_in, entries_out)

    def test_year_delta(self):
        entries_range = 10
        entries_in = [{'diff': 0, 'year': 2000}]
        for i in range(1, entries_range + 1):
            entries_in.append({'diff': -i, 'year': 2000 - i})
            entries_in.append({'diff': +i, 'year': 2000 + i})

        for i in range(entries_range + 1):
            with self.subTest(diff=i):
                entries_out = filter_meta(entries_in, year=2000, year_delta=i)
                for j in range(i + 1):
                    self.assertEquals(
                        j <= i,
                        2000 - j in [e['year'] for e in entries_out]
                    )
                    self.assertEquals(
                        j <= i,
                        2000 + j in [e['year'] for e in entries_out]
                    )
