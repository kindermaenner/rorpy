#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: cassandra.py,v 2.7 2005/04/12 12:59:30 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def cassandraMain(rorObj, explicit):
#    Hauptfunktion von Cassandra, die den Ablauf steuert.
#
# def checkSemantik(units):
#    units - Liste aller Einheiten des RorAW-Objekts
#    Funktion, die fuer alle Befehle Command.checkSemantik aufruft.
#
# def checkFlags(aw, units):
#    aw    - RorAW-Objekt
#    units - Liste aller Einheiten des RorAW-Objekts
#    Prueft die Flags der Einheiten, fuehrt 'sammle limit x' und 'segle' aus.
#
# def executeCommands(aw):
#    aw - RorAW-Objekt
#    Funktion, die fuer alle Befehle, deren Semantik korrekt ist,
#    Command.execute ausfuehrt.
#
# def checkResources(aw, units):
#    aw    - RorAW-Objekt
#    units - Liste aller Einheiten des RorAW-Objekts
#    Berechnet fuer alle Einheiten und Flotten Kapazitaet, Belastung und
#    Bewegungspunkte.
#
# def calcPPs(aw, units):
#    aw    - RorAW-Objekt
#    units - Liste aller Einheiten des RorAW-Objekts
#    Berechnet den Gesamt-PP-Verbrauch der Partei und erzeugt politik.txt.
#
# def calcLivelihood(aw):
#    aw - RorAW-Objekt
#    Berechner fuer alle Einheiten den Lebensunterhalt.
#
# def printCassMessage(o, out):
#    o   - Message-Objekt
#    out - Ausgabe-Objekt
#    Die Funktion liefert fuer alle Meldungen, die erzeugt wurden, den
#    Ausgabestring und beurteilt, ob eine Meldung vom Benutzer ignoriert werden
#    moechte.
#
# def printHtml(aw):
#    aw - RorAW-Objekt
#    Funktion zum Schreiben der HTML-Prognose. Fuer Einheiten wird printUnit
#    aufgerufen
#
# def printUnit(unit, aw, out):
#    unit - Einheit, die ausgegeben werden soll
#    aw   - RorAW-Objekt
#    out  - Ausgabe-Objekt
#    Funktion zum Schreiben der HTML-Ausgabe fuer Einheiten.
#
# ---------------------------------------------------------------------------

__all__ = ["cassandraMain"]

import sys
from data.configuration import FILE_CASSANDRA, IGNORE_MESSAGE, DO_CASSANDRA
from util.htmloutput    import HTMLPage
from util.messages      import *
from rorqual.commands   import createCommand
from rorqual.constants  import *
from rorqual.kb         import GetKB

_commandOrder = []
_commandOrder += ["bezahle"]
_commandOrder += ["neu"]
_commandOrder += ["adresse"]
_commandOrder += ["benenne"]
_commandOrder += ["beschreibe"]
_commandOrder += ["botschaft"]
_commandOrder += ["dauersteuer"]
_commandOrder += ["einzeln"]
_commandOrder += ["erklaere"]
_commandOrder += ["glaubenstendenz"]
_commandOrder += ["halte"]
_commandOrder += ["hinten"]
_commandOrder += ["kampfzauber"]
_commandOrder += ["offenbare"]
_commandOrder += ["option"]
_commandOrder += ["partei"]
_commandOrder += ["passwort"]
_commandOrder += ["reihenfolge"]
_commandOrder += ["verbrauche"]
_commandOrder += ["vermeide"]
_commandOrder += ["versorge"]
_commandOrder += ["vertretung"]
_commandOrder += ["zeige"]
_commandOrder += ["gott"]
_commandOrder += ["ausbauen"]
_commandOrder += ["stammrasse"]
_commandOrder += ["kontakt"]
_commandOrder += ["verlasse"]
_commandOrder += ["ausschiffen"]
_commandOrder += ["betrete"]
_commandOrder += ["befoerdere"]
_commandOrder += ["attackiere"]
_commandOrder += ["meuchle"]
_commandOrder += ["stehle"]
_commandOrder += ["beanspruche"]
_commandOrder += ["behalte"]
_commandOrder += ["sammle"]
_commandOrder += ["gib"]
_commandOrder += ["foerdere"]
_commandOrder += ["opfere"]
_commandOrder += ["einschiffen"]
_commandOrder += ["zerstoere"]
_commandOrder += ["zaubere"]
_commandOrder += ["bewache"]
_commandOrder += ["verkaufe"]
_commandOrder += ["kaufe"]
_commandOrder += ["stirb"]
_commandOrder += ["vergiss"]
_commandOrder += ["reise"]
_commandOrder += ["segle"]
_commandOrder += ["vorruecken"]
_commandOrder += ["pluendere"]
_commandOrder += ["treibe"]
_commandOrder += ["lerne"]
_commandOrder += ["lehre"]
_commandOrder += ["besiedeln"]
_commandOrder += ["erobere"]
_commandOrder += ["arbeite"]
_commandOrder += ["baue"]
_commandOrder += ["produziere"]
_commandOrder += ["unterhalte"]
_commandOrder += ["verwerte"]
_commandOrder += ["belagere"]

