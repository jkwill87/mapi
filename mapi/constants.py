# coding=utf-8

""" Constants used by mapi
"""

MEDIA_MOVIE = 'movie'
MEDIA_TELEVISION = 'television'
MEDIA_ALL = {MEDIA_MOVIE, MEDIA_TELEVISION}

PROVIDER_IMDB = 'imdb'
PROVIDER_TMDB = 'tmdb'
PROVIDER_TVDB = 'tvdb'

API_TELEVISION = {PROVIDER_TVDB}
API_MOVIE = {PROVIDER_IMDB, PROVIDER_TMDB}
API_ALL = API_TELEVISION | API_MOVIE

META_AIRDATE = 'airdate'
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
META_YEAR = 'year'

PARAMS_MOVIE = {
    META_ID_IMDB,
    META_ID_TMDB,
    META_SYNOPSIS,
    META_TITLE,
    META_MEDIA,
    META_YEAR,
}

PARAMS_TELEVISION = {
    META_EPISODE,
    META_ID_IMDB,
    META_ID_TVDB,
    META_SEASON,
    META_SERIES,
    META_SYNOPSIS,
    META_TITLE,
    META_MEDIA,
}

PARAMS_ALL = PARAMS_MOVIE | PARAMS_TELEVISION

PLATFORM_CHROME = 'chrome'
PLATFORM_EDGE = 'edge'
PLATFORM_IOS = 'ios'
PLATFORM_ALL = {PLATFORM_CHROME, PLATFORM_EDGE, PLATFORM_IOS}

AGENT_CHROME = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/601.1'
    ' (KHTML, like Gecko) CriOS/53.0.2785.86 Mobile/14A403 Safari/601.1.46'
)
AGENT_EDGE = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like '
    'Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
)
AGENT_IOS = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) '
    'AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A403 '
    'Safari/602.1'
)
AGENT_ALL = (AGENT_CHROME, AGENT_EDGE, AGENT_IOS)

TVDB_LANGUAGE_CODES = [
    'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it',
    'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'ru', 'sl', 'sv', 'tr', 'zh'
]

API_KEY_ENV_TMDB = 'API_KEY_TMDB'
API_KEY_ENV_TVDB = 'API_KEY_TVDB'
