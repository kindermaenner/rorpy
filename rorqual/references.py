#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
# $Id: references.py,v 2.5 2005/05/12 21:59:09 kdm Exp $                      #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#                                                                             #
#                                                                             #
# --------------------------------------------------------------------------- #

__all__ = ["RefObject", "RefProduct", "RefParty", "RefTalent", "RefUnit"]

from constants     import *
from rorparserutil import GetEntry
from rorscanner    import *
from util.messages import Message
from rorqual.kb    import GetKB
from rorqual.objects import *

class ResolveError(AttributeError):
    "Interner Fehler beim resolven von References"
    def __init__(self):
        super(ResolveError, self).__init__()

    def __str__(self):
        return "ResolveError: " + self.value

class Reference(object):
    def __init__(self):
        self.obj = None
        self.resolved = False

    def setTarget(self, o):
        if (o is None):
            raise Exception("Resolved Object is None")
        self.obj = o
        self.resolved = True

    def getTargetClassName(self):
        if not self.resolved:
            return ""
        else:
            return self.obj.__class__.__name__

    def __str__(self):
        if self.resolved:
            return str(self.obj)
        else:
            return self.GetUnresolvedAsString()

    def GetUnresolvedAsString(self):
        return ""

    def parse(self):
        return False

    def resolve(self, unit = None):
        return 0

class RefObject(Reference):
    def __init__(self, id = None, name = None):
        Reference.__init__(self)
        self.id   = id
        self.name = name

    def GetUnresolvedAsString(self):
        if self.name is None:
            return "ObjectRef: " + str(self.id)
        else:
            return "ObjectRef: " + self.name

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_NUMBER):
            self.id = value
            return True
        if (type == TOK_IDENT):
            self.name = value.replace("_", " ")
            return True
        if (type == TOK_STRING):
            self.name = value[1:-1].replace("_", " ")
            return True
        return False

    def resolve(self, unit = None):
        if self.resolved:
            return 0
        if not self.name is None:
            kb = GetKB()
            spec = kb.findBuilding(self.name)
            if not spec is None:
                object = RorBuilding()
                object.kbobj = spec
                object.initValuesFromKB()
                self.setTarget(object)
                return 0
            else:
                return (12, (self.name))
        elif not self.id is None:
            if unit is None:
                raise ResolveError
            if not unit.region is None:
                try:
                    o = unit.region.sortedObjects[int(self.id)]
                    self.setTarget(o)
                    return 0
                except IndexError:
                    return (13, (int(self.id)))
            else:
                return (14, (unit.getKey()))
        else:
            raise ResolveError

class RefParty(Reference):
    def __init__(self, id = None):
        Reference.__init__(self)
        self.id = id

    def GetUnresolvedAsString(self):
        return "PartyRef: " + str(self.id)

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_NUMBER):
            self.id = value
            return True
        return False

    def resolve(self, unit = None):
        if self.resolved:
            return 0
        self.setTarget(self.id)
        return 0

class RefProduct(Reference):
    def __init__(self, name = None):
        Reference.__init__(self)
        self.name = name

    def GetUnresolvedAsString(self):
        return "ProductRef: " + self.name

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_IDENT):
            self.name = value.replace("_", " ")
            return True
        if (type == TOK_STRING):
            self.name = value[1:-1].replace("_", " ")
            return True
        return False

    def resolve(self, unit = None):
        if self.resolved:
            return 0
        kb = GetKB()
        spec = kb.findProduct(self.name)
        if spec is None:
            if (self.name == "bauern") or (self.name == "bauer"):
                return 0
        if not spec is None:
            product = RorProduct()
            product.id = spec.key
            product.kbobj = product.getKBObject()
            product.initValuesFromKB()
            self.setTarget(product)
            return 0
        else:
            return (15, (self.name))

class RefTalent(Reference):
    def __init__(self, name = None):
        Reference.__init__(self)
        self.name = name

    def GetUnresolvedAsString(self):
        return "TalentRef: " + self.name

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_IDENT):
            self.name = value.replace("_", " ")
            return True
        if (type == TOK_STRING):
            self.name = value[1:-1].replace("_", " ")
            return True
        return False

    def resolve(self, unit = None):
        if self.resolved:
            return 0
        kb = GetKB()
        spec = kb.findTalent(self.name)
        if not spec is None:
            talent = RorTalent()
            talent.id = spec.key
            talent.kbobj = talent.getKBObject()
            talent.initValuesFromKB()
            self.setTarget(talent)
            return 0
        else:
            return (16, (self.name))

class RefUnit(Reference):
    def __init__(self, id = None, new = False, party = None):
        Reference.__init__(self)
        self.id    = id
        self.new   = new
        self.party = party

    def GetUnresolvedAsString(self):
        if not self.new:
            return "UnitRef: " + str(self.id)
        else:
            if self.party is None:
                return "UnitRef: NEU " + str(self.id)
            else:
                return "UnitRef: PARTEI " + str(self.party) + " NEU " + str(self.id)

    def parse(self):
        (type, value) = GetEntry()
        if (type == TOK_NUMBER):
            self.id = value
            return True
        if (type == TOK_KEYWORD):
            if (value == "partei"):
                (type, value) = GetEntry()
                if (type == TOK_NUMBER):
                    self.party    = RefParty()
                    self.party.id = value
                    (type, value) = GetEntry()
                    if (type != TOK_KEYWORD):
                        return False
                else:
                    return False
            if (value == "neu"):
                (type, value) = GetEntry()
                if (type == TOK_NUMBER):
                    self.id = value
                    self.new = True
                    return True
        return False

    def resolve(self, unit = None):
        if self.resolved:
            return 0
        if unit is None:
            raise ResolveError
        r = unit.region
        if not self.new: # Fall 1: bestehende Einheit
            if (int(self.id) == 0):
                u = RorUnit()
                u.id = - int(self.id)
                u.name = "NEU " + str(self.id)
                u.partynumber = -1
                u.region = r
                u.region.getHinterland().addUnit(u)
                self.setTarget(u)
                return 0
            else:
                u = r.getUnit(int(self.id))
                if (u is None):
                    return (17, (int(self.id)))
                self.setTarget(u)
                return 0
        else:            # Fall 2: neue Einheit
            if self.party is None:
                # Eigene neue Einheit (existiert bereits)
                u = r.getUnitByName("NEU " + str(self.id))
                if (u is None):
                    return (17, int((self.id)))
                self.setTarget(u)
                return 0
            else:
                # Fremde neue Einheit (kann existiern, wird sonst angelegt)
                p = int(self.party.id)
                if p == unit.partynumber:
                    # Fehler: Eigene Partei
                    return (18, ())
                u = r.getUnit(- int(self.id))
                if u is None:
                    u = RorUnit()
                    u.id = - int(self.id)
                    u.name = "NEU " + str(self.id)
                    u.partynumber = int(self.party.id)
                    u.region = r
                    u.region.getHinterland().addUnit(u)
                self.setTarget(u)
                return 0

