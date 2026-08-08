#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: taskmasters.py,v 2.3 2005/02/24 19:29:36 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def taskmastersMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine Uebersicht aller Lehrer der Partei.
#
# ---------------------------------------------------------------------------

__all__ = ["taskmastersMain"]

from data.configuration import FILE_TASKMASTERS, DO_TASKMASTERS
from rorqual.objects import RorRegion

def taskmastersMain(aw, explicit):
    if not DO_TASKMASTERS and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_TASKMASTERS, "w")

    print "creating " + FILE_TASKMASTERS + "."*3 ,

    regions     = aw.getSortedRegionsAsList()
    taskmasters = {}

    for region in regions:
        if region.isShortReport:
            continue
        for object in region.sortedObjects:
            for unit in object.sortedUnits:
                if (unit.partynumber != aw.partynumber):
                    continue
                if not unit.isLeader():
                    continue
                if unit.talents == {}:
                    continue
                regionKey = region.getKey()
                if taskmasters.has_key(regionKey):
                    taskmasters[regionKey].append(unit)
                else:
                    taskmasters[regionKey] = [unit]

    f.write("Lehrerliste fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))

    regionKeys = taskmasters.keys()
    for key in regionKeys:
        region = aw.getRegionByKey(key)
        f.write("%s (%d, %d, %s)\n" % (region.terrain, region.x, region.y, region.world))
        if not (region.homestead is None):
            f.write("    dort liegt %s [%s]\n" % (region.homestead.name, region.homestead.type))
        f.write("=" * 75 + "\n")
        tList = taskmasters[key]
        for taskmaster in tList:
            f.write("  %s (%d): \n" % (taskmaster.name, taskmaster.getKey()))
            talents = taskmaster.talents.values()
            for talent in talents:
                f.write("      %4d %-35s [%4s] %2d, %2d XP\n" % (taskmaster.getPersons(), talent.name, talent.getKey(), talent.level, talent.xp))
            f.write("\n")
        f.write("\n")

    f.close()

    print "done."