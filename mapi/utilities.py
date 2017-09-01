# coding=utf-8

""" A collection of internal utility functions used by the package
"""

import random
from sys import version_info

import requests
import requests_cache
from appdirs import user_cache_dir

from mapi import log
from mapi.constants import *

# Setup requests caching
SESSION = requests_cache.CachedSession(
    cache_name=user_cache_dir() + '/mapi-py%d' % version_info.major,
    expire_after=604800,
)


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


def d2l(d):
    """ Convenience function that converts a dict into a sorted list of tuples

    :param dict d: dictionary
    :return: list of sorted tuples
    :rtype: list of tuple
    """
    return sorted([(k, v) for k, v in d.items()])


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
        return abs(int(x['year']) - year)

    # Remove duplicate entries
    unique_entries = list()
    [unique_entries.append(e) for e in entries if e not in unique_entries]
    entries = unique_entries

    # Remove entries outside of year delta for target year, if available
    if year and year_delta:
        year = int(year)
        year_delta = int(year_delta)
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

    :param optional str platform: the platform for the required user agent
    :return: the user agent string
    :rtype: str
    """
    if isinstance(platform, str):
        platform = platform.upper()
    return {
        PLATFORM_CHROME: AGENT_CHROME,
        PLATFORM_EDGE: AGENT_EDGE,
        PLATFORM_IOS: AGENT_IOS
    }.get(platform, random.choice(AGENT_ALL))


def request_json(url, parameters=None, body=None, headers=None, cache=True,
        agent=None):
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
    :param bool cache: Use requests_cache cached session; default True
    :return: a list where the first item is the numeric status code and the
        second is a dict containing the JSON data retrieved
    :rtype: list
    """
    assert url
    status = 400
    log.info("url: %s" % url)

    if isinstance(headers, dict):
        headers = clean_dict(headers)
    else:
        headers = dict()
    if isinstance(parameters, dict):
        parameters = d2l(clean_dict(parameters))
    if body:
        method = 'POST'
        headers['content-type'] = 'application/json'
        headers['user-agent'] = get_user_agent(agent)
        headers['content-length'] = str(len(body))
    else:
        method = 'GET'
        headers['user-agent'] = get_user_agent(agent)

    try:
        SESSION._is_cache_disabled = not cache  # yes, i'm a bad person
        response = SESSION.request(
            url=url,
            params=parameters,
            json=body,
            headers=headers,
            method=method,
        )
        status = response.status_code
        content = response.json() if status // 100 == 2 else None
        cache = getattr(response, 'from_cache', False)
    except (requests.RequestException, AttributeError, ValueError) as e:
        log.debug(e, exc_info=True)
        content = None

    log.info("method: %s" % method)
    log.info("headers: %r" % headers)
    log.info("parameters: %r" % parameters)
    log.info("cache: %r" % cache)
    log.info("status: %d" % status)
    log.debug("content: %s" % content)
    return status, content