_ppMagic = 0
_ppTrade = 0
_ppWar   = 0

def cassandraMain(rorObj, explicit):
    if not DO_CASSANDRA and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    print "creating turn preview" + "."*3 ,
    aw = rorObj.clone() # Kopie des RorAW-Objekts erstellen
    units = aw.getUnits()
    checkSemantik(units)      # Semantik der Befehle pruefen
    checkFlags(aw, units)     # Anhand der Befehle die Flags der Einheiten anpassen
    executeCommands(aw)       # Befehle ausfuehren
    checkResources(aw, units) # Pruefung, ob die Resourcen einer Einheit (langer Befehl, Zauber) verbruacht wurden
    calcPPs(aw, units)        # Verbrauch der PPs berechnen
    calcLivelihood(aw)        # Lebensunterhalt berechnen
    printHtml(aw)             # Ausgabe
    print "done."

def checkSemantik(units):
    for unit in units:
        for command in unit.commands:
            command.checkSemantik(unit)

def checkFlags(aw, units):
    commandLimit  = createCommand("sammle", 0)
    commandSail   = createCommand("segle", 0)
    for unit in units:
        if (unit.partynumber != aw.partynumber):
            continue
        if unit.getFlag(FLAG_TAXING):
            unit.commands += [createCommand("treibe", 0)]
        for command in unit.commands:
            if (len(command.output) != 0):
                continue
            if (command.syntax == commandLimit.syntax):
                if (command.type == 1):
                    command.execute(unit, unit.region, aw)
            if (command.syntax == commandSail.syntax):
                if (len(command.parameters) == 0): # Befehl: segle
                    command.execute(unit, unit.region, aw)

def executeCommands(aw):
    for commandName in _commandOrder:
        commandToExecute = createCommand(commandName, 0)
        regions = aw.regions.values()
        if commandToExecute.__class__.__name__ == "CommandEinschiffen":
            for region in regions:
                units = region.getUnitsFromPartyAsList(aw.partynumber)
                for unit in units:
                    for command in unit.commands:
                        if (command.syntax == commandToExecute.syntax):
                            if (len(command.parameters) == 0) or (command.parameters[0] == unit):
                                command.execute(unit, region, aw)
                            break
                        continue
        for region in regions:
            units = region.getUnitsFromPartyAsList(aw.partynumber)
            for unit in units:
                for command in unit.commands:
                    if command.executed:         # Befehl wurde bereits ausgefuehrt
                        continue
                    if len(command.output) != 0: # Fehlermeldung liegt vor
                        continue
                    if (command.syntax == commandToExecute.syntax):
                        command.execute(unit, region, aw)
                        continue
                    continue
            if commandToExecute.__class__.__name__ == "CommandAusschiffen":
                for f in region.fleets:
                    if (len(f.sortedUnits) == 0):
                        region.fleets.remove(f)
                        continue
                    if (len(f.sortedUnits) > 0) and (f.sortedUnits[0].getKey() != f.getKey()):
                        for u in f.sortedUnits:
                            f.disembark(u)
                            u.output += [Message(CAT_WARN, 155)]
                        region.getHinterland().units[f.getKey()].output += [Message(CAT_WARN, 154)]
                        region.fleets.remove(f)
                    continue
    for region in regions:
        unit = region.getUnit(0)
        if not unit is None:
            unit.object.delUnit(unit)

