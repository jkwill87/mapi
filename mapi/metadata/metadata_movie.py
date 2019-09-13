# coding=utf-8

from mapi.metadata.metadata import Metadata

__all__ = ["MetadataMovie"]


class MetadataMovie(Metadata):
    """Movie Metadata class.
    """

    fields_accepted = Metadata.fields_accepted | {"id_imdb", "id_tmdb"}

    def __init__(self, **params):
        super(MetadataMovie, self).__init__(**params)
        self._dict["media"] = "movie"

    def __format__(self, format_spec):
        return super(MetadataMovie, self).__format__(
            format_spec or "{title} ({year})"
        )

    def __str__(self):
        return self.__format__(None)
