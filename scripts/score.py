#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: score.py,v 2.8 2005/04/04 20:54:37 till Exp $
#
# ---------------------------------------------------------------------------
#
# def buildingsMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Erzeugt aus dem RorAW-Objekt, dem der CR zu grunde liegt, eine
#    Auswertung. Das Skript kann nur die Daten des CRs benutzen, so dass die
#    erzeugt Auswertung von der host-generierten Auswertung abweichen kann.
#
# ---------------------------------------------------------------------------

__all__ = ["scoreMain"]

from data.configuration import FILE_SCORE, DO_SCORE
from rorqual.objects import *
from rorqual.constants import *
from util.wwriter import *

def scoreMain(aw, explicit):
    if not DO_SCORE and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    if aw.turn < 150:
        print FILE_SCORE + " canceled: CR too old."
        return

    f = file(FILE_SCORE, "w")
    out = WrapedPrinter(f)

    print "creating " + FILE_SCORE + "."*3 ,

    out.write("Rorqual Auswertung\n")
    out.write("Rorqual Version: %s\n" % (aw.version))
    out.write("Naechster ETS: %s\n" % (aw.ets))
    out.write("\n")
    out.write("Eigene E-Mailadresse: %s\n" % (aw.email))
    out.write("\n")
    out.write("%s, Jahr %d\n" % (aw.month, aw.year))
    out.write("\n")
    out.write("%s (%d) (Krieg %d, Handel %d, Magie %d)\n" % (aw.partyname, aw.partynumber, aw.ppWar, aw.ppTrade, aw.ppMagic))
    out.write("Glaubenstendenz: %s, Stammrasse: %s\n" % (aw.religion, aw.optedRace))
    out.write("Hauptgottheit  : %s\n" % (aw.god))
    out.write("Spieleinstieg: %d\n" %(aw.gameStart))
    out.write("\n")
    out.write("Eigene KONTAKT-Adresse: %s\n" % (aw.contact))
    out.write("\n")
    out.write("Anfuehrer : %d\n" % (aw.quantityLeaders))
    out.write("Regulaere : %d\n" % (aw.quantityRegulars))
    out.write("Gesamt    : %d\n" % (aw.quantityLeaders + aw.quantityRegulars))
    out.write("Bewaffnete: %d\n" % (aw.gunmen))
    out.write("Anteil Anfuehrer: %d%%\n" % (aw.quantityLeaders*100/(aw.quantityLeaders + aw.quantityRegulars)))
    out.write("\n")
    out.write("Eigene Einheiten     : %d\n" % (aw.ownUnits))
    if (aw.fragmentation < 100):
        out.write("Zersplitterungsfaktor: %d%% (keine Zersplitterung des Volkes).\n" % (aw.fragmentation))
    else:
        out.write("Zersplitterungsfaktor: %d%% (das Volk ist zersplittert).\n" % (aw.fragmentation)) # TODO
    out.write("\n")
    out.write("Nur %d Reiche sind groesser als %s (%d) (Einwohner).\n" % (aw.rank - 1, aw.partyname, aw.partynumber))
    out.write("\n")
    out.write("Gesamtes Einkommen diesen Monat: %d Silber.\n" % (aw.income_entire))
    out.write("\n")
    out.write("Politik:\n")
    out.write("Krieg : %d von %d Kriegspunkten verbraucht.\n" % (aw.ppWarUsed, aw.ppWar))
    out.write("Handel: %d von max. %d Regionen bewirtschaftet.\n" % (aw.ppTradeUsed/2, aw.ppTrade/2))
    out.write("Magier: %d von max. %d in eigenen Diensten.\n" % (aw.ppMagicUsed/24, aw.ppMagic/24))
    out.write("PP    : %d verteilt von %d.\n" % ((aw.ppWar + aw.ppTrade + aw.ppMagic), aw.ppEntire))
    out.write("\n")
    out.write("Diplomatische Position (Standard: %s):\n" % (aw.standard_diplomacy))
    printDiplomacy(aw, out, DIPLOMACY_HOSTILE)
    printDiplomacy(aw, out, DIPLOMACY_UNFRIENDLY)
    printDiplomacy(aw, out, DIPLOMACY_NEUTRAL)
    printDiplomacy(aw, out, DIPLOMACY_FRIENDLY)
    printDiplomacy(aw, out, DIPLOMACY_ALLIED)
    out.write("\n")
    out.write("Reichsschatz: %d.\n" % (aw.treasury))
    out.write("\n")
    if (aw.msgBattles != []):
        out.write("Kaempfe:\n")
        for s in aw.msgBattles:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgErrors != []):
        out.write("Fehler:\n")
        for s in aw.msgErrors:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgDispatch != []):
        out.write("Botschaften:\n")
        for s in aw.msgDispatch:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgContacts != []):
        out.write("Kontakte:\n")
        for s in aw.msgContacts:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgEvents != []):
        out.write("Ereignisse:\n")
        for s in aw.msgEvents:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgTalents != []):
        out.write("Neue Talentberichte:\n")
        for s in aw.msgTalents:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgTransfers != []):
        out.write("Uebergaben:\n")
        for s in aw.msgTransfers:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgProduction != []):
        out.write("Produziertes:\n")
        for s in aw.msgProduction:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgTrade != []):
        out.write("An- und Verkaeufe:\n")
        for s in aw.msgTrade:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgIncome != []):
        out.write("Einkommen:\n")
        for s in aw.msgIncome:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgForeignActivities != []):
        out.write("Fremde Aktivitaeten auf unserem Reichsgebiet:\n")
        for s in aw.msgForeignActivities:
            out.write(str(s) + "\n")
        out.write("\n")
    if (aw.msgMagical != []):
        out.write("Magisches:\n")
        for s in aw.msgMagical:
            out.write(str(s) + "\n")
        out.write("\n")
    out.write("\n")
    regions = aw.getSortedRegionsAsList()
    for r in regions:
        if not r.isShortReport:
            printRegion(r, aw, out)
    for r in regions:
        if r.isShortReport:
            printRegionShortReport(r, out)
    print "done."

