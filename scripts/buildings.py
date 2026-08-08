#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: buildings.py,v 2.2 2005/02/24 19:26:23 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def buildingsMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine Uebersicht aller Gebaeude einer Region und
#    deren Ausbaustatus. Fehlende Produktionsgebaeude und Gaststaetten werden
#    ebenfalls mit ausgegeben.
#    Die Ausgabe erfolgt nur fuer Regionen, die zum eigenen Reich gehoeren.
#
# ---------------------------------------------------------------------------

__all__ = ["buildingsMain"]

from data.configuration import FILE_BUILDINGS, DO_BUILDINGS
from rorqual.kb import GetKB

def buildingsMain(aw, explicit):
    if not DO_BUILDINGS and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_BUILDINGS, "w")

    print "creating " + FILE_BUILDINGS + "."*3 ,

    regions   = aw.getSortedRegionsAsList()
    kbObjects = GetKB().buildings.values()
    inn       = GetKB().findBuilding("Gaststaette")

    f.write("Gebaeudeuebersicht fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))
    for region in regions:
        if not region.isTerritory(aw.partynumber):
            continue
        neededBuildings = {inn.key:inn}
        regionProducts  = region.producable.values()
        for p in regionProducts:
            for o in kbObjects:
                if o.favour.has_key(p.getKey()):
                    neededBuildings[o.key] = o
        if (len(region.objects) > 1): # Da Umland immer existiert
            f.write("%d, %d, %s, %s\n" %(region.x, region.y, region.world, region.terrain))
            for object in region.sortedObjects:
                if object.isHinterland():
                    continue
                if not object.kbobj is None:
                    if neededBuildings.has_key(object.kbobj.key):
                        del neededBuildings[object.kbobj.key]
                f.write("  %-25s %3d/%3d\n" % (object.singular, object.size, object.maxSize))
            neededBuildings = neededBuildings.values()
            for n in neededBuildings:
                f.write("  %-25s %3d/%3d\n" % (n.singular, 0, n.maxSize))
            f.write("\n")

    f.close()

    print "done."