#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: magicians.py,v 2.2 2005/02/24 19:27:08 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def buildingsMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine Uebersicht aller eigenen Magier, ihrer
#    Faehigkeiten und ihrern Lernmoeglichkeiten.
#
# ---------------------------------------------------------------------------

__all__ = ["magiciansMain"]

from data.configuration import FILE_MAGICIANS, DO_MAGICIANS

def magiciansMain(aw, explicit):
    if not DO_MAGICIANS and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_MAGICIANS, "w")

    print "creating " + FILE_MAGICIANS + "."*3 ,

    regions   = aw.getSortedRegionsAsList()

    f.write("Magierliste fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))

    for region in regions:
        if region.isShortReport:
            continue
        for object in region.sortedObjects:
            for unit in object.sortedUnits:
                if unit.partynumber != aw.partynumber:
                    continue
                if not unit.isMagician():
                    continue
                f.write("%s (%d)\n" % (unit.name, unit.getKey()))
                f.write("  Talente:\n")
                keys = []
                talents = unit.talents.values()
                for talent in talents:
                    f.write("    %s [%s] %d (%s, %d Xp)\n" % (talent.name, talent.getKey(), talent.level, talent.title, talent.xp))
                keys = []
                #talents = unit.learnable.values()
                #for talent in talents:
                #    keys.append(talent.getKey())
                keys = unit.learnable.keys()
                keys.sort()
                f.write("  Kann Lernen:\n")
                for key in keys:
                    talent = unit.learnable[key]
                    f.write("    %s [%s] \n" % (talent.name, talent.getKey()))
                f.write("\n")

    f.close()

    print "done."