def printDiplomacy(aw, out, key):
    if (key ==DIPLOMACY_HOSTILE ):
        diplStr = "Feindlich : "
    elif (key == DIPLOMACY_UNFRIENDLY):
        diplStr = "Unfreundlich : "
    elif (key == DIPLOMACY_NEUTRAL):
        diplStr = "Neutral : "
    elif (key == DIPLOMACY_FRIENDLY):
        diplStr = "Freundlich : "
    elif (key == DIPLOMACY_ALLIED):
        diplStr = "Alliiert : "
    else:
        diplStr = ""
    if (aw.diplomacy[key] != []):
        diplStr += aw.diplomacy[key][0]
        for x in aw.diplomacy[key][1:]:
            diplStr += ", " + x
    else:
        diplStr += "Niemand"
    out.write(diplStr + ".\n")

def printRegionShortReport(r, out):
    out.write("KURZBERICHT:\n")
    regionStr = "%s (%d,%d,%s)" % (r.terrain, r.x, r.y, r.world)
    if not (r.province is None):
        regionStr += " in %s" % (r.province)
    if not (r.homestead is None):
        regionStr += ", dort liegt %s [%s]" % (r.homestead.name, r.homestead.type)
    if not (r.race is None):
        regionStr += ", Bevoelkerung: %s." % (r.race)
    out.write(regionStr + "\n")
    out.setIndent(4)
    if (r.population > 0):
        out.write("  Einwohnerstufe der Region : %2d\n" % (r.population))
    if not (r.homestead is None):
        out.write("  Einwohnerstufe Ansiedlung : %2d\n" % (r.homestead.size))
    out.write("---------------------------------------------------------------------\n")
    if (r.weather != None):
        out.write("  " + r.weather + "\n")
    if r.lanes != {}:
        out.write("Wege:\n")
        key = DIR_NORTH
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_NORTHEAST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_SOUTHEAST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_SOUTH
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_SOUTHWEST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_NORTHWEST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        out.write("\n")
    out.setIndent(2)

