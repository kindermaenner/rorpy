#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: trading.py,v 2.4 2005/02/26 00:38:37 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def buildingsMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine tabellarische Uebersicht ueber die Handels-
#    gueter in den Staedten, die die Partei sieht. Pro Handelsgut wird
#    aufgelistet, in welchen Staedten und zu welchem Preis es an- und ver-
#    kauft werden kann.
#
# ---------------------------------------------------------------------------

__all__ = ["tradingMain"]

from data.configuration import FILE_TRADING, DO_TRADING
from rorqual.objects import RorHomestead, RorRegion, RorProduct
from rorqual.constants import *

def getProductAmountFromRegion(aw, region, key):
    units = region.getUnitsFromPartyAsList(aw.partynumber)
    amount = 0
    for unit in units:
        if unit.inventory.has_key(key):
            amount += unit.inventory[key].amount
    return amount

def tradingMain(aw, explicit):
    if not DO_TRADING and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f  = file(FILE_TRADING, "w")

    print "creating " + FILE_TRADING + "."*3 ,

    regions   = aw.getSortedRegionsAsList()
    purchases = {}
    sales     = {}
    names     = {}

    for region in regions:
        ownProducts = region.getProductsFromParty(aw.partynumber)
        if (region.homestead is None) or region.isShortReport:
            continue
        regionPurchases = region.purchases.values()
        for product in regionPurchases:
            key = product.getKey()
            amount = getProductAmountFromRegion(aw, region, product.getKey())
            val = (region.homestead.name, product.amount, product.cost, amount)
            if purchases.has_key(key):
                purchases[key].append(val)
            else:
                purchases[key] = [val]
            if not names.has_key(key):
                names[key] = product.plural
        regionSales = region.sales.values()
        for product in regionSales:
            if product.hasType(TYPE_P_HUMANOID):
                continue
            key = product.getKey()
            val = (region.homestead.name, product.amount, product.cost)
            if sales.has_key(key):
                sales[key].append(val)
            else:
                sales[key] = [val]
            if not names.has_key(key):
                names[key] = product.plural
    keys = names.keys()
    keys.sort()
    f.write("Handelsuebersicht fuer %s (%d)\n" %(aw.partyname, aw.partynumber))
    f.write("  %s, Jahr %d\n\n" % (aw.month, aw.year))
    f.write("%-18s %-30s %-28s %-12s\n" %("Name", "zu Kaufen in (St/Preis)", "zu Verkaufen in (St/Preis)", "Lagermenge"))
    f.write("=" * 90 + "\n")
    for key in keys: # ueber alle Waren
        if sales.has_key(key):
            sList = sales[key]
        else:
            sList = []
        if purchases.has_key(key):
            pList = purchases[key]
        else:
            pList = []
        i = 0
        lst = map(None, sList, pList) # Aus 2 Listen mach eine Liste zweier Tupel
        for tupel in lst: # ueber alle Kauf-/Verkaufsstaetten
            #print tupel
            if i == 0:
                s = "%-18s" % (names[key][:15], )
                i = 1
            else:
                s = "%-18s" % ("")
            if tupel[0] != None:
                tmp = " %-15s %4d/%4d     " % (tupel[0][0][:15],tupel[0][1],tupel[0][2])
            else:
                tmp = " %-30s" % ("")
            s += tmp
            if tupel[1] != None:
                if (tupel[1][3] == 0):
                    amount = ""
                else:
                    amount = str(tupel[1][3])
                tmp = " %-18s %4d/%4d %8s" % (tupel[1][0][:15],tupel[1][1],tupel[1][2], amount)
            else:
                tmp = " %-28s" % ("")
            s += tmp
            f.write(s + "\n")
        f.write("-" * 90 + "\n")

    f.close()

    print "done."