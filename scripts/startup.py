#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: startup.py,v 2.9 2005/05/12 22:19:35 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def get_usage():
#    Liefert den Hilfe-Text zu Rorpy.
#
# def parse_args():
#    Wertet die Kommandozeilen-Parameter und gibt sie als Dictionary zurueck.
#    Fuer nicht angegebene Parameter werden default-Werte benutzt oder die
#    Konfiguration ausgewertet.
#
# def init_kb():
#    Initialisiert die KnowledgeBase.
#
# def patchKB(aw):
#    aw       - das RorAW-Objekt
#    Patch fuer die KnowledgeBase, um Rassenwaffen der eigenen Rasse mit 
#    Talentlevel 2 produzieren zu koennen.
#
# def doCheckVDF(obj, indent, log):
#    obj    - zu pruefende Gruppe
#    indent - Einrueckung fuer die Ausgabe
#    log    - Ausgabe-Datei
#    Prueft die nicht-Gruppen-Eintraege der zu pruefenden Gruppe. Fuer Unter-
#    gruppen wird rekursiv diese Funktion wieder aufgerufen.
#
# def checkVDF(obj, log):
#    obj - das VDF-Objekt, aus dem das RorAW-Objekt erzeugt wurde
#    log - Ausgabe-Datei
#    Funktion zum Pruefen, ob alle eingelesenen VDF-Eintraege in das RorAW-
#    Objekt ueberfuehrt wurden.
#
# def getRorObjects(filename):
#    filename - Name der CR-Datei
#
# def readCommands(aw, filename, fromAW = False):
#    aw       - das RorAW-Objekt
#    filename - Dateiname, aus dem die Befehle gelesen werden sollen.
#    fromAW   - Gibt an, ob die Zugvorlage aus der .AUS oder der Zug eingelesen
#               werden soll.
#    Initialisiert den Zug-Parser und startet ihn.
#
# ---------------------------------------------------------------------------

__all__  = ["get_usage", "parse_args", "init_kb", "getRorObjects", "readCommands", "patchKB"]

import sys
import getopt
from rorqual.cr import readCR
from rorqual.kb import GetKB, readConfigfile
from rorqual.objects import RorAW
from rorqual.rorparserutil import InitRorscanner
from rorqual.rorparser import readTurn
from rorqual.constants import *
from data.configuration import FILE_AW, FILE_CR, FILE_TURN

_user_conf  = "data/user.vdf"
_local_conf = "data/local.vdf"

def get_usage():
    return "Rorpy-Skriptsammlung (http:\\\\kenderkrams.de)\n\nUsage: python rorpy.py [--cr=<CR-File>|--zug=<Zug-File>|--script=<Skriptname>|--link|--help]"

def parse_args():
    global _local_conf
    global _user_conf
    lst = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["cr=", "turn=", "script=", "link", "help"])
    except IndexError:
        print get_usage()
        return None
    except getopt.error, msg:
        print msg
        print get_usage()
        return None
    lst["cr"]     = FILE_CR
    lst["aw"]     = FILE_AW
    lst["turn"]   = FILE_TURN
    lst["script"] = None
    lst["link"]   = False
    for o, a in opts:
        if o == "--cr":
            lst["cr"] = a
        if o == "--turn":
            lst["turn"] = a
        if o == "--link":
            lst["link"] = True
        if o == "--script":
            lst["script"] = a
        if o == "--help":
            print get_usage()
            sys.exit(0)
    if (lst["cr"] == ""):
        print get_usage()
        return None
    return lst

def init_kb():
    global _user_conf
    global _local_conf
    kb = GetKB()
    common = readConfigfile("data/common.vdf")
    user   = readConfigfile(_user_conf)
    local  = readConfigfile(_local_conf)
    kb.add(common)
    kb.add(user)
    kb.add(local)
    return kb

def patchKB(aw):
    # TODO_PATCH: Korrektur des Talentwerts fuer die Rassenwaffe der eigenen Rasse
    products = GetKB().products.values()
    for p in products:
        if (TYPE_P_RACEWEAPON in p.types) and not (p.production is None):
            needs = p.production.subterms
            for n in needs:
                if n.__class__.__name__ == "ProductTerm":
                    if n.product.plural == aw.optedRace:
                        for x in needs:
                            if x.__class__.__name__ == "TalentTerm":
                                if x.getKey().lower() == "waff":
                                    x.data[KB_TALENT_LEVEL] = 2
                                    break
                        break

def doCheckVDF(obj, indent, log):
    for sub in obj.getAllSubItems():
        if not (sub.visited or sub.ignored):
            if sub.isGroup():
                print >> log, " " * indent + sub.key
            else:
                print >> log, " " * indent + "[!] " + sub.key
        if sub.isGroup() and not sub.ignored:
            doCheckVDF(sub, indent + 2, log)

def checkVDF(obj, log):
    obj.visitCheck()
    if not obj.visited:
        print >> log, "Nicht beachtete Eintraege: "
        print >> log, obj.key
    doCheckVDF(obj, 2, log)

def checkKB(obj, log):
    for x in obj.missingProducts:
        print >> log, "Unbekannter Gegenstand: ", x
    for x in obj.missingBuildings:
        print >> log, "Unbekanntes Gebaeude: ", x
    for x in obj.missingTalents:
        print >> log, "Unbekanntes Talent: ", x

def getRorObjects(filename):
    cr = readCR(filename)
    aw = RorAW(cr)
    log = open("cr.log", "a")
    checkVDF(cr, log)
    log.close()
    log = open("kb.log", "a")
    checkKB(GetKB(), log)
    log.close()
    return aw

def readCommands(aw, filename, fromAW = False):
    print "reading " + filename + "."*3 ,
    InitRorscanner(filename)
    turn = readTurn(aw, fromAW)
    print "done."
    return turn
