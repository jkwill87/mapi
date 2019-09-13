# coding=utf-8

from mapi.metadata.metadata import Metadata

__all__ = ["MetadataTelevision"]


class MetadataTelevision(Metadata):
    """Television Metadata class.
    """

    fields_accepted = Metadata.fields_accepted | {
        "episode",
        "id_imdb",
        "id_tvdb",
        "season",
        "series",
    }

    def __init__(self, **params):
        super(MetadataTelevision, self).__init__(**params)
        self._dict["media"] = "television"

    def __format__(self, format_spec):
        return super(MetadataTelevision, self).__format__(
            format_spec or "{series} - {season:02}x{episode:02} - {title}"
        )

    def __str__(self):
        return self.__format__(None)
