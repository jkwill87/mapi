import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from mapi.exceptions import MapiNetworkException


def request_json(url, parameters=None, body=None, headers=None):
    if not url: return 400, None

    # Format request
    if isinstance(parameters, dict):
        url += '?' + urlencode(clean_dict(parameters))

    if isinstance(headers, dict):
        headers = clean_dict(headers)

    if body:
        method = 'POST'
        if isinstance(body, str): body = body.encode()
        elif isinstance(body, dict): body = json.dumps(body).encode()
        headers = headers or {}
        headers['content-type'] = 'application/json'
        headers['content-length'] = len(body)
        headers['user-agent'] = 'Mozilla/5.0'
    else: method = 'GET'

    # Perform request
    try:
        request = Request(
            url=url,
            data=body,
            headers=headers or {},
            method=method
        )
        response = urlopen(request)
    except (ValueError, TypeError): return 400, None
    except HTTPError as e: return e.code, None
    except URLError: raise MapiNetworkException

    # Parse JSON
    if response.status is 200:
        try: content = json.loads(response.read())
        except ValueError: return 400, None
        return response.status, content

    return response.status, None


def clean_dict(x):
    assert isinstance(x, dict)
    return {
        str(k).strip(): str(v).strip()
        for k, v in x.items()
        if v not in (None, Ellipsis, [], (), '')
    }