def printRegion(r, aw, out):
    regionStr = ""
    if not (r.name is None):
        regionStr += "%s, " % (r.name)
    regionStr += "%s (%d,%d,%s)" % (r.terrain, r.x, r.y, r.world)
    if not (r.province is None):
        regionStr += " in %s" % (r.province)
    if not (r.homestead is None):
        regionStr += ", dort liegt %s [%s]" % (r.homestead.name, r.homestead.type)
    if not (r.race is None):
        regionStr += ", Bevoelkerung: %s" % (r.race)
    if (r.IncomeTaxes != 0):
        regionStr += ", %d Steuersilber." % (r.IncomeTaxes)
    out.write(regionStr + "\n")
    out.setIndent(4)
    if (r.population > 0):
        out.write("  Einwohnerstufe der Region : %2d\n" % (r.population))
    if not (r.homestead is None):
        out.write("  Einwohnerstufe Ansiedlung : %2d\n" % (r.homestead.size))
    out.write("---------------------------------------------------------------------\n")
    if (r.weather != None):
        out.write("  " + r.weather + "\n")
    if (r.wages > 0):
        out.write("  Loehne: %d Silber (Max: %d Silber/%d Arbeiter).\n" % (r.wages, r.IncomeWork, r.IncomeWork/r.wages))
    else:
        out.write("  Loehne: 0 Silber.\n")
    if (r.IncomeEntertainment > 0):
        out.write("  Max. Unterhaltungseinnahmen: %d Silber.\n" % (r.IncomeEntertainment))
    if (r.producable != {}):
        products = r.producable.values()
        productStr = "  Oertliche Produktion: %d %s [%s]" % (products[0].amount, products[0].getName(), products[0].getKey())
        for p in products[1:]:
            productStr += ", %d %s [%s]" % (p.amount, p.getName(), p.getKey())
        out.write(productStr + ".\n")
    if (r.buildingCost > 0):
        out.write("  Ansiedlungsbaukosten: %d%%" % (r.buildingCost))
    out.write("  Gesucht: \n")
    if r.purchases != {}:
        purchases = r.purchases.values()
        for p in purchases:
          out.write("    %-17s [%4s]: %4d fuer %4dS\n" % (p.getName(), p.getKey(), p.amount, p.cost))
    else:
        out.write("    Nichts.\n")
    out.write("  Zu verkaufen: \n")
    if r.sales != {}:
        sales = r.sales.values()
        for p in sales:
          out.write("    %-17s [%4s]: %4d fuer %4dS\n" % (p.getName(), p.getKey(), p.amount, p.cost))
    else:
        out.write("    Nichts.\n")
    out.write("\n")
    if r.lanes != {}:
        out.write("Wege:\n")
        key = DIR_NORTH
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_NORTHEAST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_SOUTHEAST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_SOUTH
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_SOUTHWEST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        key = DIR_NORTHWEST
        if r.lanes.has_key(key):
            printLane(key, r.lanes[key], out)
        out.write("\n")
    out.setIndent(2)
    if (r.ownerNumber != 0):
        out.write("Region gehoert zum Reichsgebiet von %s (%d)\n" % (r.ownerName, r.ownerNumber))
    elif (r.terrain != TYPE_TER_OCEAN):
        out.write("Region gehoert niemandem.\n")
    if (r.minder != []):
        minderStr = "Region wird bewacht von: %s" % (r.minder[0])
        for m in r.minder[1:]:
            minderStr += ", %s" % m
        out.write(minderStr)
    if (r.ownerNumber != 0) or (r.minder != []):
        out.write("\n")
    out.write("\n")
    if r.sum_leaders != 0:
        out.write("Anfuehrer: %d\n" % (r.sum_leaders) ) 
    if r.sum_regulars != 0:
        out.write("Regulaere: %d\n" % (r.sum_regulars) ) 
    if r.sum_livelihood != 0:
        out.write("Zu erwartender Unterhalt: %d\n"% (r.sum_livelihood) )
    out.write("\n")
    if not r.ownProducts is []:
        out.write("Eigene Vorraete:\n")
        keys = map(lambda(x): x.getKey(), r.ownProducts)
        types = []
        for p in r.ownProducts:
            types += p.types
        if "SILB" in keys:
            out.write("--------- GELD:\n")
            for p in r.ownProducts:
                if p.getKey() == "SILB":
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
                    break
        if TYPE_P_HUMANOID in types:
            out.write("--------- RASSEN:\n")
            for p in r.ownProducts:
                if TYPE_P_HUMANOID in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        if TYPE_P_MOUNT in types:
            out.write("--------- REITTIERE:\n")
            for p in r.ownProducts:
                if TYPE_P_MOUNT in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        if TYPE_P_MAGIC in types:
            out.write("--------- MAGISCHE ARTEFAKTE:\n")
            for p in r.ownProducts:
                if TYPE_P_MAGIC in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        if (TYPE_P_WEAPON in types):
            ok = False
            for p in r.ownProducts:
                if (TYPE_P_WEAPON in p.types) and not ("type_distance" in p.types):
                    ok = True
                    break
            if ok:
                out.write("--------- NAHKAMPFWAFFEN:\n")
                for p in r.ownProducts:
                    if (TYPE_P_WEAPON in p.types) and not ("type_distance" in p.types):
                        if p.amount > 1:
                            name = p.plural
                        else:
                            name = p.singular
                        out.write("%5d %s\n" % (p.amount, name))
        if "type_distance" in types:
            out.write("--------- SCHUSSWAFFEN:\n")
            for p in r.ownProducts:
                if "type_distance" in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        if "type_armour" in types:
            out.write("--------- RUESTUNGEN:\n")
            for p in r.ownProducts:
                if "type_armour" in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        if "type_shield" in types:
            out.write("--------- SCHILDE:\n")
            for p in r.ownProducts:
                if "type_shield" in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        if TYPE_P_FOOD in types:
            out.write("--------- NAHRUNG:\n")
            for p in r.ownProducts:
                if TYPE_P_FOOD in p.types:
                    if p.amount > 1:
                        name = p.plural
                    else:
                        name = p.singular
                    out.write("%5d %s\n" % (p.amount, name))
        ok = False
        for p in r.ownProducts:
            if ("type_normal" in p.types) and not (TYPE_P_FOOD in p.types) and not (TYPE_P_MOUNT in p.types) and (len(p.types) > 1) and (p.getKey() != "SILB"):
                ok = True
                break
        if ok:
            out.write("--------- ROHSTOFFE:\n")
            for p in r.ownProducts:
                if ("type_normal" in p.types) and not (TYPE_P_MOUNT in p.types) and not (TYPE_P_FOOD in p.types) and (len(p.types) > 1) and (p.getKey() != "SILB"):
                    out.write("%5d %s\n" % (p.amount, p.plural))            
        if TYPE_P_TRADE in types:
            out.write("--------- LUXUSGUETER:\n")
            for p in r.ownProducts:
                if TYPE_P_TRADE in p.types:
                    out.write("%5d %s\n" % (p.amount, p.plural))
        out.write("\n")
    if r.dimensionGate > 0:
        out.write("Hier gibt es ein Dimensionstor (Tor %d).\n" % (r.dimensionGate))
        out.write("\n")
    elif r.dimensionGate == -1:
        out.write("Hier gibt es ein magisches Tor ins Unbekannte.\n")
        out.write("\n")
    out.write("\n")
    hinterland = r.getHinterland()
    for u in hinterland.sortedUnits:
        if (u.fleetNumber == 0):
            out.write(getUnitString(u, aw, 0) + "\n")
    for f in r.fleets:
        printFleet(f, aw, out)
    for b in r.sortedObjects:
        printBuilding(b, aw, out)
    out.write("\n")
    out.setIndent(2)

