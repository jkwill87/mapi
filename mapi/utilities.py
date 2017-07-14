# coding=utf-8

""" A collection of internal utility functions used by the package
"""

import json
import random

import requests
import requests_cache

from mapi import log
from mapi.constants import *

# Setup requests caching
requests_cache.install_cache('.mapi', expire_after=604800)  # week


def request_json(url, parameters=None, body=None, headers=None, agent=None):
    """ Queries a url for json data

    Essentially just wraps requests to abstract return values and exceptions

    Note: Requests are cached using requests_cached for a week, this is done
    transparently by using the package's monkey patching

    :param str url: The url to query
    :param dict parameters: Query string parameters
    :param dict body: JSON body parameters; if set implicitly POSTs
    :param optional dict headers: HTTP headers; content type, length, and user
        agent already get set internally
    :param str agent: User agent handle to include in headers; must be one
        specified in the constants module; if unset on will be chosen randomly
    :return: a list where the first item is the numeric status code and the
        second is a dict containing the JSON data retrieved
    :rtype: list
    """
    assert url
    status = 400
    log.info("url: %s" % url)

    if isinstance(headers, dict):
        headers = clean_dict(headers)
        log.info("headers: %s" % headers)
    if isinstance(parameters, dict):
        parameters = clean_dict(parameters)
        log.info("parameters: %s" % parameters)
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
        log.debug("response: %s" % response)
    except (requests.RequestException, ValueError) as e:
        log.debug(e, exc_info=True)
        content = None

    log.info("method: %s" % method)
    log.info("status: %d" % status)
    log.info("content: %s" % content)
    return status, content


def clean_dict(target_dict, whitelist=None):
    """ Convenience function that removes a dicts keys that have falsy values

    :param dict target_dict: the dict to clean
    :param optional set whitelist: if set, will filter keys outside of whitelist
    :return: the cleaned dict
    :rtype: dict
    """
    assert isinstance(target_dict, dict)
    return {
        str(k).strip(): str(v).strip()
        for k, v in target_dict.items()
        if v not in (None, Ellipsis, [], (), '')
        and (not whitelist or k in whitelist)
    }


def filter_meta(entries, max_hits=None, year=None, year_delta=None):
    """ Filters a list of metadata dicts

    Note: this might be a good candidate for future refactoring, perhaps to
    split them up?

    :param list entries: the list of metadata dicts
    :param int max_hits: the maximum number of entries to include in the list
    :param int or str year: the target year to filter around
    :param int year_delta: results are filtered around this value inclusively
    :return: the filtered list of entries
    :rtype: dict
    """
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
    """ Convenience function that looks up a user agent string, random if N/A

    Valid platforms are listed in the constants module

    :param optional str platform: the platform for the required user agent string
    :return: the user agent string
    :rtype: str
    """
    if isinstance(platform, str):
        platform = platform.upper()
    return {
        PLATFORM_CHROME: USER_AGENT_CHROME,
        PLATFORM_EDGE: USER_AGENT_EDGE,
        PLATFORM_IOS: USER_AGENT_IOS
    }.get(platform, random.choice(USER_AGENT_ALL))
