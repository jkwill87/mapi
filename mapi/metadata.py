# coding=utf-8

""" Metadata data classes
"""

from datetime import datetime as dt

from mapi import ustr

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

DEFAULT_FIELDS = {"date", "media", "synopsis", "title"}

EXTRA_FIELDS = {"extension", "group", "quality"}

NUMERIC_FIELDS = {"season", "episode"}


class Metadata(MutableMapping):
    """ Base Metadata class
    """

    fields = DEFAULT_FIELDS | EXTRA_FIELDS

    def __init__(self, **params):
        self._dict = {k: None for k in DEFAULT_FIELDS}
        self.update(params)

    def __delitem__(self, key):
        raise NotImplementedError("values can be modified but keys are static")

    def __getitem__(self, key):
        # Case insensitive keys
        key = key.lower()

        # Special case for year
        if key == "year":
            date = self._dict.__getitem__("date")
            return date[:4] if date else None
        else:
            return self._dict.__getitem__(key)

    def __iter__(self):
        return {k: v for k, v in self._dict.items() if v}.__iter__()

    def __hash__(self):
        return frozenset(self._dict.items()).__hash__()

    def __len__(self):
        return {k: v for k, v in self._dict.items() if v}.__len__()

    def __repr__(self):
        return {k: v for k, v in self._dict.items() if v}.__repr__()

    def __setitem__(self, key, value):

        # Validate key
        if key not in self.fields:
            raise KeyError(
                "'%s' cannot be set for %s" % (key, self.__class__.__name__)
            )

        elif key == "extension":
            value = value if not value or value.startswith(".") else "." + value

        elif key == "media" and self["media"] and self["media"] != value:
            raise ValueError("media cannot be changed")

        elif key == "date" and value is not None:
            dt.strptime(value, "%Y-%m-%d")  # just checks date format is valid

        # Multi-episode hack; treat as if simply the first episode in list
        elif key == "episode" and isinstance(value, (list, tuple)):
            value = sorted(value)[0]

        # Store all values as strings unless known numeric field
        elif value and key not in NUMERIC_FIELDS:
            value = ustr(value)

        # Store falsy fields (e.g. None, False, etc.) as None
        if not value:
            value = None

        # Looks good if its gotten this far, store it!
        self._dict[key] = value


class MetadataTelevision(Metadata):
    """ Television Metadata class
    """

    fields = Metadata.fields | {
        "episode",
        "id_imdb",
        "id_tvdb",
        "season",
        "series",
    }

    def __init__(self, **params):
        super(MetadataTelevision, self).__init__(**params)
        self._dict["media"] = "television"


class MetadataMovie(Metadata):
    """ Movie Metadata class
    """

    fields = Metadata.fields | {"id_imdb", "id_tmdb"}

    def __init__(self, **params):
        super(MetadataMovie, self).__init__(**params)
        self._dict["media"] = "movie"
