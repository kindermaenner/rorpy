#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
# $Id: types.py,v 2.1 2005/04/04 17:54:10 kdm Exp $                           #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#                                                                             #
#                                                                             #
# --------------------------------------------------------------------------- #

__all__ = ["TypeAmount", "TypeDirection", "TypeStatus", "TypeReligion", "TypeFlag"]

from rorparserutil import GetEntry
from rorscanner    import *
from references    import RefObject

class Type:
    def __init__(self):
        pass

    def __str__(self):
        return ""

    def parse(self):
        pass

class TypeAmount(Type):
    ALLES = -2
    ALLE  = -1

    def __init__(self):
        Type.__init__(self)
        self.value = -1

    def hasDefinedValue(self):
        return not self.value < 0

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_NUMBER):
            self.value = int(value)
            return True
        elif (type == TOK_KEYWORD):
            if (value == "alle"):
                self.value = -1
                return True
            elif (value == "alles"):
                self.value = -2
                return True
        return False

class TypeDirection(Type):
    def __init__(self, val = None, obj = None, through = False, wait = False):
        Type.__init__(self)
        self.value   = val
        self.object  = obj
        self.through = through
        self.wait    = wait

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_DIRECTION):
            if (value == "Norden"):
                self.value = DIR_NORTH
            elif (value == "Nordwesten"):
                self.value = DIR_NORTHWEST
            elif (value == "Suedwesten"):
                self.value = DIR_SOUTHWEST
            elif (value == "Sueden"):
                self.value = DIR_SOUTH
            elif (value == "Suedosten"):
                self.value = DIR_SOUTHEAST
            elif (value == "Nordosten"):
                self.value = DIR_NORTHEAST
            elif (value == "hindurch"):
                self.through = True
            elif (value == "pause"):
                self.wait = True
            else:
                self.value = value
            return True
        if (type == TOK_NUMBER):
            self.object = RefObject()
            self.object.id = value
            return True
        return False

class TypeStatus(Type):
    def __init__(self, val = None):
        Type.__init__(self)
        self.value = val
        self.keywords = ["alliiert", "freundlich", "neutral", "unfreundlich", "feindlich"]

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_KEYWORD):
            if value in self.keywords:
                self.value = value
                return True
        return False

class TypeReligion(Type):
    def __init__(self, val = None):
        Type.__init__(self)
        self.value = val

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_IDENT):
            if ((value == "licht") or (value == "wechselhaft") or (value == "finster")):
                self.value = value
                return True
        return False

class TypeFlag(Type):
    def __init__(self, value = False):
        Type.__init__(self)
        self.value = value

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_NUMBER):
            if (value == "0"):
                return True
            if (value == "1"):
                self.value = True
                return True
        return False