def printLane(key, l, out):
    if key == DIR_NORTH:
        dirStr = "  Norden : "
    elif key == DIR_NORTHEAST:
        dirStr = "  Nordosten : "
    elif key == DIR_SOUTHEAST:
        dirStr = "  Suedosten : "
    elif key == DIR_SOUTH:
        dirStr = "  Sueden : "
    elif key == DIR_SOUTHWEST:
        dirStr = "  Suedwesten : "
    elif key == DIR_NORTHWEST:
        dirStr = "  Nordwesten : "
    else:
        dirStr = ""
    if (l.name != ""):
        dirStr += "%s, " % (l.name)
    dirStr += "%s (%d,%d,%s) in %s" % (l.terrain, l.x, l.y, l.world, l.province)
    if not (l.homestead is None):
        dirStr += ", dort liegt %s [%s]" % (l.homestead.name, l.homestead.type)
    if not (l.wall is None):
        dirStr += ", geschuetzt durch %s" % (l.wall)
    if l.ban:
        dirStr += " (Banngebiet)"
    out.write(dirStr + ".\n")

def printBuilding(b, aw, out):
    if b.isHinterland():
        return
    buildingStr = "+ %s [%d] : %s" % (b.name, b.id, b.singular)
    if b.underConstruction or b.hasType(TYPE_O_PRODUCTION):
        buildingStr += ", Groesse %d/%d" % (b.size, b.maxSize)
    if not b.description is None:
        buildingStr += "; %s" % (b.description)
    out.write(buildingStr + "\n")
    out.setIndent(4)
    for u in b.sortedUnits:
        out.write("\n" + getUnitString(u, aw, 2))
    out.write("\n")
    out.setIndent(2)

def printFleet(f, aw, out):
    ship = f.getShipItem()
    fleetStr = "F FLOTTE %d (%d %s)" % (f.id, ship.amount, ship.getName())
    if (f.sortedUnits[0].capacity != {}):
        fleetStr += ", Beladung: %d/%d" % (f.sortedUnits[0].usedCapacity[MOVE_SWIMMING], f.sortedUnits[0].capacity[MOVE_SWIMMING])
    fleetStr += "."
    out.write(fleetStr)
    out.setIndent(4)
    for u in f.sortedUnits:
        out.write(getUnitString(u, aw, 2) + "\n")
    out.setIndent(2)

