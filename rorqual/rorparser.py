#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: rorparser.py,v 2.6 2005/03/09 07:39:33 kdm Exp $
#
# ---------------------------------------------------------------------------
#
#   def readTurn(aw, fromAW = False):
#        aw     - das RorAW-Objekt
#        fromAW - True, wenn die Zugvorlage aus der Auswertung eingelesen
#                 wird.
#        Liest den Rorqual Zug ein. Die Funktion kennt drei Zustaende:
#        z = 0: Lesen aller Zeilen vor dem ersten Vorkommen von #
#        z = 1: Lesen der Befehle
#        z = 2: Lesen aller Zeilen nach dem zweiten Vorkommen von #
#
#   def readCommands(new = False, object = None, region = None, fromAW = False):
#        new    - True, wenn es sich um eine neue Einheit handelt
#        object - Objekt, in dem die Einheit steht
#        region - Region, in der die Einheit steht
#        fromAW - True, wenn die Zugvorlage aus der Auswertung eingelesen
#                 wird.
#        Liest fuer eine Einheit die Befehle ein. Diese Funktion wird immer
#        aufgerufen, wenn das Schluesselwort EINHEIT gelesen wird und liest
#        alle Tokens bis zum naechsten Vorkommen des Schlussselworts EINHEIT.
#        Vor dem Verlassen der Funktion wird das letzte Token (Schluesselwort
#        EINHEIT) zurueckgeschrieben, da es nicht mehr zu der aktuellen
#        Einheit gehoert.
#
# ---------------------------------------------------------------------------

__all__ = ["readTurn"]

from rorscanner    import *
from rorparserutil import GetLine, EOFException, GetEntry, ReadNewline, NewlineException, ReadUntilNL, PushbackEntry
from objects       import RorUnit
from commands      import createCommand
from constants     import IDENT_UNIT_PARTY, IDENT_UNIT_NAME, IDENT_UNIT_KEY, IDENT_UNIT
from util.messages import Message, CAT_HINT, CAT_WARN, CAT_ERR

_aw        = None
_newUnits  = 0
_allUnits  = {}

def readTurn(aw, fromAW = False):
    "Liest den Rorqual Zug ein"
    global _aw
    global _newUnits
    global _allUnits
    _aw = aw
    _allUnits = _aw.getUnitsFromParty(_aw.partynumber)
    z   = 0
    try:
        while True:
            try:
                (type, value) = GetEntry()
                if (z == 0):
                    if (type is TOK_SPECIAL):
                        if (value == "#"):
                            z = 1
                            try:
                                (type, value) = GetEntry()
                                if (type == TOK_KEYWORD):
                                    if (value == "rorqual"):
                                        (type, value) = GetEntry()
                                        if (type == TOK_NUMBER):
                                            (type, value) = GetEntry()
                                            if (type == TOK_STRING):
                                                if ReadNewline():
                                                    continue
                                if not fromAW:
                                    _aw.output += [Message(CAT_ERR, 1, line = GetLine())]
                            except NewlineException:
                                if not fromAW:
                                    _aw.output += [Message(CAT_ERR, 1, line = GetLine())]
                                continue
                    elif ((type != TOK_COMMENT) and (type != TOK_NEWLINE)) and not fromAW:
                        _aw.output += [Message(CAT_ERR, 3, (value), GetLine())]
                        ReadUntilNL()
                elif (z == 1):
                    if (type is TOK_SPECIAL):
                        if (value == "#"):
                            z = 2
                            try:
                                (type, value) = GetEntry()
                                if (type == TOK_KEYWORD):
                                    if (value == "ende"):
                                        if ReadNewline():
                                            continue
                                if not fromAW:
                                    _aw.output += [Message(CAT_ERR, 2, line = GetLine())]
                            except NewlineException:
                                if not fromAW:
                                    _aw.output += [Message(CAT_ERR, 2, line = GetLine())]
                                continue
                    elif (type == TOK_KEYWORD):
                        if (value == "einheit"):
                            readCommands(fromAW = fromAW)
                            continue
                        if not fromAW:
                            _aw.output += [Message(CAT_ERR, 5, (value), GetLine())]
                    ReadUntilNL()
                elif (z == 2):
                    if ((type != TOK_COMMENT) and (type != TOK_NEWLINE)) and not fromAW:
                        _aw.output += [Message(CAT_ERR, 4, (value), GetLine())]
                        ReadUntilNL()
                (type, value) = GetEntry()
            except NewlineException:
                continue
    except EOFException:
        return _aw