def checkResources(aw, units):
    for unit in units:
        if (unit.partynumber != aw.partynumber):
            continue
        if unit.getRace() is None:
            unit.output += [Message(CAT_HINT, 30)]
            continue
        if unit.isSacrificed:
            continue
        if (unit.longCommand == ""):
            unit.output += [Message(CAT_WARN, 31)]
        if unit.isMagician():
            if (unit.combatSpell is None):
                unit.output += [Message(CAT_HINT, 32)]
            if not unit.hasConjured:
                unit.output += [Message(CAT_HINT, 33)]
        unit.calcEncumbrance()
        unit.calcCapacity()
        unit.calcBP()
    regions = aw.regions.values()
    for r in regions:
        for f in r.fleets:
            f.calcEncumbrance()
            f.calcCapacity()
            f.calcBP()

def calcPPs(aw, units):
    global _ppMagic
    global _ppTrade
    global _ppWar

    f = file("out/politik.txt", "w")

    regions = aw.regions.values()
    for region in regions:
        if region.ppTrade:
            f.write("In %s wird Handel getrieben: 2PPs \n" % (region.getKeyAsString()))
            _ppTrade += 2
        if region.ppWar:
            costRegion = region.getPPCost()
            f.write("In %s werden Steuern getrieben: %d PPs fuer die Region\n" % (region.getKeyAsString(),costRegion))
            _ppWar += costRegion
            if not region.homestead is None:
                costHomestead = region.homestead.getPPCost()
                f.write("In %s werden Steuern getrieben: %d PPs fuer die Ansiedlung\n" % (region.getKeyAsString(),costHomestead))
                _ppWar += costHomestead

    for unit in units:
        if unit.isMagician():
            _ppMagic += 24

    ppUsed = _ppMagic + _ppTrade + _ppWar
    if (ppUsed < aw.ppEntire):
        aw.output += [Message(CAT_HINT, 34, (aw.ppEntire - ppUsed))]
    elif (ppUsed > aw.ppEntire):
        aw.output += [Message(CAT_WARN, 35)]
    if (_ppMagic < aw.ppMagic):
        aw.output += [Message(CAT_HINT, 36)]
    if (_ppWar > aw.ppWar):
        aw.output += [Message(CAT_ERR, 157, ("Krieg"))]
    if (_ppTrade > aw.ppTrade):
        aw.output += [Message(CAT_ERR, 157, ("Handel"))]
    if (_ppMagic > aw.ppMagic) :
        aw.output += [Message(CAT_ERR, 157, ("Magie"))]

def calcLivelihood(aw):
    regions = aw.regions.values()
    for region in regions:
        ownUnits = region.getUnitsFromPartyAsList(aw.partynumber)
        for unit in ownUnits:
            if (unit.partynumber != aw.partynumber):
                continue
            if unit.isSacrificed:
                continue
            if unit.isSurrendered:
                continue
            if unit.getFlag(FLAG_CONSUME_PARTY) or unit.getFlag(FLAG_CONSUME_UNIT): #TODO verbrauche
                unprovidedPersons = unit.getPersons()
                inventory = unit.inventory.values()
                for i in inventory:
                    if i.hasType(TYPE_P_FOOD):
                        if i.amount < unprovidedPersons:
                            delAmount = i.amount
                        else:
                            delAmount = unprovidedPersons
                        unit.delProduct(i.getKey(), delAmount)
                        unprovidedPersons -= delAmount
                        if (unprovidedPersons <= 0):
                            break
                if unit.getFlag(FLAG_CONSUME_PARTY):
                    for u in ownUnits:
                        if supplier.isSacrificed or supplier.isSurrendered:
                            continue
                        inventory = u.inventory.values()
                        for i in inventory:
                            if i.hasType(TYPE_P_FOOD):
                                if i.amount < unprovidedPersons:
                                    delAmount = i.amount
                                else:
                                    delAmount = unprovidedPersons
                                u.delProduct(i.getKey(), delAmount)
                                unprovidedPersons -= delAmount
                                if (unprovidedPersons <= 0):
                                    break
                if unprovidedPersons <= 0:
                    continue
                livelihood = unit.calcLivelihood(unit.getPersons() - unprovidedPersons)
            else:
                livelihood = unit.calcLivelihood()
            region.MoneyLivelihood += livelihood
            if unit.inventory.has_key(ID_P_SILB):
                deletable = unit.inventory[ID_P_SILB].amount
                if (livelihood < deletable):
                    deletable = livelihood
                unit.delProduct(ID_P_SILB, deletable)
                livelihood -= deletable
            if (livelihood <= 0):
                continue
            for supplier in ownUnits:
                if (supplier == unit):
                    continue
                if not supplier.getFlag(FLAG_SUPPLY):
                    continue
                if supplier.isSacrificed or supplier.isSurrendered:
                    continue
                if supplier.inventory.has_key(ID_P_SILB):
                    deletable = supplier.inventory[ID_P_SILB].amount
                    if (livelihood < deletable):
                        deletable = livelihood
                    supplier.delProduct(ID_P_SILB, deletable)
                    livelihood -= deletable
                if (livelihood <= 0):
                    break
            if livelihood > 0:
                region.MoneyLivelihood -= livelihood
                unit.output += [Message(CAT_WARN, 37)]