def getUnitString(u, aw, indent):
    if (u.partynumber == aw.partynumber):
        unitStr = " " * indent + "*"
    elif ("%s (%d)" % (u.partyname, u.partynumber)) in aw.diplomacy[DIPLOMACY_ALLIED]:
        unitStr = " " * indent + "="
    else:
        unitStr = " " * indent + "-" # TODO: Hier muss anhand der Diplomatie-Liste ermittelt werden, welchen Prefix die Einheit bekommt
    unitStr += " %s (%d)" % (u.name, u.id)
    if u.getFlag(FLAG_GUARD):
        unitStr += ", auf Wache"
    if u.conqueringProgress > 0:
        unitStr += ", erobert Region (%d%%)" % (u.conqueringProgress)
    elif u.settlingProgress > 0:
        unitStr += ", besiedelt Region (%d%%)" % (u.settlingProgress)
    if (u.partynumber != 0): # parteigetarnte Einheiten: kein angegebenes Reich
        unitStr += ", %s (%d)" % (u.partyname, u.partynumber)
    if (u.expartynumber != 0):
        unitStr += ", ehemals Buerger von: %s (%d)" % (u.expartyname, u.expartynumber)
    if not u.maskerade is None:
        unitStr += ", %s" % (u.maskerade)
    if u.getFlag(FLAG_AVOID):
        unitStr += ", kaempft nicht"
    if u.getFlag(FLAG_BACKWARD):
        unitStr += ", kaempft hinten"
    if u.getFlag(FLAG_REVEAL_PARTY):
        unitStr += ", offenbart Partei"
    if u.getFlag(FLAG_REVEAL_UNIT):
        unitStr += ", offenbart Einheit"
    if u.getFlag(FLAG_REVEAL) or u.getFlag(FLAG_MASKED):
        unitStr += ", getarnt"
    if u.getFlag(FLAG_HOLD_POSITION):
        unitStr += ", haelt Stellung"
    if u.getFlag(FLAG_TAXING):
        unitStr += ", besteuert selbststaendig"
    if u.getFlag(FLAG_SINGLE):
        unitStr += ", erhaelt keine Unterstuetzung"
    if u.getFlag(FLAG_CONSUME_PARTY):
        unitStr += ", verbraucht Nahrung der Partei"
    if u.getFlag(FLAG_CONSUME_UNIT):
        unitStr += ", verbraucht Nahrung der Einheit"
    if u.getFlag(FLAG_SUPPLY):
        unitStr += ", versorgt andere"
    items = u.inventory.values()
    for i in items:
        if (i.amount == 1):
            unitStr += ", %s [%s]" % (i.singular, i.getKey())
        else:
            unitStr += ", %d %s [%s]" % (i.amount, i.plural, i.getKey())
    if (u.partynumber == aw.partynumber):
        if (u.talents != {}):
            unitStr += "\n" + (" " * (indent + 2)) + "Talente: "
            talents = u.talents.values()
            for t in talents:
                unitStr += "%s [%s] %d (%s" % (t.name, t.getKey(), t.level, t.title)
                if (t.xp > 0):
                    unitStr += ", %d Xp" % (t.xp)
                unitStr += "), "
            unitStr = unitStr[:-2]
        else:
            unitStr += "\n" + (" " * (indent + 2)) + "Talente: Keine"
    if u.isMagician():
        if not (u.combatSpell is None):
            unitStr += "\n" + (" " * (indent + 2)) + "Kampfzauber: %s [%s]." % (u.combatSpell.name, u.combatSpell.getKeyAsString())
        if (u.learnable != {}):
            unitStr += "\n" + (" " * (indent + 2)) + "Kann lernen: "
            talents = u.learnable.values()
            for t in talents:
                unitStr += "%s [%s], " % (t.name, t.getKey())
            unitStr = unitStr[:-2]
    if not (u.description is None):
        unitStr += "; %s" % (u.description)
    if (u.capacity != {}):
        unitStr += "\n" + (" " * (indent + 2)) + "Belastung:"
        if u.capacity.has_key(MOVE_WALKING):
            unitStr += " G %d/%d," % (u.usedCapacity[MOVE_WALKING], u.capacity[MOVE_WALKING])
        if u.capacity.has_key(MOVE_RIDING):
            unitStr += " R %d/%d," % (u.usedCapacity[MOVE_RIDING], u.capacity[MOVE_RIDING])
        if u.capacity.has_key(MOVE_FLYING):
            unitStr += " F %d/%d," % (u.usedCapacity[MOVE_FLYING], u.capacity[MOVE_FLYING])
        if u.capacity.has_key(MOVE_SWIMMING):
            unitStr += " S %d/%d," % (u.usedCapacity[MOVE_SWIMMING], u.capacity[MOVE_SWIMMING])
        unitStr = unitStr[:-1]
    return unitStr + "\n"