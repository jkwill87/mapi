# coding=utf-8

from logging import getLogger

getLogger("mapi").disabled = True


JUNK_TEXT = "asdf#$@#g9765sdfg54hggaw"

MOVIE_META = [
    {
        "media": "movie",
        "year": "1985",
        "title": "The Goonies",
        "id_imdb": "tt0089218",
        "id_tmdb": "9340",
    },
    {
        "media": "movie",
        "year": "1939",
        "title": "The Wizard of Oz",
        "id_imdb": "tt0032138",
        "id_tmdb": "630",
    },
    {
        "media": "movie",
        "year": "1941",
        "title": "Citizen Kane",
        "id_imdb": "tt0033467",
        "id_tmdb": "15",
    },
    {
        "media": "movie",
        "year": "2017",
        "title": "Get Out",
        "id_imdb": "tt5052448",
        "id_tmdb": "419430",
    },
    {
        "media": "movie",
        "year": "2002",
        "title": u"Amélie",
        "id_imdb": "tt0211915",
        "id_tmdb": "194",
    },
]

TELEVISION_META = [
    {
        "media": "television",
        "series": "The Walking Dead",
        "season": "5",
        "episode": "11",
        "title": "The Distance",
        "id_imdb": "tt1520211",
        "id_tvdb": "153021",
    },
    {
        "media": "television",
        "series": "Adventure Time",
        "season": "7",
        "episode": "39",
        "title": "Reboot",
        "id_imdb": "tt1305826",
        "id_tvdb": "152831",
    },
    {
        "media": "television",
        "series": "Downtown",
        "season": "1",
        "episode": "13",
        "title": "Trip or Treat",
        "id_imdb": "tt0208616",
        "id_tvdb": "78342",
    },
    {
        "media": "television",
        "series": "Breaking Bad",
        "season": "3",
        "episode": "5",
        "title": "Más",
        "id_imdb": "tt0903747",
        "id_tvdb": "81189",
    },
    {
        "media": "television",
        "series": "The Care Bears",
        "season": "2",
        "episode": "2",
        "title": "Grumpy's Three Wishes",
        "id_imdb": "tt0284713",
        "id_tvdb": "76079",
    },
]


class MockRequestResponse:
    def __init__(self, status, content):
        self.status_code = status
        self.content = content

    def json(self):
        from json import loads

        return loads(self.content)