def printCassMessage(o, out):
    # User moechte Nachricht ignorieren
    if o.id in IGNORE_MESSAGE:
        return

    msgType = o.getType()
    if (msgType == 0):
        out.ilog(str(o), CassandraOutput.LOG_HINT)
    elif (msgType == 1):
        out.ilog(str(o), CassandraOutput.LOG_WARNING)
    elif (msgType == 2):
        out.ilog(str(o), CassandraOutput.LOG_ERROR)
    elif (msgType == 3):
        out.log(str(o), CassandraOutput.LOG_INFO)

def printHtml(aw):
    global _ppMagic
    global _ppTrade
    global _ppWar
    regions = aw.getSortedRegionsAsList()
    out = CassandraOutput("./out/navigation.htm", "./out/protocol.htm")
    out.startOutput()
    out.setDebug(1)
    out.log("Rorqual Scanner Cassandra II", CassandraOutput.LOG_HEADING)
    out.log("Using Python Version: " + sys.version , CassandraOutput.LOG_HEADING)
    out.log("(c) 2004 N.Kindermann, T.Bischoff" , CassandraOutput.LOG_HEADING)
    out.log("Bugreports bitte an: rorpy@kenderkrams.de" , CassandraOutput.LOG_HEADING)
    out.brMain()
    kb = GetKB()
    if kb.output != []:
        for o in kb.output:
            printCassMessage(o, out)
        out.br()
    out.ilog("Prognose fuer den naechsten Spielzug ", CassandraOutput.LOG_HEADING)
    out.log(aw.ets, CassandraOutput.LOG_MESSAGE)
    out.br()
    out.log(aw.partyname + " (" + str(aw.partynumber) + ")", CassandraOutput.LOG_MESSAGE)
    out.log("Ausrichtung: " + aw.religion + ", Stammrasse: " + aw.optedRace, CassandraOutput.LOG_MESSAGE)
    out.log("Bevoelkerung: " + str(aw.quantityRegulars) + " Regulaere, " + str(aw.quantityLeaders) + " Anfuehrer", CassandraOutput.LOG_MESSAGE)
    out.log("Reichsschatz: " + str(aw.treasury), CassandraOutput.LOG_MESSAGE)
    out.log("Max. Politik: " + str(aw.ppMagic/24) + " Magier, " + str(aw.ppTrade) + " Handel, " + str(aw.ppWar) + " Krieg", CassandraOutput.LOG_MESSAGE)
    out.log("Akt. Politik: " + str(_ppMagic/24) + " Magier, " + str(_ppTrade) + " Handel, " + str(_ppWar) + " Krieg", CassandraOutput.LOG_MESSAGE)
    for o in aw.output:
        printCassMessage(o, out)
    out.hlineIndex()
    for region in regions:
        if (len(region.getUnitsFromParty(aw.partynumber)) == 0):
            continue
        ownProducts = region.getProductsFromParty(aw.partynumber)
        if (ownProducts == {}):
            continue
        out.brMain()
        out.ilog(region.terrain + " " + region.getKeyAsString(), CassandraOutput.LOG_HEADING)
        if region.ownerNumber != 0:
            out.log("Gehoert zum Reichsgebiet von: " + region.ownerName + " (" + str(region.ownerNumber) + ")", CassandraOutput.LOG_HEADING)
        if region.minder != None:
            minder = ""
            for m in region.minder:
                if minder == "":
                    minder = str(m)
                    continue
                minder += ", " + str(m)
            out.log("Wird bewacht von: " + minder, CassandraOutput.LOG_HEADING)
        out.log("CashFlow:", CassandraOutput.LOG_HEADING)
        if (region.IncomeTaxes > 0):
            strTaxes = "Steuern %d von max. %d (%3.2f%%)." % (region.IncomeTaxesUsed, region.IncomeTaxes, (float(region.IncomeTaxesUsed)/float(region.IncomeTaxes) * 100))
            if (region.IncomeTaxesUsed > region.IncomeTaxes):
                strTaxes += " %d Eintreiber zu viel" % ((region.IncomeTaxesUsed - region.IncomeTaxes) / 50)
            elif (region.IncomeTaxesUsed < region.IncomeTaxes):
                strTaxes += " Noch %d fehlende Eintreiber." % ((region.IncomeTaxes - region.IncomeTaxesUsed) / 50)
            out.log(strTaxes, CassandraOutput.LOG_INFO)
        if (region.IncomeEntertainment > 0):
            strEntertainment = "Unterhaltung %d von max. %d (%3.2f%%)." % (region.IncomeEntertainmentUsed, region.IncomeEntertainment, (float(region.IncomeEntertainmentUsed)/float(region.IncomeEntertainment) * 100))
            if (region.IncomeEntertainmentUsed > region.IncomeEntertainment):
                strEntertainment += " Es sind %d Unterhalter (T1) zu viel." % ((region.IncomeEntertainmentUsed - region.IncomeEntertainment) / 20)
            elif (region.IncomeEntertainmentUsed < region.IncomeEntertainment):
                strEntertainment += " Es fehlen noch %d Unterhalter (T1)." % ((region.IncomeEntertainment - region.IncomeEntertainmentUsed) / 20)
            out.log(strEntertainment, CassandraOutput.LOG_INFO)
        if (region.IncomeWork > 0):
            strWork = "Arbeit %d von max. %d (%3.2f%%)." % (region.IncomeWorkUsed, region.IncomeWork, (float(region.IncomeWorkUsed)/float(region.IncomeWork) * 100))
            if (region.IncomeWorkUsed > region.IncomeWork):
                strWork += " Fuer %d Arbeiter sind keine Arbeitsplaetzte frei." % ((region.IncomeWorkUsed - region.IncomeWork) / region.wages)
            elif (region.IncomeWorkUsed < region.IncomeWork):
                strWork += " Noch %d Arbeitsplaetze frei." % ((region.IncomeWork - region.IncomeWorkUsed) / region.wages)
            out.log(strWork, CassandraOutput.LOG_INFO)
        out.log("Ankaeufe %d / Verkauefe %d" % (region.MoneySales, region.MoneyPurchases), CassandraOutput.LOG_INFO)
        out.log("Lernkosten %d / Lebensunterhalt %d" % (region.MoneyLearning, region.MoneyLivelihood), CassandraOutput.LOG_INFO)
        regionSupport = homesteadSupport = 0
        if region.isSupported or (not (region.homestead is None) and region.homestead.isSupported):
            if region.isSupported:
                regionSupport = (region.population + 1) * 3000
            strSupport = "Foerderung Region %d" % (regionSupport)
            if not (region.homestead is None):
                if region.homestead.isSupported:
                    homesteadSupport = (region.homestead.size + 1) * 5000
                strSupport += " / Foerderung Ansiedlung %d" % (homesteadSupport)
            out.log(strSupport, CassandraOutput.LOG_INFO)
        # Cashflow ausrechnen
        cashflow = region.MoneyPurchases - region.MoneySales - region.MoneyLearning - region.MoneyLivelihood - regionSupport - homesteadSupport
        if (region.IncomeTaxesUsed < region.IncomeTaxes):
            cashflow += region.IncomeTaxesUsed
        else:
            cashflow += region.IncomeTaxes
        if (region.IncomeEntertainmentUsed < region.IncomeEntertainment):
            cashflow += region.IncomeEntertainmentUsed
        else:
            cashflow += region.IncomeEntertainment
        if (region.IncomeWorkUsed < region.IncomeWork):
            cashflow += region.IncomeWorkUsed
        else:
            cashflow += region.IncomeWork
        out.log("CashFlow: %d" % (cashflow), CassandraOutput.LOG_INFO)
        out.brIndex()
        out.log("Produktionskapazitaeten:", CassandraOutput.LOG_HEADING)
        producable = region.producable.values()
        for p in producable:
            percent = (float(p.tradedAmount)/float(p.amount)) * 100
            out.log(p.singular + ": " + str(p.tradedAmount) + " von " + str(p.amount) + (" (%3.2f%%)" % percent),CassandraOutput.LOG_INFO)
        out.log("Regionsstatistik:", CassandraOutput.LOG_HEADING)
        out.log("%d Einheiten / %d Personen" % (region.getUnitCountFromParty(aw.partynumber), region.getPersonAmountFromParty(aw.partynumber)), CassandraOutput.LOG_INFO)
        out.log("Vorraete in der Region:", CassandraOutput.LOG_HEADING)
        for i in ownProducts:
            if (ownProducts[i].amount == 0): # Durch behalte-Befehle kann es zu 0-Mengen kommen, wenn die Einheit anschliessend nix davon sammeln kann
                continue
            out.log(str(ownProducts[i].amount) + " " + ownProducts[i].getName() ,CassandraOutput.LOG_INFO)
        out.brMain()
        for o in region.sortedObjects:
            # Gebaeude [1] : Mine, Groesse 6/100
            if o.isHinterland():
                out.log("Gebaeude [%d] : %s" % (o.getKey(), o.singular), CassandraOutput.LOG_HEADING)
            else:
                out.log("Gebaeude [%d] : %s, Groesse %d/%d" % (o.getKey(), o.singular, o.size, o.maxSize), CassandraOutput.LOG_HEADING)
            out.log("%d Einheiten / %d Personen" % (o.getUnitCountFromParty(aw.partynumber), o.getPersonAmountFromParty(aw.partynumber)), CassandraOutput.LOG_INFO)
            for unit in o.sortedUnits:
                if (unit.fleetNumber != 0):
                    continue
                printUnit(unit, aw, out)
        for fleet in region.fleets:
            if not fleet.hasUnitsFromParty(aw.partynumber):
                continue
            out.log("Flotte " + fleet.getKeyAsString(), CassandraOutput.LOG_HEADING)
            if fleet.bp[MOVE_SWIMMING] > 0:
                out.log("Bewegung %s:" % (MOVE_SWIMMING), CassandraOutput.LOG_INFO)
                out.log(" Werte incl. Eigengewicht: Kapazitaet %d, Gewicht %d" % (fleet.capacity[MOVE_SWIMMING], fleet.encumbrance), CassandraOutput.LOG_INFO)
                out.log(" Werte ohne Eigengewicht:  Kapazitaet %d, Gewicht %d" % (fleet.capacityWithoutOwnWeight[MOVE_SWIMMING], fleet.encumbranceWithoutOwnWeight[MOVE_SWIMMING]), CassandraOutput.LOG_INFO)
            if fleet.bp[MOVE_FLYING] > 0:
                out.log("Bewegung %s:" % (MOVE_SWIMMING), CassandraOutput.LOG_INFO)
                out.log(" Werte incl. Eigengewicht: Kapazitaet %d, Gewicht %d" % (fleet.capacity[MOVE_SWIMMING], fleet.encumbrance), CassandraOutput.LOG_INFO)
                out.log(" Werte ohne Eigengewicht:  Kapazitaet %d, Gewicht %d" % (fleet.capacityWithoutOwnWeight[MOVE_SWIMMING], fleet.encumbranceWithoutOwnWeight[MOVE_SWIMMING]), CassandraOutput.LOG_INFO)
            out.brMain()
            for unit in fleet.sortedUnits:
                printUnit(unit, aw, out)
        out.hlineIndex()
    out.endOutput()

