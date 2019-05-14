# coding=utf-8

""" Metadata data classes
"""

from datetime import datetime as dt
from re import sub
from string import Formatter, capwords

from mapi import ustr

try:  # pragma: no cover
    from collections.abc import MutableMapping
except ImportError:  # pragma: no cover
    from collections import MutableMapping

DEFAULT_FIELDS = {"date", "media", "synopsis", "title"}

EXTRA_FIELDS = {"extension", "group", "quality"}

NUMERIC_FIELDS = {"season", "episode"}


class _MetaFormatter(Formatter):
    def format_field(self, value, format_spec):
        # prevent None values from being stored as 'None' and ValueError from
        # being raised when value specifier is given w/o a corresponding value
        return format(value, format_spec) if value else ""


class Metadata(MutableMapping):
    """ Base Metadata class
    """

    fields = DEFAULT_FIELDS | EXTRA_FIELDS
    _formatter = _MetaFormatter()
    _fallback_str = "[unset metadata]"

    def __init__(self, **params):
        self._dict = {k: None for k in DEFAULT_FIELDS}
        self.update(params)

    def __delitem__(self, key):
        self[key] = None

    def __format__(self, format_spec="{title}"):
        re_pattern = r"({(\w+)(?:\:\d{1,2})?})"
        s = sub(re_pattern, self._format_repl, format_spec)
        s = self._str_fix_whitespace(s)
        return s

    def __iter__(self):
        return {k: v for k, v in self._dict.items() if v}.__iter__()

    def __getitem__(self, key):
        # Case insensitive keys
        key = key.lower()

        # Special case for year
        if key == "year":
            date = self._dict.__getitem__("date")
            return date[:4] if date else None
        else:
            return self._dict.__getitem__(key)

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

        # Store falsy fields (e.g. None, False, etc.) as None
        if not value and value != 0:
            value = None

        # Store numeric values as ints
        elif key in NUMERIC_FIELDS:
            value = int(value)

        # Store all other values as strings
        else:
            value = ustr(value)

        # Looks good if its gotten this far, store it!
        self._dict[key] = value

    def __str__(self):
        return self.get("title") or self._fallback_str

    def _format_repl(self, mobj):
        format_string, key = mobj.groups()
        value = self._formatter.vformat(format_string, None, self)
        if key not in EXTRA_FIELDS:
            value = self._str_title_case(value)
        return value

    @staticmethod
    def _str_fix_whitespace(s):
        # Concatenate dashes
        s = sub(r"-\s*-", "-", s)
        # Remove empty brackets
        s = s.replace("()", "")
        s = s.replace("[]", "")
        # Strip leading/ trailing dashes
        s = sub(r"-\s*$|^\s*-", "", s)
        # Concatenate whitespace
        s = sub(r"\s+", " ", s)
        # Strip leading/ trailing whitespace
        s = s.strip()
        return s

    @staticmethod
    def _str_title_case(s):
        lowercase_exceptions = {
            "a",
            "an",
            "and",
            "as",
            "at",
            "but",
            "by",
            "ces",
            "de",
            "des",
            "du",
            "for",
            "from",
            "in",
            "la",
            "le",
            "nor",
            "of",
            "on",
            "or",
            "the",
            "to",
            "un",
            "une",
            "with",
            "via",
            "h264",
            "h265",
        }
        uppercase_exceptions = {
            "i",
            "ii",
            "iii",
            "iv",
            "v",
            "vi",
            "vii",
            "viii",
            "ix",
            "x",
            "2d",
            "3d",
            "au",
            "aka",
            "atm",
            "bbc",
            "bff",
            "cia",
            "csi",
            "dc",
            "doa",
            "espn",
            "fbi",
            "ira",
            "jfk",
            "la",
            "lol",
            "mlb",
            "mlk",
            "mtv",
            "nba",
            "nfl",
            "nhl",
            "nsfw",
            "nyc",
            "omg",
            "pga",
            "rsvp",
            "tnt",
            "tv",
            "ufc",
            "ufo",
            "uk",
            "usa",
            "vip",
            "wtf",
            "wwe",
            "wwi",
            "wwii",
            "xxx",
            "yolo",
        }
        padding_chars = "[\"!$'(),-./:;<>@[]_`{} ]"
        string_lower = s.lower()
        string_length = len(s)
        s = capwords(s)

        # process lowercase transformations
        for exception in lowercase_exceptions:
            pos = string_lower.find(exception)
            if pos == -1:
                continue
            starts = pos == 0
            if starts:
                continue
            prev_char = string_lower[pos - 1]
            left_partitioned = prev_char in padding_chars
            word_length = len(exception)
            ends = pos + word_length == string_length
            next_char = None if ends else string_lower[pos + word_length]
            right_partitioned = ends or next_char in padding_chars
            if left_partitioned and right_partitioned:
                s = s[:pos] + exception.lower() + s[pos + word_length :]

        # process uppercase transformations
        for exception in uppercase_exceptions:
            pos = string_lower.find(exception)
            if pos == -1:
                continue
            starts = pos == 0
            prev_char = None if starts else string_lower[pos - 1]
            left_partitioned = starts or prev_char in padding_chars
            word_length = len(exception)
            ends = pos + word_length == string_length
            next_char = None if ends else string_lower[pos + word_length]
            right_partitioned = ends or next_char in padding_chars
            if left_partitioned and right_partitioned:
                s = s[:pos] + exception.upper() + s[pos + word_length :]
        return s


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

    def __str__(self):
        return self.__format__("{series} - {season:02}x{episode:02} - {title}")


class MetadataMovie(Metadata):
    """ Movie Metadata class
    """

    fields = Metadata.fields | {"id_imdb", "id_tmdb"}

    def __init__(self, **params):
        super(MetadataMovie, self).__init__(**params)
        self._dict["media"] = "movie"

    def __str__(self):
        return self.__format__("{title} ({year})")
