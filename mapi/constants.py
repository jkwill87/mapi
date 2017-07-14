# coding=utf-8
from datetime import date as _date

ABOUT_AUTHOR = 'Jessy Williams'
ABOUT_COPYRIGHT = 'Copyright %d %s' % (_date.today().year, ABOUT_AUTHOR)
ABOUT_DESCRIPTION = 'An API for media database APIs which allows you to search for metadata using simple, common interface'
ABOUT_EMAIL = 'jessy@jessywilliams.com'
ABOUT_LICENSE = 'MIT'
ABOUT_TITLE = 'mapi'
ABOUT_URL = 'https://github.com/jkwill87/' + ABOUT_TITLE
ABOUT_VERSION = '0.1'

MEDIA_MOVIE = 'movie'
MEDIA_TELEVISION = 'television'
MEDIA_ALL = {MEDIA_MOVIE, MEDIA_TELEVISION}

PROVIDER_IMDB = 'imdb'
PROVIDER_TMDB = 'tmdb'
PROVIDER_TVDB = 'tvdb'

API_TELEVISION = {PROVIDER_TVDB}
API_MOVIE = {PROVIDER_IMDB, PROVIDER_TMDB}
API_ALL = API_TELEVISION | API_MOVIE

META_EPISODE = 'episode'
META_ID_IMDB = 'id_imdb'
META_ID_TMDB = 'id_tmdb'
META_ID_TVDB = 'id_tvdb'
META_MEDIA = 'media'
META_OVERVIEW = 'overview'
META_SEASON = 'season'
META_SERIES = 'series'
META_SYNOPSIS = 'synopsis'
META_TITLE = 'title'
META_TYPE = 'type'
META_YEAR = 'year'

PARAMS_MOVIE = {
    META_ID_IMDB,
    META_ID_TMDB,
    META_SYNOPSIS,
    META_TITLE,
    META_TYPE,
    META_YEAR,
}

PARAMS_TELEVISION = {
    META_EPISODE,
    META_ID_TVDB,
    META_SEASON,
    META_SERIES,
    META_SYNOPSIS,
    META_TITLE,
    META_TYPE,
}

PARAMS_ALL = PARAMS_MOVIE | PARAMS_TELEVISION

PLATFORM_CHROME = 'chrome'
PLATFORM_EDGE = 'edge'
PLATFORM_IOS = 'ios'
PLATFORM_ALL = {PLATFORM_CHROME, PLATFORM_EDGE, PLATFORM_IOS}

USER_AGENT_CHROME = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.86 Mobile/14A403 Safari/601.1.46'
USER_AGENT_EDGE = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
USER_AGENT_IOS = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A403 Safari/602.1'
USER_AGENT_ALL = (USER_AGENT_CHROME, USER_AGENT_EDGE, USER_AGENT_IOS)

ENV_TMDB_API_KEY = 'TMDB_API_KEY'