def printUnit(unit, aw, out):
    if (unit.partynumber != aw.partynumber):
        return
    out.ilog(unit.name + " (" + unit.getKeyAsString() + ")", CassandraOutput.LOG_MESSAGE)
    if unit.isSacrificed:
        for o in unit.output:
            printCassMessage(o, out)
        out.brMain()
        return
    if unit.isSurrendered:
        for o in unit.output:
            printCassMessage(o, out)
        for c in unit.commands:
            if (len(c.output) != 0):
                for o in c.output:
                    printCassMessage(o, out)
            if not c.executed:
                out.ilog("Befehl " + c.syntax + " wurde nicht ausgefuehrt.", CassandraOutput.LOG_ERROR)
        out.brMain()
        return
    if (unit.inventory == {}):
        for o in unit.output:
            printCassMessage(o, out)
        out.brMain()
        return
    inventory = unit.inventory.values()
    talents   = unit.talents.values()
    if unit.bp[MOVE_SWIMMING] > 0:
        out.log("Bewegung %s:" % (MOVE_SWIMMING), CassandraOutput.LOG_INFO)
        out.log(" Werte incl. Eigengewicht: Kapazitaet %d, Gewicht %d" % (unit.capacity[MOVE_SWIMMING], unit.encumbrance), CassandraOutput.LOG_INFO)
        out.log(" Werte ohne Eigengewicht:  Kapazitaet %d, Gewicht %d" % (unit.capacityWithoutOwnWeight[MOVE_SWIMMING], unit.encumbranceWithoutOwnWeight[MOVE_SWIMMING]), CassandraOutput.LOG_INFO)
    if unit.bp[ MOVE_WALKING] > 0:
        out.log("Bewegung %s:" % (MOVE_WALKING), CassandraOutput.LOG_INFO)
        out.log(" Werte incl. Eigengewicht: Kapazitaet %d, Gewicht %d" % (unit.capacity[MOVE_WALKING], unit.encumbrance), CassandraOutput.LOG_INFO)
        out.log(" Werte ohne Eigengewicht:  Kapazitaet %d, Gewicht %d" % (unit.capacityWithoutOwnWeight[MOVE_WALKING], unit.encumbranceWithoutOwnWeight[MOVE_WALKING]), CassandraOutput.LOG_INFO)
    if unit.bp[MOVE_RIDING] > 0:
        out.log("Bewegung %s:" % (MOVE_RIDING), CassandraOutput.LOG_INFO)
        out.log(" Werte incl. Eigengewicht: Kapazitaet %d, Gewicht %d" % (unit.capacity[MOVE_RIDING], unit.encumbrance), CassandraOutput.LOG_INFO)
        out.log(" Werte ohne Eigengewicht:  Kapazitaet %d, Gewicht %d" % (unit.capacityWithoutOwnWeight[MOVE_RIDING], unit.encumbranceWithoutOwnWeight[MOVE_RIDING]), CassandraOutput.LOG_INFO)
    if unit.bp[MOVE_FLYING] > 0:
        out.log("Bewegung %s:" % (MOVE_FLYING), CassandraOutput.LOG_INFO)
        out.log(" Werte incl. Eigengewicht: Kapazitaet %d, Gewicht %d" % (unit.capacity[MOVE_FLYING], unit.encumbrance), CassandraOutput.LOG_INFO)
        out.log(" Werte ohne Eigengewicht:  Kapazitaet %d, Gewicht %d" % (unit.capacityWithoutOwnWeight[MOVE_FLYING], unit.encumbranceWithoutOwnWeight[MOVE_FLYING]), CassandraOutput.LOG_INFO)
    if (unit.longCommand != ""):
        out.log("langer Befehl: " + unit.longCommand, CassandraOutput.LOG_MESSAGE)
    if unit.isMagician() and not (unit.combatSpell is None):
        out.log("Kampfzauber: " + unit.combatSpell.name, CassandraOutput.LOG_MESSAGE)
    for i in inventory:
        if (i.amount == 0): # Durch behalte-Befehle kann es zu 0-Mengen kommen, wenn die Einheit anschliessend nix davon sammeln kann
            continue
        out.log(str(i.amount) + " " + i.plural, CassandraOutput.LOG_MESSAGE)
    for t in talents:
        strTalent = "%s %d (%s" % (t.name, t.level, t.title)
        if (t.xp != -1): strTalent += ", %d XP" % (t.xp)
        if (unit.learnedTalent == t.getKey()):
            strTalent += " lernt"
            if unit.isTeached:
                strTalent += " mit Lehrer"
        strTalent += ")"
        out.log(strTalent, CassandraOutput.LOG_MESSAGE)
    for o in unit.output:
        printCassMessage(o, out)
    for c in unit.commands:
        if (len(c.output) != 0):
            for o in c.output:
                printCassMessage(o, out)
        if not c.executed:
            out.ilog("Befehl " + c.syntax + " wurde nicht ausgefuehrt.", CassandraOutput.LOG_ERROR)
    out.brMain()

