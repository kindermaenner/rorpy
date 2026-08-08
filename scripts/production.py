#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: production.py,v 2.2 2005/02/24 19:27:30 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def buildingsMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine Uebersicht der moeglichen Monatsproduktion
#    einer Region und ermittelt daraus die moegliche Gesamtproduktion eines
#    Reiches. Dabei wird nicht beachtet, wieviele Produzenten in einer Region
#    stehen oder ob durch Ausbau der Produktionsgebaeude eine hoehere
#    Produktion moeglich waere.
#    Die Ausgabe erfolgt nur fuer Regionen, die zum eigenen Reich gehoeren.
#
# ---------------------------------------------------------------------------

__all__ = ["productionMain"]

from data.configuration import FILE_PRODUCTION, DO_PRODUCTION

def productionMain(aw, explicit):
    if not DO_PRODUCTION and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_PRODUCTION, "w")

    print "creating " + FILE_PRODUCTION + "."*3 ,

    f.write("Produktionsstatistik fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))
    f.write("Bitte beachten, dass nur eigenes Reichsgebiet beachtet wird!!!\n")
    f.write("Bei den angegebenen Werten handelt es sich um die maximal moegliche Produktion bei aktuellem Ausbau, nicht unbedingt um die tatsaechliche.\n\n")

    regions    = aw.getSortedRegionsAsList()
    production = {}
    names      = {}

    for region in regions:
        if region.isShortReport:
            continue
        if not region.isTerritory(aw.partynumber):
            continue
        f.write(str(region.x) + ", " + str(region.y) + ", " + region.world + ", " + region.terrain + ":\n")
        products = region.producable.values()
        for product in products:
            key = product.getKey()
            if product.amount is None:
                print "1"
            if production.has_key(key):
                production[key] += product.amount
            else:
                production[key] = product.amount
                names[key] = product.plural
            f.write("  %-25s %6s\n" % (names[key], str(product.amount)))
    f.write("\n\nGesamte Produktion:\n")
    keys = production.keys()
    keys.sort()
    for key in keys:
        f.write("  %-25s %6s\n" % (names[key], str(production[key])))

    f.close()

    print "done."