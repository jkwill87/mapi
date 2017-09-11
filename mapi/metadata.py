from abc import ABCMeta
from collections import MutableMapping
from datetime import datetime as dt
from re import sub

# Compatibility for Python 2.7/3+
_AbstractClass = ABCMeta('ABC', (object,), {'__slots__': ()})


class Metadata(_AbstractClass, MutableMapping):
    template = ''
    fields = {}

    def __delitem__(self, key):
        raise NotImplementedError('values can be modified but keys are static')

    def __getitem__(self, key):
        # Case insensitive keys
        key = key.lower()

        # Special case for year
        if key == 'year':
            date = self._dict.__getitem__('date')
            return date[:4] if date else None
        else:
            return self._dict.__getitem__(key)

    def __init__(self, **params):
        self._dict = {k: None for k in self.fields}
        self.update(params)
        if 'template' in params:
            self.template = params['template']

    def __iter__(self):
        return self._dict.__iter__()

    def __len__(self):
        return self._dict.__len__()

    def __repr__(self):
        return repr(dict(self))

    def __setitem__(self, key, value):

        # Validate key
        if key not in self.fields:
            raise KeyError(
                '%s is not a valid %s field'
                % (key, self.__class__.__name__)
            )

        # Validate value
        elif key == 'mtype' and value not in ['movie', 'television']:
            raise ValueError()
        elif key == 'date':
            dt.strptime(value, '%Y-%m-%d')

        # If its gotten this far, looks good
        self._dict[key] = value

    def __str__(self):
        return self.format()

    @staticmethod
    def _str_fix_whitespace(s):
        # Concatenate dashes
        s = sub(r'-\s*-', '-', s)
        # Strip leading/ trailing dashes
        s = sub(r'-\s*$|^\s*-', '', s)
        # Concatenate whitespace
        s = sub(r'\s+', ' ', s)
        # Strip leading/ trailing whitespace
        s = s.strip()
        return s

    def _str_replace(self, mobj):
        try:
            prefix, key, suffix = mobj.groups()
            value = self[key]
            # log.debug(
            #     "sub for '%s' - key='%s',value='%s',prefix='%s',suffix='%s'"
            #     % (mobj.group(), key, value, prefix, suffix)
            # )
            assert value
            return '%s%s%s' % (prefix, value, suffix)
        except (IndexError, KeyError, AssertionError):
            # log.warning("couldn't sub for %s" % mobj.group())
            return ''

    def format(self, template=None):
        """ Substitutes variables within template with that of fields'

        :param template: Each substitution is indicated by an alphanumeric word
            prefixed by a sigil ($) symbol within angled brackets. If the
            matching field is found then substitution takes place, else it is
            omitted. If it is omitted, then all whitespace and non alphanumerics
            (i.e. spaces, dashes, underscores and the like) within the square
            brackets will be omitted as well.
        :rtype: str
        """
        s = sub(
            r'(?:<([^<]*?)\$(\w+)([^>]*?)>)',
            self._str_replace,
            template or self.template
        )
        s = self._str_fix_whitespace(s)
        return s


# noinspection PyAbstractClass
class MetadataTelevision(Metadata):
    template = '<$series - >< - $season><x$episode - >< - $title>'
    fields = {
        'id_imdb',
        'id_tvdb',
        'media',
        'series',
        'season',
        'episode',
        'title',
        'date',
        'synopsis',
    }

    @staticmethod
    def _str_pad_episode(s):
        s = sub(r'(?<=\s)(\d)(?=x\d)', r'0\1', s)
        s = sub(r'(?<=\dx)(\d)(?=\s)', r'0\1', s)
        s = sub(r'([S|E])(\d)(?=\s|$|E)', r'\g<1>0\g<2>', s)
        return s

    def format(self, template=None):
        s = super(MetadataTelevision, self).format(template)
        return self._str_pad_episode(s)


# noinspection PyAbstractClass
class MetadataMovie(Metadata):
    template = '<$title ><($year)>'
    fields = {
        'id_imdb',
        'id_tmdb',
        'media',
        'title',
        'date',
        'synopsis',
    }
