# coding=utf-8

import json
from random import choice
from sys import stderr, version_info

from mapi.constants import *
from mapi.exceptions import MapiNetworkException


# noinspection PyUnusedLocal
def request_json_py2(url, parameters=None, body=None, headers=None, agent=None):
    pass  # TODO


def request_json_py3(url, parameters=None, body=None, headers=None, agent=None):
    if not url:
        return 400, None

    # Format request
    if isinstance(parameters, dict):
        url += '?' + urlencode(clean_dict(parameters))
    if isinstance(headers, dict):
        headers = clean_dict(headers)
    if body:
        method = 'POST'
        if isinstance(body, str):
            body = body.encode()
        elif isinstance(body, dict):
            body = json.dumps(body).encode()
        headers = headers or {}
        headers['content-type'] = 'application/json'
        headers['content-length'] = len(body)
        headers['user-agent'] = get_user_agent(agent)
    else:
        method = 'GET'

    # Perform request
    try:
        request = Request(
            url=url,
            data=body,
            headers=headers or {},
            method=method
        )
        response = urlopen(request)
    except (ValueError, TypeError):
        return 400, None
    except HTTPError as e:
        return e.code, None
    except URLError:
        raise MapiNetworkException
    if response.status != 200:
        return response.status, None

    # Parse JSON
    try:
        content = response.read()
        content = unescape(content.decode())
        content = json.loads(content)
    except ValueError:
        return 400, None
    return response.status, content


def clean_dict(x):
    assert isinstance(x, dict)
    return {
        str(k).strip(): str(v).strip()
        for k, v in x.items()
        if v not in (None, Ellipsis, [], (), '')
    }


def filter_meta(entries, max_hits=None, year_delta=None, year=None):
    assert isinstance(entries, list)

    def year_diff(x):
        return abs(int(x['year']) - int(year))

    # Remove duplicate entries
    unique_entries = list()
    [unique_entries.append(e) for e in entries if e not in unique_entries]
    entries = unique_entries

    # Remove entries outside of year delta for target year, if available
    if year and isinstance(year_delta,int):
        entries = [entry for entry in entries if year_diff(entry) <= year_delta]

        # Sort entries around year
        entries.sort(key=year_diff)

    # Cut off entries after max_hits, if set
    if max_hits:
        entries = entries[:max_hits]
    return entries


def get_user_agent(platform=None):
    return {
        PLATFORM_CHROME: USER_AGENT_CHROME,
        PLATFORM_EDGE: USER_AGENT_EDGE,
        PLATFORM_IOS: USER_AGENT_IOS
    }.get(platform, choice(USER_AGENT_ALL))


# Python version enforcement ---------------------------------------------------
if version_info >= (3, 0):
    # noinspection PyCompatibility
    from html import unescape
    # noinspection PyCompatibility
    from urllib.error import HTTPError, URLError
    # noinspection PyCompatibility
    from urllib.parse import urlencode
    # noinspection PyCompatibility
    from urllib.request import Request, urlopen

    request_json = request_json_py3
elif version_info == (2, 7):
    request_json = request_json_py2
else:
    stderr.write('Incompatible version of python; requires 2.7 or 3+')
    exit(1)
