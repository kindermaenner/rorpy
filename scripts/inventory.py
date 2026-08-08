#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: inventory.py,v 2.4 2005/02/24 19:26:55 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def inventoryMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine Uebersicht aller Gegenstaende, die die Partei
#    besitzt.
#
# ---------------------------------------------------------------------------

__all__ = ["inventoryMain"]

from data.configuration import FILE_INVENTORY, DO_INVENTORY
from rorqual.constants import TYPE_P_HUMANOID, TYPE_P_SHIP, TYPE_P_MOUNT, TYPE_P_SHIELD, TYPE_P_ARMOUR, TYPE_P_TRADE, TYPE_P_MAGIC, TYPE_P_WEAPON, TYPE_P_FOOD
from rorqual.objects import *

def inventoryMain(aw, explicit):
    if not DO_INVENTORY and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_INVENTORY, "w")

    print "creating " + FILE_INVENTORY + "."*3 ,

    partynumber = aw.partynumber

    regions   = aw.getSortedRegionsAsList()
    names     = {}
    weapons   = {}
    other     = {}
    races     = {}
    armour    = {}
    magic     = {}
    ships     = {}
    mounts    = {}
    trade     = {}
    food      = {}

    for region in regions:
        if region.isShortReport:
            continue
        for object in region.sortedObjects:
            for unit in object.sortedUnits:
                if unit.partynumber != partynumber:
                    continue
                inv = unit.inventory.values()
                for product in inv:
                    key = product.getKey()
                    if not names.has_key(key):
                        names[key] = product.plural
                    if product.hasType(TYPE_P_HUMANOID):
                        if races.has_key(key):
                            races[key] += product.amount
                        else:
                            races[key]  = product.amount
                    elif product.hasType(TYPE_P_TRADE):
                        if trade.has_key(key):
                            trade[key] += product.amount
                        else:
                            trade[key]  = product.amount
                    elif product.hasType(TYPE_P_MAGIC):
                        if magic.has_key(key):
                            magic[key] += product.amount
                        else:
                            magic[key]  = product.amount
                    elif product.hasType(TYPE_P_FOOD):
                        if food.has_key(key):
                            food[key] += product.amount
                        else:
                            food[key]  = product.amount
                    elif product.hasType(TYPE_P_WEAPON):
                        if weapons.has_key(key):
                            weapons[key] += product.amount
                        else:
                            weapons[key]  = product.amount
                    elif product.hasType(TYPE_P_ARMOUR) or product.hasType(TYPE_P_SHIELD):
                        if armour.has_key(key):
                            armour[key] += product.amount
                        else:
                            armour[key]  = product.amount
                    elif product.hasType(TYPE_P_MOUNT):
                        if mounts.has_key(key):
                            mounts[key] += product.amount
                        else:
                            mounts[key]  = product.amount
                    elif product.hasType(TYPE_P_SHIP):
                        if ships.has_key(key):
                            ships[key] += product.amount
                        else:
                            ships[key]  = product.amount
                    else:
                        if other.has_key(key):
                            other[key] += product.amount
                        else:
                            other[key]  = product.amount

    namesKeys   = names.keys()
    weaponsKeys = weapons.keys()
    otherKeys   = other.keys()
    racesKeys   = races.keys()
    armourKeys  = armour.keys()
    magicKeys   = magic.keys()
    shipsKeys   = ships.keys()
    mountsKeys  = mounts.keys()
    tradeKeys   = trade.keys()
    foodKeys    = food.keys()

    namesKeys.sort()
    weaponsKeys.sort()
    otherKeys.sort()
    racesKeys.sort()
    armourKeys.sort()
    magicKeys.sort()
    shipsKeys.sort()
    mountsKeys.sort()
    tradeKeys.sort()
    foodKeys.sort()

    f.write("Reichsinventur fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))
    if (racesKeys != []):
        f.write("Rassen:\n\n")
        for key in racesKeys:
            f.write("  %-25s %7d\n" % (names[key], races[key]))
    if (weaponsKeys != []):
        f.write("\nWaffen:\n\n")
        for key in weaponsKeys:
            f.write("  %-25s %7d\n" % (names[key], weapons[key]))
    if (armourKeys != []):
        f.write("\nRuestungen:\n\n")
        for key in armourKeys:
            f.write("  %-25s %7d\n" % (names[key], armour[key]))
    if (magicKeys != []):
        f.write("\nMagische Gegenstaende:\n\n")
        for key in magicKeys:
            f.write("  %-25s %7d\n" % (names[key], magic[key]))
    if (shipsKeys != []):
        f.write("\nSchiffe:\n\n")
        for key in shipsKeys:
            f.write("  %-25s %7d\n" % (names[key], ships[key]))
    if (mountsKeys != []):
        f.write("\nReittiere:\n\n")
        for key in mountsKeys:
            f.write("  %-25s %7d\n" % (names[key], mounts[key]))
    if (tradeKeys != []):
        f.write("\nLuxusgueter:\n\n")
        for key in tradeKeys:
            f.write("  %-25s %7d\n" % (names[key], trade[key]))
    if (foodKeys != []):
        f.write("\nNahrungsmittel:\n\n")
        for key in foodKeys:
            f.write("  %-25s %7d\n" % (names[key], food[key]))
    if (otherKeys != []):
        f.write("\nsonstiges:\n\n")
        for key in otherKeys:
            f.write("  %-25s %7d\n" % (names[key], other[key]))

    f.close()

    print "done."