#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-


# Auszufuehrende Skripte
# Die Skripte, die durch den Aufruf von Rorpy ausgefuehrt werden.
# 1 = ausfuehren, 0 = nicht ausfuehren
DO_BUILDINGS   = 0
DO_CASSANDRA   = 0
DO_INVENTORY   = 0
DO_MAGICIANS   = 0
DO_POPULATION  = 0
DO_PRODUCTION  = 0
DO_TASKMASTERS = 0
DO_TRADING     = 0
DO_SCORE       = 0
DO_GUNMEN      = 0


# Eingabedateien
# Die hier angegebenen Dateinamen werden durch per Parameter uebergebene
# Dateinamen ueberschrieben. Bitte beachten, dass \ fuer Python als
# Sonderzeichen (\\) dargestellt werden muss.
FILE_AW   = ""
FILE_CR   = ""
FILE_TURN = ""


# Ausgabedateien
# Die Ausgaben erfolgen immer in das Unterverzeichnis out.
FILE_BUILDINGS   = "out/Gebaeudeuebersicht.txt"
FILE_CASSANDRA   = "out/Cassandra.txt"
FILE_INVENTORY   = "out/Reichsinventur.txt"
FILE_MAGICIANS   = "out/Magier.txt"
FILE_POPULATION  = "out/Volkszaehlung.txt"
FILE_PRODUCTION  = "out/Gesamtproduktion.txt"
FILE_TASKMASTERS = "out/Lehrer.txt"
FILE_TRADING     = "out/Handelsuebersicht.txt"
FILE_SCORE       = "out/Auswertung.txt"
FILE_GUNMEN      = "out/Bewaffnete.txt"


# Boolsche Variable, die angibt, ob in der Cassandra-Ausgabe die Nachrichten-ID
# mit ausgegeben werden soll. Dieses ist sinnvoll, wenn man eine Nachricht
# unterdruecken oder sie einer anderen Kategorie zuordnen moechte.
SHOW_MESSAGE_ID = 0


# ID-Liste der nicht auszugebenden Meldungen
IGNORE_MESSAGE = []

# Listen, die die Nachrichten enthalten, die vom Benutzer der entsprechenden
# Kategorie zugeordnet wurden.
MOVE_TO_ERR  = []
MOVE_TO_WARN = []
MOVE_TO_HINT = []