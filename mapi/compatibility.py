# coding=utf-8

"""Manages compatibility for Python versions 2.7 and 3+."""

from abc import ABCMeta

try:  # pragma: no cover
    from collections.abc import MutableMapping
except ImportError:  # pragma: no cover
    from collections import MutableMapping

__all__ = ["MutableMapping", "AbstractClass", "ustr"]

AbstractClass = ABCMeta("ABC", (object,), {"__slots__": ()})
ustr = type(u"")  # unicode string type
