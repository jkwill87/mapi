# coding=utf-8

import re

from mapi import log
from mapi.compatibility import ustr
from mapi.endpoints.tvdb import *
from mapi.metadata import MetadataTelevision
from mapi.providers import Provider

__all__ = ["TVDb"]


class TVDb(Provider):
    """ Queries the TVDb API
    """

    def __init__(self, **options):
        super(TVDb, self).__init__(**options)
        if not self.api_key:
            raise MapiProviderException("TVDb requires an API key")
        self.token = "" if self.cache else self._login()

    def _login(self):
        return tvdb_login(self.api_key)

    def search(self, id_key=None, **parameters):
        """ Searches TVDb for movie metadata

        TODO: Consider making parameters for episode ids
        """
        episode = parameters.get("episode")
        id_tvdb = parameters.get("id_tvdb") or id_key
        id_imdb = parameters.get("id_imdb")
        season = parameters.get("season")
        series = parameters.get("series")
        date = parameters.get("date")
        date_fmt = r"(19|20)\d{2}(-(?:0[1-9]|1[012])(-(?:[012][1-9]|3[01]))?)?"

        try:
            if id_tvdb:
                for result in self._search_id_tvdb(id_tvdb, season, episode):
                    yield result
            elif id_imdb:
                for result in self._search_id_imdb(id_imdb, season, episode):
                    yield result
            elif series and date:
                if not re.match(date_fmt, date):
                    raise MapiProviderException(
                        "Date format must be YYYY-MM-DD"
                    )
                for result in self._search_series_date(series, date):
                    yield result
            elif series:
                for result in self._search_series(series, season, episode):
                    yield result
            else:
                raise MapiNotFoundException
        except MapiProviderException as e:
            if not self.token:
                log.info(
                    "Result not cached; logging in and reattempting search"
                )
                self.token = self._login()
                for result in self.search(id_key, **parameters):
                    yield result
            else:
                raise e

    def _search_id_imdb(self, id_imdb, season=None, episode=None):
        series_data = tvdb_search_series(
            self.token, id_imdb=id_imdb, cache=self.cache
        )
        id_tvdb = series_data["data"][0]["id"]
        return self._search_id_tvdb(id_tvdb, season, episode)

    def _search_id_tvdb(self, id_tvdb, season=None, episode=None):
        assert id_tvdb
        found = False
        series_data = tvdb_series_id(self.token, id_tvdb, cache=self.cache)
        page = 1
        page_max = 5
        while True:
            episode_data = tvdb_series_id_episodes_query(
                self.token, id_tvdb, episode, season, cache=self.cache
            )
            for entry in episode_data["data"]:
                try:
                    yield MetadataTelevision(
                        series=series_data["data"]["seriesName"],
                        season=ustr(entry["airedSeason"]),
                        episode=ustr(entry["airedEpisodeNumber"]),
                        date=entry["firstAired"],
                        title=entry["episodeName"].split(";", 1)[0],
                        synopsis=(entry["overview"] or "")
                        .replace("\r\n", "")
                        .replace("  ", "")
                        .strip(),
                        media="television",
                        id_tvdb=ustr(id_tvdb),
                    )
                    found = True
                except (AttributeError, ValueError):
                    continue
            if page == episode_data["links"]["last"]:
                break
            elif page >= page_max:
                break
            page += 1
        if not found:
            raise MapiNotFoundException

    def _search_series(self, series, season, episode):
        assert series
        found = False
        series_data = tvdb_search_series(self.token, series, cache=self.cache)

        for series_id in [entry["id"] for entry in series_data["data"][:5]]:
            try:
                for data in self._search_id_tvdb(series_id, season, episode):
                    found = True
                    yield data
            except MapiNotFoundException:
                continue  # may not have requested episode or may be banned
        if not found:
            raise MapiNotFoundException

    def _search_series_date(self, series, date):
        assert series and date
        found = False
        series_data = tvdb_search_series(self.token, series, cache=self.cache)
        series_entries = {
            entry["id"]: entry["seriesName"]
            for entry in series_data["data"][:5]
        }
        page = 1
        page_max = 100
        for id_tvdb, series_name in series_entries.items():
            while True:
                try:
                    response = tvdb_series_id_episodes(
                        self.token, id_tvdb, page, cache=self.cache
                    )
                except MapiNotFoundException:
                    break
                for entry in response["data"]:
                    if not entry["firstAired"].startswith(date):
                        continue
                    try:
                        yield MetadataTelevision(
                            series=series_name,
                            season=ustr(entry["airedSeason"]),
                            episode=ustr(entry["airedEpisodeNumber"]),
                            date=entry["firstAired"],
                            title=entry["episodeName"].split(";", 1)[0],
                            synopsis=ustr(entry["overview"])
                            .replace("\r\n", "")
                            .replace("  ", "")
                            .strip(),
                            media="television",
                            id_tvdb=ustr(entry["airedSeasonID"]),
                        )
                        found = True
                    except (AttributeError, ValueError):
                        continue
                if page == response["links"]["last"]:
                    break
                elif page >= page_max:
                    break
                elif found and len(date) == 10:
                    break
                page += 1
        if not found:
            raise MapiNotFoundException
