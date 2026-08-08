#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: gunmen.py,v 2.2 2005/02/24 19:26:44 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def gunmenMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine Uebersicht der Bewaffneten und Monster pro
#    Reich in einer Region
#
# ---------------------------------------------------------------------------

__all__ = ["gunmenMain"]

from data.configuration import FILE_GUNMEN, DO_GUNMEN
from rorqual.objects import *
from rorqual.constants import *

def gunmenMain(aw, explicit):
    if not DO_GUNMEN and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_GUNMEN, "w")

    print "creating " + FILE_GUNMEN + "."*3 ,

    f.write("Truppenuebersicht fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))

    regions = aw.getSortedRegionsAsList()

    for region in regions:
        gunmen    = {}
        names     = {}
        creatures = {}
        units = region.getUnit().values()
        for u in units:
            if u.isArmed(aw):
                if names.has_key(u.partynumber):
                    gunmen[u.partynumber] += u.getArmedPersons(aw)
                else:
                    names[u.partynumber]     = u.partyname
                    gunmen[u.partynumber]    = u.getArmedPersons(aw)
                    creatures[u.partynumber] = 0
            items = u.inventory.values()
            for i in items:
                if i.hasType(TYPE_P_MONSTER):
                    if names.has_key(u.partynumber):
                        creatures[u.partynumber] += i.amount
                    else:
                        names[u.partynumber]     = u.partyname
                        gunmen[u.partynumber]    = 0
                        creatures[u.partynumber] = i.amount
        if gunmen == {}:
            continue

        f.write("(%d,%d,%s,%s)\n" % (region.x, region.y, region.world, region.terrain))
        gunmenKeys = gunmen.keys()
        gunmenKeys.sort()
        for x in gunmenKeys:
            f.write("  %-50s (%4d): %5d Bewaffnete, %6d Monster\n" % (names[x], x, gunmen[x], creatures[x]))
        f.write("\n")

    f.close()

    print "done."