class CassandraOutput(HTMLPage):
    TARGET_INDEX = 1
    TARGET_MAIN = 2

    LOG_DEBUG = 1    # Nur in Main, falls debug == 1
    LOG_MESSAGE = 2  # Nur in Main, Farbe Message
    LOG_WARNING = 3  # Link, von Index in Main, Farbe Warning
    LOG_ERROR = 4    # Link, von Index in Main, Farbe Error
    LOG_HEADING = 5  # Link, von Index in Main, Farbe Message
    LOG_HINT = 6     # Link, von Index in Main, Farbe Hint
    LOG_INFO = 7     # Nur in Main, Farbe Info

    def __init__(self, indexfile, mainfile):
        #super(CassandraOutput, self).__init__()
        self.index = HTMLPage(indexfile, "Cassandra II Navigator")
        self.index.addHeadEntry('<base target="prog">')
        self.main = HTMLPage(mainfile, "Cassandra II Prognose")
        self.debug = 0
        self.nextAnchor = 1
        self.main.addStyleSheet("cassandra.css")
        self.index.addStyleSheet("navigation.css")

    def getAnchor(self):
        s = "ref%04d" % (self.nextAnchor)
        self.nextAnchor += 1
        return s

    def setDebug(self, debug):
        self.debug = debug

    def startOutput(self):

        self.index.startPage()
        self.main.startPage()
        self.index.startPar()

    def endOutput(self):
        self.index.endPar()
        self.index.endPage()
        self.main.endPage()

    def getIndex(self):
        return self.index

    def getMain(self):
        return self.main

    def ilog(self, text, flag):
        if flag == self.LOG_DEBUG:
            if self.debug == 1:
                ref = self.getAnchor()
                self.main.startAnchor(ref)
                self.main.addTextEx(text, {"class":"debug"})
                self.main.endAnchor()
                self.main.newline()
                self.index.startNoBreak()
                self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"debug"})
                self.index.endNoBreak()
                self.index.newline()
        elif flag == self.LOG_MESSAGE:
            ref = self.getAnchor()
            self.main.startAnchor(ref)
            self.main.addTextEx(text, {"class":"message"})
            self.main.endAnchor()
            self.main.newline()
            self.index.startNoBreak()
            self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"message"})
            self.index.endNoBreak()
            self.index.newline()
        elif flag == self.LOG_INFO:
            ref = self.getAnchor()
            self.main.startAnchor(ref)
            self.main.addTextEx(text, {"class":"info"})
            self.main.endAnchor()
            self.main.newline()
            self.index.startNoBreak()
            self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"info"})
            self.index.endNoBreak()
            self.index.newline()
        elif flag == self.LOG_WARNING:
            ref = self.getAnchor()
            self.main.startAnchor(ref)
            self.main.addTextEx(text, {"class":"warning"})
            self.main.endAnchor()
            self.main.newline()
            self.index.startNoBreak()
            self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"warning"})
            self.index.endNoBreak()
            self.index.newline()
        elif flag == self.LOG_ERROR:
            ref = self.getAnchor()
            self.main.startAnchor(ref)
            self.main.addTextEx(text, {"class":"error"})
            self.main.endAnchor()
            self.main.newline()
            self.index.startNoBreak()
            self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"error"})
            self.index.endNoBreak()
            self.index.newline()
        elif flag == self.LOG_HEADING:
            ref = self.getAnchor()
            self.main.startAnchor(ref)
            self.main.addTextEx(text, {"class":"heading"})
            self.main.endAnchor()
            self.main.newline()
            self.index.startNoBreak()
            self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"heading"})
            self.index.endNoBreak()
            self.index.newline()
        elif flag == self.LOG_HINT:
            ref = self.getAnchor()
            self.main.startAnchor(ref)
            self.main.addTextEx(text, {"class":"hint"})
            self.main.endAnchor()
            self.main.newline()
            self.index.startNoBreak()
            self.index.addRef(text, url="protocol.htm", anchor=ref, attributes = {"class":"hint"})
            self.index.endNoBreak()
            self.index.newline()

    def log(self, text, flag):
        if flag == self.LOG_DEBUG:
            if self.debug == 1:
                self.main.addTextEx(text, {"class":"debug"})
                self.main.newline()
        elif flag == self.LOG_MESSAGE:
            self.main.addTextEx(text, {"class":"message"})
            self.main.newline()
        elif flag == self.LOG_WARNING:
            self.main.addTextEx(text, {"class":"warning"})
            self.main.newline()
        elif flag == self.LOG_ERROR:
            self.main.addTextEx(text, {"class":"error"})
            self.main.newline()
        elif flag == self.LOG_HEADING:
            self.main.addTextEx(text, {"class":"heading"})
            self.main.newline()
        elif flag == self.LOG_INFO:
            self.main.addTextEx(text, {"class":"info"})
            self.main.newline()

    def brIndex(self):
        self.index.newline()

    def brMain(self):
        self.main.newline()

    def br(self):
        self.main.newline()
        self.index.newline()

    def hlineIndex(self):
        self.index.hline()

    def hlineMain(self):
        self.main.hline()