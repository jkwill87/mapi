# coding=utf-8

from mapi.metadata._metadata_base import MetadataBase

__all__ = ["MetadataMovie"]


class MetadataMovie(MetadataBase):
    """Movie Metadata class.
    """

    fields_accepted = MetadataBase.fields_accepted | {"id_imdb", "id_tmdb"}

    def __init__(self, **params):
        super(MetadataMovie, self).__init__(**params)
        self._dict["media"] = "movie"

    def __format__(self, format_spec):
        return super(MetadataMovie, self).__format__(
            format_spec or "{title} ({year})"
        )

    def __str__(self):
        return self.__format__(None)
