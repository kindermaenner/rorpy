#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: messages.py,v 2.2 2005/02/24 18:17:36 kdm Exp $
#
# ---------------------------------------------------------------------------
#
#  Klasse Message
#      Klasse zur Handhabeung von Nachrichten jeglicher Art.
#
#      __init__(self, type, id, para = (), line = 0):
#          type - Typ der Nachricht. Innerhalb von Rorpy gibt es folgende:
#                 0 - Hinweis
#                 1 - Warnung
#                 2 - Fehler
#          id   - Nummer des Nachrichtentexts. Diese werden in Form eines
#                 Arrays in einer gesonderten Datei mit Konstanten abgelegt.
#          para - Eventuelle Parameter, die fuer die Vervollstaendigung des
#                 Nachrichtentextes benoetigt werden.
#          line - Zeilenangabe, z.B. fuer aufgetretene Fehler in einer Datei.
#
#      __str__(self):
#          Liefert die Daten des Objektes als string, falls dies moeglich
#          ist.
#
#      getType(self):
#          Liefert den Typ der Nachricht unter Beruecksichtigung der user-
#          Einstellungen.
#
# ---------------------------------------------------------------------------

from rorqual.constants import MESSAGE_TEXT
from data.configuration import MOVE_TO_ERR, MOVE_TO_WARN, MOVE_TO_HINT, SHOW_MESSAGE_ID

all = ["Message", "CAT_ERR", "CAT_WARN", "CAT_HINT"]

CAT_INFO = 3
CAT_ERR  = 2
CAT_WARN = 1
CAT_HINT = 0

class Message:
    def __init__(self, type, id, para = (), line = 0):
        self.type = type
        self.id   = id
        self.para = para
        self.line = line

    def __str__(self):
        if (self.line != 0):
            s = "Zeile " + str(self.line) + " "
        else:
            s = ""
        s += MESSAGE_TEXT[self.id] % self.para
        if (SHOW_MESSAGE_ID == 1):
            s += " (Meldungs-ID %d)" % (self.id)
        return s

    def getType(self):
        if self.id in MOVE_TO_ERR:
            return CAT_ERR
        elif self.id in MOVE_TO_WARN:
            return CAT_WARN
        elif self.id in MOVE_TO_HINT:
            return CAT_HINT
        else:
            return self.type