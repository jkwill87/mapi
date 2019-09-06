# coding=utf-8

"""Unit tests for mapi/utils.py."""

import pytest
from mock import patch
from requests import Session

from mapi.utils import AGENT_ALL, clean_dict, d2l, get_user_agent, request_json
from tests import MockRequestResponse


@pytest.mark.parametrize("code", [200, 201, 209, 400, 500])
@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__status(mock_request, code):
    mock_response = MockRequestResponse(code, "{}")
    mock_request.return_value = mock_response
    status, _ = request_json("http://...", cache=False)
    assert status == code


@pytest.mark.parametrize(
    "code, truthy", [(200, True), (299, True), (400, False), (500, False)]
)
@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__data(mock_request, code, truthy):
    mock_response = MockRequestResponse(code, '{"status":true}')
    mock_request.return_value = mock_response
    _, content = request_json("http://...", cache=False)
    assert content if truthy else not content


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__json_data(mock_request):
    json_data = """{
        "status": true,
        "data": {
            "title": "The Matrix",
            "year": 1999,
            "genre": null
        }
    }"""
    json_dict = {
        "status": True,
        "data": {"title": "The Matrix", "year": 1999, "genre": None},
    }
    mock_response = MockRequestResponse(200, json_data)
    mock_request.return_value = mock_response
    status, content = request_json("http://...", cache=False)
    assert status == 200
    assert content == json_dict


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__xml_data(mock_request):
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
    status, content = request_json("http://...", cache=False)
    assert status == 500
    assert content is None


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__html_data(mock_request):
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
    status, content = request_json("http://...", cache=False)
    assert status == 500
    assert content is None


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__get_headers(mock_request):
    mock_request.side_effect = Session().request
    request_json(
        url="http://google.com", headers={"apple": "pie", "orange": None}
    )
    _, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert len(kwargs["headers"]) == 2
    assert kwargs["headers"]["apple"] == "pie"
    assert "user-agent" in kwargs["headers"]


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__get_parameters(mock_request):
    test_parameters = {"apple": "pie"}
    mock_request.side_effect = Session().request
    request_json(url="http://google.com", parameters=test_parameters)
    _, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert kwargs["params"] == d2l(test_parameters)


def test_request_json__get_invalid_url():
    status, content = request_json("mapi rulez", cache=False)
    assert status == 500
    assert content is None


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__post_body(mock_request):
    data = {"apple": "pie"}
    mock_request.side_effect = Session().request
    request_json(url="http://google.com", body=data)
    _, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert data == kwargs["json"]


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__post_parameters(mock_request):
    mock_request.side_effect = Session().request
    data = {"apple": "pie", "orange": None}
    request_json(url="http://google.com", body=data, parameters=data)
    _, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert kwargs["params"] == d2l(clean_dict(data))


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__post_headers(mock_request):
    mock_request.side_effect = Session().request
    data = {"apple": "pie", "orange": None}
    request_json(url="http://google.com", body=data, headers=data)
    _, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "apple" in kwargs["headers"]
    assert "orange" not in kwargs["headers"]


@patch("mapi.utils.requests_cache.CachedSession.request")
def test_request_json__failure(mock_request):
    mock_request.side_effect = Exception
    status, content = request_json(url="http://google.com")
    assert status == 500
    assert content is None


def test_clean_dict__str_values():
    dict_in = {"apple": "pie", "candy": "corn", "bologna": "sandwich"}
    dict_out = clean_dict(dict_in)
    assert dict_in == dict_out


def test_clean_dict__some_none():
    dict_in = {
        "super": "mario",
        "sonic": "hedgehog",
        "samus": None,
        "princess": "zelda",
        "bowser": None,
    }
    dict_expect = {"super": "mario", "sonic": "hedgehog", "princess": "zelda"}
    dict_out = clean_dict(dict_in)
    assert dict_expect == dict_out


def test_clean_dict__all_falsy():
    dict_in = {"who": None, "let": 0, "the": False, "dogs": [], "out": ()}
    dict_expect = {"let": "0", "the": "False"}
    dict_out = clean_dict(dict_in)
    assert dict_expect == dict_out


def test_clean_dict__int_values():
    dict_in = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4}
    dict_expect = {"0": "0", "1": "1", "2": "2", "3": "3", "4": "4"}
    dict_out = clean_dict(dict_in)
    assert dict_expect == dict_out


def test_clean_dict__not_a_dict():
    with pytest.raises(AssertionError):
        clean_dict("mama mia pizza pie")


def test_clean_dict__str_strip():
    dict_in = {
        "please": ".",
        "fix ": ".",
        " my spacing": ".",
        "  issues  ": ".",
    }
    dict_expect = {"please": ".", "fix": ".", "my spacing": ".", "issues": "."}
    dict_out = clean_dict(dict_in)
    assert dict_expect == dict_out


def test_clean_dict__whitelist():
    whitelist = {"apple", "raspberry", "pecan"}
    dict_in = {"apple": "pie", "pecan": "pie", "pumpkin": "pie"}
    dict_out = {"apple": "pie", "pecan": "pie"}
    assert clean_dict(dict_in, whitelist) == dict_out


@pytest.mark.parametrize("platform", ["chrome", "edge", "ios"])
def test_get_user_agent__explicit(platform):
    assert get_user_agent(platform) in AGENT_ALL


def test_get_user_agent__random():
    for _ in range(10):
        assert get_user_agent(get_user_agent()) in AGENT_ALL
