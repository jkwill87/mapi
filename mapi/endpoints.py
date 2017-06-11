# coding=utf-8

from re import match
from time import sleep

from mapi.constants import PLATFORM_IOS
from mapi.exceptions import *
from mapi.utilities import request_json


# noinspection PyUnboundLocalVariable
def imdb_main_details(id_imdb):
    """
    Lookup a media item using the Internet Movie Database's internal API

    :param str id_imdb: Internet Movie Database's primary key; prefixed w/ 'tt'
    :return: dict
    """
    if not match(r'tt\d+', id_imdb):
        raise MapiNotFoundException
    url = 'http://app.imdb.com/title/maindetails'
    parameters = {'tconst': id_imdb}
    for i in range(50):  # retry when service unavailable
        status, content = request_json(url, parameters, agent=PLATFORM_IOS)
        if status == 503:
            sleep((i + 1) * .025)  # .025 to 1.25 secs, total ~32
        else:
            break
    if status == 400:
        raise MapiError
    elif status == 404:
        raise MapiNotFoundException
    elif status != 200:
        raise MapiError
    elif not content:
        raise MapiNotFoundException
    else:
        return content


def imdb_mobile_find(title, nr=True, tt=True):
    """
    Search the Internet Movie Database using its undocumented iOS API

    :param str title: Movie title used for searching
    :param bool nr: ???
    :param bool tt: ???
    :return: status, data
    """
    url = 'http://www.imdb.com/xml/find'
    parameters = {'json': True, 'nr': nr, 'tt': tt, 'q': title}
    for i in range(50):  # retry when service unavailable
        status, content = request_json(url, parameters)
        if status == 503:
            sleep((i + 1) * .025)  # wait from .025 to 1.25 secs
        else:
            break
    # noinspection PyUnboundLocalVariable
    if status == 400 or not content:
        raise MapiNotFoundException
    elif status != 200:
        raise MapiError
    return content
