#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: rorparserutil.py,v 2.2 2005/02/24 19:35:50 kdm Exp $
#
# ---------------------------------------------------------------------------
#
#
#    class RorScannerException(Exception):
#        Exception Klasse fuer Parserfehler des Rorqual-Zugparsers.
#
#    class NewlineException(RorScannerException):
#        Exception Klasse fuer Zeilenumbruch.
#
#    class EOFException(RorScannerException):
#        Exception Klasse fuer Dateiende.
#
#    def InitRorscanner(filename):
#        filename - zu parsende Datei
#        Initialisiert den Parser.
#
#    def ResetRorscanner(filename):
#        filename - zu parsende Datei
#        Initialisiert den Parser neu, so dass er nun die angegebene Datei
#        parst.
#
#    def GetEntry():
#        Liefert den naechsten Token des Zugs. Bei Erreichen eines Zeilen-
#        umbruchs wird eine NewlineException geworfen, beim Erreichen des
#        Dateiendes wird eine EOFException geworfen.
#
#    def PushbackEntry(e):
#        e - Token, der zurueckgeschrieben werden soll
#        Schreibt den angegebenen Token zurueck, so dass ein darauf folgendes
#        GetEntry() diesen wieder liest.
#
#    def ReadNewline():
#        Ueberprueft, ob das naechste zu beachtende Zeichen ein Zeilenumbruch
#        ist.
#
#    def ReadUntilNL():
#        Liest solange weitere Tokens des Zugs ein, bis die zum Lesen
#        benutzte Funktion GetEntry() eine NewlineException (Zeichen fuer
#        Erreichen eines Zeilenumbruchs) wirft.
#
#    def GetLine():
#        Liefert die Zeile, aus der der aktuelle Token gelesen wurde.
#
# ---------------------------------------------------------------------------

__all__ = ["GetLine", "NewlineException", "EOFException", "InitScanner", "ResetScanner", "GetEntry", "ReadNewline", "ReadUntilNL", "PushbackEntry"]

import string
from rorscanner import *

_lines     = 1
_pushback  = []

class RorScannerException(Exception):
    def __init__(self, str):
        self.str = str

    def __str__(self):
        return "RorScannerException: " + self.value

class NewlineException(RorScannerException):
    def __init__(self):
        pass

    def __str__(self):
        return "NewlineException: " + self.value

class EOFException(RorScannerException):
    def __init__(self):
        pass

    def __str__(self):
        return "EOFException: " + self.value

def InitRorscanner(filename):
    if InitScanner(filename) != 0:
        raise IOError("InitParser Failed")

def ResetRorscanner(filename):
    if InitScanner(filename) != 0:
        raise IOError("ResetParser Failed")

def GetEntry():
    global _lines
    global _pushback
    if (len(_pushback) > 0):
        token = _pushback[0]
        _pushback = _pushback[1:]
    else:
        token = GetNextToken()
    if (token != None):
        (type, value) = token
        if (type != TOK_NEWLINE):
            if (type != TOK_COMMENT) and (type != TOK_STRING):
                value = string.lower(value)
            return (type, value)
        else:
            # Zeilenumbruch: Zeilencounter hochzaehlen und NewlineException schmeissen
            _lines += 1
            raise NewlineException()
    else:
        # Dateiende: EOFException schmeissen
        raise EOFException()

def PushbackEntry(e):
    global _pushback
    global _lines
    _pushback = [e] + _pushback
    if (e[0] == TOK_NEWLINE):
        _lines -= 1

def ReadNewline():
    try:
        (type, value) = GetEntry()
        if (type == TOK_COMMENT):
            (type, value) = GetEntry()
        PushbackEntry((type, value))
        return False
    except NewlineException:
        return True

def ReadUntilNL():
    try:
        while (True):
            GetEntry()
    except NewlineException:
        return

def GetLine():
    global _lines
    return _lines