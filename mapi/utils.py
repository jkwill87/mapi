# coding=utf-8

"""A collection of utility functions non-specific to mapi's domain logic."""

import random
from os.path import join
from re import match
from sys import version_info

import requests_cache
from appdirs import user_cache_dir
from requests.adapters import HTTPAdapter

from mapi import log
from mapi.compatibility import ustr

__all__ = [
    "AGENT_ALL",
    "AGENT_CHROME",
    "AGENT_EDGE",
    "AGENT_IOS",
    "CACHE_PATH",
    "clean_dict",
    "clear_cache",
    "d2l",
    "get_session",
    "get_user_agent",
    "request_json",
    "year_expand",
]

AGENT_CHROME = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/601.1"
    " (KHTML, like Gecko) CriOS/53.0.2785.86 Mobile/14A403 Safari/601.1.46"
)
AGENT_EDGE = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like "
    "Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
)
AGENT_IOS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) "
    "AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A403 "
    "Safari/602.1"
)
AGENT_ALL = (AGENT_CHROME, AGENT_EDGE, AGENT_IOS)
CACHE_PATH = join(user_cache_dir(), "mapi-py%d.sqlite" % version_info.major)


def clean_dict(target_dict, whitelist=None):
    """Convenience function that removes a dicts keys that have falsy values."""
    assert isinstance(target_dict, dict)
    return {
        ustr(k).strip(): ustr(v).strip()
        for k, v in target_dict.items()
        if v not in (None, Ellipsis, [], (), "")
        and (not whitelist or k in whitelist)
    }


def clear_cache():
    """Clears requests-cache cache."""
    get_session().cache.clear()


def d2l(d):
    """Convenience function that converts a dict into a sorted tuples list."""
    return sorted([(k, v) for k, v in d.items()])


def get_session():
    """Convenience function that returns request-cache session singleton."""
    if not hasattr(get_session, "session"):
        get_session.session = requests_cache.CachedSession(
            cache_name=CACHE_PATH.rstrip(".sqlite"),
            expire_after=518400,  # 6 days
        )
        adapter = HTTPAdapter(max_retries=3)
        get_session.session.mount("http://", adapter)
        get_session.session.mount("https://", adapter)
    return get_session.session


def get_user_agent(platform=None):
    """Convenience function that looks up a user agent string, random if N/A."""
    if isinstance(platform, ustr):
        platform = platform.upper()
    return {"chrome": AGENT_CHROME, "edge": AGENT_EDGE, "ios": AGENT_IOS}.get(
        platform, random.choice(AGENT_ALL)
    )


def request_json(
    url, parameters=None, body=None, headers=None, cache=True, agent=None
):
    """
    Queries a url for json data.

    Note: Requests are cached using requests_cached for a week, this is done
    transparently by using the package's monkey patching.
    """
    assert url
    session = get_session()

    log.info("-" * 80)
    log.info("url: %s", url)

    if isinstance(headers, dict):
        headers = clean_dict(headers)
    else:
        headers = dict()
    if isinstance(parameters, dict):
        parameters = d2l(clean_dict(parameters))
    if body:
        method = "POST"
        headers["content-type"] = "application/json"
        headers["user-agent"] = get_user_agent(agent)
        headers["content-length"] = ustr(len(body))
    else:
        method = "GET"
        headers["user-agent"] = get_user_agent(agent)

    initial_cache_state = session._is_cache_disabled  # yes, i'm a bad person
    try:
        session._is_cache_disabled = not cache
        response = session.request(
            url=url,
            params=parameters,
            json=body,
            headers=headers,
            method=method,
            timeout=1,
        )
        status = response.status_code
        content = response.json() if status // 100 == 2 else None
        cache = getattr(response, "from_cache", False)
    except Exception as e:
        content = None
        status = 500
        log.debug(e, exc_info=True)
    else:
        log.debug("method: %s", method)
        log.debug("headers: %r", headers)
        log.debug("parameters: %r", parameters)
        log.debug("cache: %r", cache)
        log.info("status: %d", status)
        log.debug("content: %s", content)
    finally:
        session._is_cache_disabled = initial_cache_state
    return status, content


def year_expand(s):
    """Parses a year or dash-delimited year range."""
    regex = r"^((?:19|20)\d{2})?(\s*-\s*)?((?:19|20)\d{2})?$"
    try:
        start, dash, end = match(regex, ustr(s)).groups()
        start = start or 1900
        end = end or 2099
    except AttributeError:
        return 1900, 2099
    return (int(start), int(end)) if dash else (int(start), int(start))