def readCommands(new = False, object = None, region = None, fromAW = False):
    global _newUnits
    global _aw
    global _allUnits
    durableCommand = False
    try:
        (type, value) = GetEntry()
        if (type != TOK_NUMBER) and not fromAW:
            _aw.output += [Message(CAT_ERR, 7, ("EINHEIT"), GetLine())]
            ReadUntilNL()
            return
        else:
            if not _allUnits.has_key(int(value)):
                if not new:
                    if not fromAW:
                        _aw.output += [Message(CAT_ERR, 6, (int(value)), GetLine())]
                    unit = RorUnit()
                    unit.id = int(value)
                    unit.object = object
                    unit.region = region
                    unit.partynumber = _aw.partynumber
                    unit.partyname = _aw.partyname
                    unit.name = "unbekannte Einheit"
                    # TODO: Dummy-Region einfuegen
                else:
                    _newUnits -= 1
                    unit = RorUnit()
                    unit.id = _newUnits
                    unit.object = object
                    unit.region = region
                    unit.partynumber = _aw.partynumber
                    unit.partyname = _aw.partyname
                    unit.name = "NEU " + str(value)
                    object.addUnit(unit)
            else:
                unit = _allUnits[int(value)]
    except NewlineException:
        if not fromAW:
            _aw.output += [Message(CAT_ERR, 8, ("EINHEIT"), GetLine())]
            return
    while True:
        try:
            (type, value) = GetEntry()
            if (type == TOK_KEYWORD):
                if (value == "einheit"):
                    if (new == True) and not fromAW:
                        _aw.output += [Message(CAT_ERR, 9, ("NEU", "ENDE"), GetLine())]
                    PushbackEntry((type, value))
                    return
                if (value == "neu"):
                    readCommands(True, unit.object, unit.region, fromAW)
                elif (value == "ende"):
                    if (new == False) and not fromAW:
                        _aw.output += [Message(CAT_ERR, 9, ("ENDE", "NEU"), GetLine())]
                    else:
                        return
                else:
                    o = createCommand(value, GetLine())
                    if (o is None) and not fromAW:
                        unit.output += [Message(CAT_ERR, 146, (value), GetLine())]
                        ReadUntilNL()
                        continue
                    o.durable = durableCommand
                    durableCommand = False
                    if (unit != None):
                        o.parse()
                        unit.addCommand(o)
                    elif not fromAW:
                        _aw.output += [Message(CAT_ERR, 10, (value), GetLine())]
            elif (type == TOK_SPECIAL):
                if (value == "@"):
                    durableCommand = True
                    continue
                if (value == "+"):
                    # Werden erstmal nicht geprueft
                    (type, value) = GetEntry()
                    if (type != TOK_NUMBER) and not fromAW:
                        _aw.output += [Message(CAT_ERR, 11, ("Zahl"), GetLine())]
                    ReadUntilNL()
                if (value == "="):
                    (type, value) = GetEntry()
                    if (type == TOK_NUMBER):
                        continue
                    elif not fromAW:
                        _aw.output += [Message(CAT_ERR, 11, ("Zahl"), GetLine())]
                if (value == "#"):
                    if new and not fromAW:
                        _aw.output += [Message(CAT_ERR, 9, ("NEU", "ENDE"), GetLine())]
                    PushbackEntry((type, value))
                    return
            elif (type == TOK_COMMENT):
                PushbackEntry((type, value))
                o = createCommand("Kommentar", GetLine())
                o.parse()
                o.durable = durableCommand
                durableCommand = False
                unit.addCommand(o)
                continue
            elif not fromAW:
                _aw.output += [Message(CAT_ERR, 5, (value), GetLine())]
                ReadUntilNL()
        except NewlineException:
            continue
