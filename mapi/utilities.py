# coding=utf-8

import json
import random

import requests
import requests_cache

from mapi.constants import *


def request_json(url, parameters=None, body=None, headers=None, agent=None):
    assert url
    status = 400

    if isinstance(headers, dict):
        headers = clean_dict(headers)
    if isinstance(parameters, dict):
        parameters = clean_dict(parameters)
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
    try:
        response = requests.request(
            url=url,
            params=parameters,
            json=body,
            headers=headers,
            method=method,
        )
        status = response.status_code
        content = response.json() if status // 100 == 2 else None
    except (requests.RequestException, ValueError):
        content = None
    return status, content


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
    if year and isinstance(year_delta, int):
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
    }.get(platform, random.choice(USER_AGENT_ALL))


# Setup requests caching
requests_cache.install_cache('.mapi', expire_after=604800)  # week
