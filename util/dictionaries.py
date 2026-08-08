#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: dictionaries.py,v 2.1 2005/02/24 18:19:04 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# class KeyInsensitiveDict(dict):
#
#    Dictionary, that has case-insensitive keys.
#
#    Keys are retained in their original form when queried with .keys() or
#    .items().
#
#    Implementation: An internal dictionary maps lowercase keys to
#    (key,value) pairs. All key lookups are done against the lowercase keys,
#    but all methods that expose keys to the user retrieve the original keys.
#
#    def __init__(self):
#        Create an empty dictionary, or update from 'dict'.
#
#    def __getitem__(self, key):
#        Retrieve the value associated with 'key' (in any case).
#
#    def __setitem__(self, key, value):
#        Associate 'value' with 'key'. If 'key' already exists, but in
#        different case, it will be replaced.
#
#    def has_key(self, key):
#        Case insensitive test wether 'key' exists.
#
#    def __contains__(self, key):
#        Case insensitive test where key is in dict.
#
# ---------------------------------------------------------------------------

__all__ = ["KeyInsensitiveDict"]

import sys
import string

class KeyInsensitiveDict(dict):
    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, key):
        if (type(key) == type("")):
            key = key.lower()
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if (type(key) == type("")):
            key = key.lower()
        dict.__setitem__(self, key, value)

    def has_key(self, key):
        if (type(key) == type("")):
            key = key.lower()
        return dict.has_key(self, key)

    def __contains__(self, key):
        if (type(key) == type("")):
            key = key.lower()
        return dict.__contains__(self, key)

    def __delitem__(self, key):
        if (type(key) == type("")):
            key = key.lower()
        dict.__delitem__(self, key)