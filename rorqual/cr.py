#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
# $Id: cr.py,v 2.0 2005/01/21 17:33:50 kdm Exp $                              #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#                                                                             #
#                                                                             #
# --------------------------------------------------------------------------- #

from vdf.vdfparser import InitParser
from vdf.vdf import ParseEntry, VDFObject
from rorqual.constants import IDENT_REPORT, ERR_MISSING_AW_GROUP

__all__  = ["readCR", "CRException"]

class CRException(Exception):
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return "CRException: " + self.msg
        
def readCR(filename):
    print "reading " + filename + "."*3 ,
    if InitParser(filename) != 0:
        raise IOError("File not found");
    (key, type, value, line) = ParseEntry()
    if key != IDENT_REPORT:
        raise CRException(ERR_MISSING_AW_GROUP)
    cr = VDFObject(key, type, line)
    cr.init(value)
    print "done."
    return cr
