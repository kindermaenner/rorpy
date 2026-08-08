#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: commands.py,v 2.18 2005/05/12 22:15:07 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Klasse Command(object):
#    Oberklasse der Rorqual-Befehle. Fuer jeden Befehl gibt es eine davon
#    abgeleitete Klasse, in der die Funktionen __init__, parse, execute und
#    checkSemantik implementiert sein muessen.
#
#    def __init__(self, line):
#        line - Zeile des Zugs, in der der Befehl steht
#        Initialisierung des Befehls.
#
#    def __str__(self):
#        Gibt die Syntax des Befehls zurueck.
#
#    def parse(self):
#        Funktion zum Parsen des Befehls.
#
#    def execute(self, unit, region, aw):
#        unit   - Einheit, der dieser Befehl erteilt wurde
#        region - Region, in der die Einheit steht
#        aw     - das RorAW-Objekt
#        Funktion zum Ausfuehren des Befehls.
#
#    def checkSemantik(self, unit):
#        unit   - Einheit, der dieser Befehl erteilt wurde
#        Die Funktion prueft die Semantik des Befehls.
#
# def createCommand(name, line):
#    name - Name des zu erzeugenden Befehls
#    line - Zeile, aus der der Befehl gelesen wurde
#    Diese Funktion liefert das Objekt des uebergebenen Befehls zurueck.
#    Es koennen nur Objekte der Befehle erzeugt werden, die im dicht
#    _commands vorhanden sind.
#
# ---------------------------------------------------------------------------

from util.messages import *
from rorparserutil import NewlineException, GetEntry, ReadNewline, ReadUntilNL, PushbackEntry
from rorscanner    import *
from references    import RefObject, RefParty, RefProduct, RefTalent, RefUnit
from objects       import *
from constants     import *
from types         import TypeAmount, TypeDirection, TypeStatus, TypeReligion, TypeFlag
from kb            import GetKB

__all__ = ["createCommand"]

class Command(object):
    def __init__(self, line):
        self.output     = []
        self.parameters = []
        self.fLong      = None
        self.syntax     = "unbekannt"
        self.line       = line
        self.executed   = False
        self.durable    = False

    def __str__(self):
        return self.syntax

    def parse(self):
        self.output += [Message(CAT_ERR, 38, line = self.line)]
        return

    def execute(self, unit, region, aw):
        self.executed = True
        return

    def checkSemantik(self, unit):
        for p in self.parameters:
            if p.__class__.__name__ in ["Reference", "RefUnit", "RefObject", "RefTalent", "RefProduct", "RefParty"]:
                result = p.resolve(unit)
                if result != 0:
                    self.output += [Message(CAT_ERR, result[0], result[1], self.line)]

class Comment(Command):
    def __init__(self, line):
        super(Comment, self).__init__(line)
        self.syntax = None
        self.line = line
        self.executed = True

    def parse(self):
        try:
            (type, value) = GetEntry()
            self.parameters += [value]
        except NewlineException:
            return True

class CommandAdresse(Command):
    def __init__(self, line):
        super(CommandAdresse, self).__init__(line)
        self.syntax = 'adresse "meine@adresse.de"'

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_STRING):
                self.parameters += [value]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("ADRESSE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("ADRESSE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("ADRESSE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        aw.email = self.parameters[0]
        return

class CommandArbeite(Command):
    def __init__(self, line):
        super(CommandArbeite, self).__init__(line)
        self.fLong  = True
        self.syntax = "arbeite"
        self.name = "arbeite"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("ARBEITE"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        maxIncomeRegion = unit.region.IncomeWork - unit.region.IncomeWorkUsed
        maxIncomeUnit   = unit.region.wages * unit.getPersons()
        region.IncomeWorkUsed += maxIncomeUnit
        if (maxIncomeRegion >= maxIncomeUnit): # Ist noch genuegend Arbeitssilber fuer alle Personen der Einheit da?
            unit.addProduct(ID_P_SILB, maxIncomeUnit)
            self.output += [Message(CAT_INFO, 150, para = (maxIncomeUnit, "Arbeit"))]
        elif (maxIncomeRegion > 0): # Ist ueberhaupt noch Arbeitssilber in der Region uebrig?
            unit.addProduct(ID_P_SILB, maxIncomeRegion)
            self.output += [Message(CAT_WARN, 108, line = self.line)]
            self.output += [Message(CAT_INFO, 150, (maxIncomeRegion, "Arbeit"))]
        else:
            self.output += [Message(CAT_WARN, 109, line = self.line)]
        region.ppTrade = True # Handels-PPs an der Region merken
        return

class CommandAttackiere(Command):
    def __init__(self, line):
        super(CommandAttackiere, self).__init__(line)
        self.syntax = "attackiere <Zieleinheit(en)>"

    def parse(self):
        try:
            while(True):
                ref = RefUnit()
                if ref.parse():
                    self.parameters += [ref]
                else:
                    self.output += [Message(CAT_ERR, 7, ("ATTACKIERE"), self.line)]
                    ReadUntilNL()
                    return False
        except NewlineException:
            if (len(self.parameters) != 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("ATTACKIERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if not unit.isArmed(aw):
            self.output += [Message(CAT_WARN, 110, line = self.line)]
        return

class CommandAusbauen(Command):
    def __init__(self, line):
        super(CommandAusbauen, self).__init__(line)
        self.syntax = "ausbauen"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("AUSBAUEN"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.object.kbobj is None):
            self.output += [Message(CAT_ERR, 12, (""), self.line)]
            return
        if unit.object.underConstruction: # Das Gebaeude darf sich nicht schon im Bau befinden.
            self.output += [Message(CAT_ERR, 20, line = self.line)]
            return
        if not unit.object.isExpandable(): # Das Gebaeude muss ausbaubar sein.
            self.output += [Message(CAT_ERR, 21, line = self.line)]
            return
        if (unit.object.sortedUnits[0].partynumber != aw.partynumber): # Partei muss Besitzer des Gebaeudes sein
            self.output += [Message(CAT_ERR, 22, line = self.line)]
            return
        unit.object.kbobj = GetKB().findBuilding(unit.object.kbobj.expandableTo.key)
        unit.object.initValuesFromKB()
        unit.object.underConstruction = True # Gebaeude als im Bau kennzeichnen
        return

class CommandAusschiffen(Command):
    def __init__(self, line):
        super(CommandAusschiffen, self).__init__(line)
        self.syntax = "ausschiffen"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("AUSSCHIFFEN"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.fleetNumber == 0):
            self.output += [Message(CAT_ERR, 23, line = self.line)]
            return
        region.getFleet(unit.fleetNumber).disembark(unit)
        index = unit.object.sortedUnits.index(unit)
        while (unit.object.sortedUnits[index - 1].fleetNumber != 0):
            unit.object.sortedUnits.remove(unit)
            unit.object.sortedUnits.insert((index - 1), unit)
            index -= 1
        return

class CommandBaue(Command):
    def __init__(self, line):
        super(CommandBaue, self).__init__(line)
        self.fLong  = True
        self.syntax = "baue [Objekttyp]"
        self.name = "baue"

    def parse(self):
        try:
            ref = RefObject()
            if ref.parse():
                if ref.id != None:
                    self.output += [Message(CAT_ERR, 7, ("BAUE"), self.line)]
                else:
                    self.parameters += [ref]
                    dir = TypeDirection()
                    if dir.parse():
                        self.parameters += [ref]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("BAUE"), self.line)]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BAUE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BAUE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            return True

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = "baue"
        if (len(self.parameters) == 0):
            # Wenn Parameterlos: Pruefe, ob Einheit in einem unfertigen Objekt stehtt
            if not unit.object.underConstruction:
                self.output += [Message(CAT_ERR, 24, line = self.line)]
                return
            if (unit.object.kbobj is None): # keine Objektspec
                self.output += [Message(CAT_ERR, 12, (""), self.line)]
                return
            # Kann Einheit das Objekt errichten?
            if not unit.canBuild(unit.object):
                self.output += [Message(CAT_ERR, 25, line = self.line)]
                return
            # Baumaterialverbrauch berechnen
            (amount, productList) = unit.getBuildingMaterial(unit.object)
            # Hat Einheit ueberhaupt Material?
            if (amount == 0):
                self.output += [Message(CAT_ERR, 26, line = self.line)]
                return
            # Wieviel Material braucht es noch, um das Gebaeude fertig zu stellen?
            if (amount > (unit.object.maxSize - unit.object.size)):
                amount = (unit.object.maxSize - unit.object.size)
            # Baumaterialverbrauch von Einheit abziehen, neue Groesse berechnen
            for p in productList:
                unit.delProduct(p.getKey(), (p.amount * amount))
            # neue Groesse des Objekts anpassen
            unit.object.size += amount
            # Handels-PP hinzufuegen
            unit.region.ppTrade = True
            return
        newObject = self.parameters[0].obj
        if newObject.kbobj.production is None:
            self.output += [Message(CAT_ERR, 148, (newObject.getKeyAsString()), GetLine())]
            return
        if newObject.hasType(TYPE_O_CITY):
            # Feststellen, ob das Gebaeude schon existiert
            for object in unit.region.sortedObjects:
                if (object.kbobj != None):
                    if (object.getKey() == newObject.getKey()):
                        self.output += [Message(CAT_ERR, 27, line = self.line)]
                        return
                elif (object.getKey() != 0):
                    self.output += [Message(CAT_HINT, 39, (object.getKey()), self.line)]
        elif newObject.hasType(TYPE_O_PRODUCTION):
            # Feststellen, ob das Gebaeude schon existiert
            for object in unit.region.sortedObjects:
                if (object.kbobj != None):
                    if (object.getKey() == newObject.getKey()):
                        self.output += [Message(CAT_ERR, 27, line = self.line)]
                        return
                elif (object.getKey() != 0):
                    self.output += [Message(CAT_HINT, 39, (object.getKey()), self.line)]
            # Feststellen, ob das Gebaeude Sinn macht
            if newObject.favour != {}:
                products = newObject.favour.values()
                regionHasProduct = False
                for p in products:
                    if unit.region.producable.has_key(p.getKey()):
                        regionHasProduct = True
                if not regionHasProduct:
                    self.output += [Message(CAT_HINT, 41, line = self.line)]
                    return
        # Schaun, ob die Einheit das Gebaeude bauen kann.
        if not unit.canBuild(newObject):
            self.output += [Message(CAT_ERR, 25, line = self.line)]
            return
        # Baumaterialverbrauch berechnen
        (amount, amountPerPiece) = unit.getBuildingMaterial(newObject)
        # Schaun, ob Baumaterial vorhanden ist.
        if (amount == 0):
            self.output += [Message(CAT_ERR, 26, line = self.line)]
            return
        # Wieviel Material braucht es noch, um das Gebaeude fertig zu stellen?
        if (amount > (newObject.maxSize - newObject.size)):
            amount = (newObject.maxSize - newObject.size)
        # Baumaterialverbrauch von Einheit abziehen, neue Groesse berechnen
        for p in amountPerPiece:
            unit.delProduct(p.getKey(), (p.amount * amount))
        # neue Groesse des Objekts anpassen
        newObject.size = amount
        # neues Objekt der Region hinzufuegen
        newObject.region = unit.region
        newObject.id = len(unit.region.sortedObjects)
        unit.region.sortedObjects += [newObject]
        # Einheit aus dem jetzigen Objekt entfernen und in das neue Objekt stellen
        unit.object.delUnit(unit)
        newObject.addUnit(unit)
        # Handelspp hinzufuegen
        unit.region.ppTrade = True
        return

class CommandBeanspruche(Command):
    def __init__(self, line):
        super(CommandBeanspruche, self).__init__(line)
        self.syntax = "beanspruche <Anzahl> Silber"

    def parse(self):
        try:
            ref = TypeAmount()
            if ref.parse():
                if not ref.hasDefinedValue():
                    self.output += [Message(CAT_ERR, 7, ("BEANSPRUCHE"), self.line)]
                else:
                    self.parameters += [ref]
                ref = RefProduct()
                if ref.parse():
                    self.parameters += [ref]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("BEANSPRUCHE"), self.line)]
                else:
                    self.output += [Message(CAT_ERR, 7, ("BEANSPRUCHE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BEANSPRUCHE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BEANSPRUCHE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        silbAmount = self.parameters[0].value
        if (aw.treasury < silbAmount):
            self.output += [Message(CAT_HINT, 42, line = self.line)]
            silbAmount = aw.treasury
        # Silber vom Reichsschatz abziehen
        aw.treasury -= silbAmount
        # Silber der Einheit geben
        unit.addProduct(ID_P_SILB, silbAmount)
        return

class CommandBefoerdere(Command):
    def __init__(self, line):
        super(CommandBefoerdere, self).__init__(line)
        self.syntax = "befoerdere <Einheitsnummer>"

    def parse(self):
        try:
            ref = RefUnit()
            if ref.parse():
                self.parameters += [ref]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("BEFOERDERE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BEFOERDERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BEFOERDERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Einheit darf sich nicht im Umland befinden
        if unit.object.isHinterland():
            self.output += [Message(CAT_ERR, 137, line = self.line)]
            return
        # Einheit muss Besitzer des Gebaeudes sein
        if (unit.object.sortedUnits.index(unit) != 0):
            self.output += [Message(CAT_ERR, 22, line = self.line)]
            return
        # Einheit muss sich im Inneren des Objekts befinden
        if (unit.object.getKey() != self.parameters[0].obj.object.getKey()):
            self.output += [Message(CAT_ERR, 43, line = self.line)]
            return
        # eigene Einheiten oder freundliche Einheiten koennen befoerdert werden
        if (self.parameters[0].obj.partynumber != aw.partynumber):
            self.output += [Message(CAT_HINT, 125, line = self.line)]
        unit.object.sortedUnits.remove(self.parameters[0].obj)
        unit.object.sortedUnits.insert(0, self.parameters[0].obj)
        return

class CommandBehalte(Command):
    def __init__(self, line):
        super(CommandBehalte, self).__init__(line)
        self.syntax = "behalte <alle|alles|Anzahl> [Gegenstand]"

    def parse(self):
        try:
            ref = TypeAmount()
            if ref.parse():
                self.parameters += [ref]
                ref = RefProduct()
                try:
                    if ref.parse():
                        self.parameters += [ref]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("BEHALTE"), self.line)]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BEHALTE"), self.line)]
                except NewlineException:
                    return True
            else:
                self.output += [Message(CAT_ERR, 7, ("BEHALTE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BEHALTE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        amount = self.parameters[0].value
        if (len(self.parameters) == 1):
            if (amount == -1) or (amount == -2):
                unit.setFlag(FLAG_KEEP_ALL,1)
                return
        # Produkt bei der Einheit suchen
        productKey = self.parameters[1].obj.getKey()
        # Wenn die Einheit das Produkt nicht besitzt, ein neues Produkt anlegen
        if not unit.inventory.has_key(productKey):
            unit.addProduct(productKey, 0)
        unit.inventory[productKey].keepAmount = amount
        return

class CommandBelagere(Command):
    def __init__(self, line):
        super(CommandBelagere, self).__init__(line)
        self.syntax = "belagere wall norden 30" # KeyWord, Direction, amount
        self.fLong = True
        self.verbrauch = 0
        self.name = "belagere"

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_IDENT) or (type == TOK_KEYWORD):
                if (value != "wall"):
                    self.output += [Message(CAT_ERR, 7, ("BELAGERE"), self.line)]
                else:
                    dir = TypeDirection()
                    if dir.parse():
                        self.parameters += [dir]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BELAGERE"), self.line)]
                        ReadUntilNL()
                        return False
                    (type, value) = GetEntry()
                    if (type == TOK_NUMBER):
                        self.parameters += [int(value)]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BELAGERE"), self.line)]
                        ReadUntilNL()
                        return False
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("BELAGERE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BELAGERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BELAGERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        if not unit.inventory.has_key(ID_P_BG):
            self.output += [Message(CAT_ERR, 44, line = self.line)]
            return
        if (unit.inventory[ID_P_BG].amount < self.parameters[1]):
            self.output += [Message(CAT_HINT, 45, line = self.line)]
        unit.delProduct(ID_P_BG, self.parameters[1])
        return

class CommandBenenne(Command):
    def __init__(self, line):
        super(CommandBenenne, self).__init__(line)
        self.syntax = "benenne <Objekt> \"neuer Name\""
        self.target = None
        self.keywords = {"einheit" : 1, "objekt" : 2, "region" : 3, "ansiedlung" : 4, "partei" : 5, "kontakt" : 6}
        self.name = None

    def parse(self):
        # Die Namen koennen beliebig lang sein, sie duerfen jedoch keine Klammern enthalten und keine Steuerzeichen.
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                try:
                    self.target = self.keywords[value]
                    (type, value) = GetEntry()
                    if type == TOK_STRING:
                        self.name = value[1:-1]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("BENENNE"), self.line)]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BENENNE"), self.line)]
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("BENENNE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BENENNE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BENENNE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.target == 1):
            unit.name = self.name
            return
        elif (self.target == 2):
            # benennende Einheit muss Besitzer des Objekts sein
            if (unit.object.sortedUnits.index(unit) != 0):
                self.output += [Message(CAT_ERR, 22, line = self.line)]
                return
            unit.object.name = self.name
            return
        elif (self.target == 3):
            # eigenen Region darf benannt werden
            if (unit.region.ownerNumber != aw.partynumber):
                self.output += [Message(CAT_ERR, 46, line = self.line)]
                return
            unit.region.name = self.name
            return
        elif (self.target == 4):
            # eigene Ansiedlung darf benannt werden
            if (unit.region.ownerNumber != aw.partynumber):
                self.output += [Message(CAT_ERR, 46, line = self.line)]
                return
            if (unit.region.homestead is None):
                self.output += [Message(CAT_ERR, 47, line = self.line)]
                return
            unit.region.homestead.name = self.name
            return
        elif (self.target == 5):
            aw.partyname = self.name
            return
        aw.contact == self.name
        return

class CommandBeschreibe(Command):
    def __init__(self, line):
        super(CommandBeschreibe, self).__init__(line)
        self.syntax = "beschreibe <Objekt> \"neue Beschreibung\""
        self.target = None
        self.keywords = {"einheit" : 1, "objekt" : 2, "gebaeude" : 2}
        self.text = None

    def parse(self):
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                try:
                    self.target = self.keywords[value]
                    (type, value) = GetEntry()
                    if type == TOK_STRING:
                        self.text = [value[1:-1]]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("BESCHREIBE"), self.line)]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BESCHREIBE"), self.line)]
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("BESCHREIBE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BESCHREIBE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BESCHREIBE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.target == 1):
            unit.description = self.text
            return
        # beschreibende Einheit muss Besitzer des Objekts sein
        if (unit.object.sortedUnits.index(unit) != 0):
            self.output += [Message(CAT_ERR, 22, line = self.line)]
            return
        unit.object.description = self.text
        return

class CommandBesiedeln(Command):
    def __init__(self, line):
        super(CommandBesiedeln, self).__init__(line)
        self.fLong         = True
        self.syntax        = "besiedeln"
        self.name = "besiedeln"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("BESIEDELN"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Die Einheit darf noch keinen anderen langen Befehl haben
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        # Die Rasse in der Region muss ungleich der Stammrasse sein
        if (unit.region.race == aw.optedRace):
            self.output += [Message(CAT_ERR, 48, line = self.line)]
            return
        # Rasse der Einheit muss der Stammrasse entsprechen
        if (unit.getRace().plural != aw.optedRace):
            self.output += [Message(CAT_ERR, 49, line = self.line)]
            return
        # Es darf keine andere Partei in der Region besiedeln
        allUnits = unit.region.getAllUnits()
        for u in allUnits:
            if u.partynumber != aw.partynumber:
                if u.settlingProgress > 0:
                    self.output += [Message(CAT_ERR, 50, line = self.line)]
        # Eine andere Einheit besiedelt die Region schon
        if region.isSettled:
            self.output += [Message(CAT_ERR, 51, line = self.line)]
            return
        region.isSettled = True
        # Die Einheit darf nicht getarnt sein
        if not unit.getFlag(FLAG_REVEAL_PARTY):
            self.output += [Message(CAT_ERR, 52, line = self.line)]
            return
        # Die Einheit muss genuegend Personen enthalten
        if (region.homestead != None):
            if unit.getPersons() < 100:
                self.output += [Message(CAT_ERR, 53, line = self.line)]
        else:
            if unit.getPersons() < 25:
                self.output += [Message(CAT_ERR, 53, line = self.line)]
        return

class CommandBetrete(Command):
    def __init__(self, line):
        super(CommandBetrete, self).__init__(line)
        self.syntax = "betrete <Objektnummer>"

    def parse(self):
        try:
            ref = RefObject()
            if ref.parse():
                self.parameters += [ref]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("BETRETE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BETRETE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BETRETE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Warnung, wenn die eigene Partei ncht Besitzer des Gebaeudes ist.
        if (unit.object.sortedUnits[0].partynumber != aw.partynumber):
            self.output += [Message(CAT_HINT, 126, line = self.line)]
        # Wenn die Einheit getarnt ist, wird sie nun sichtbar
        if unit.getFlag(FLAG_MASKED):
            unit.setFlag(FLAG_MASKED,0)
            unit.setFlag(FLAG_REVEAL_UNIT,1)
            self.output += [Message(CAT_HINT, 127, line = self.line)]
        # Einheit aus dem aktuellen Objekt entfernen
        unit.object.delUnit(unit)
        # Einheit in das neue Objekt stellen
        self.parameters[0].obj.addUnit(unit)
        return

class CommandBewache(Command):
    def __init__(self, line):
        super(CommandBewache, self).__init__(line)
        self.syntax = "bewache 0|1"

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.parameters += [f]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("BEWACHE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BEWACHE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BEWACHE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if not self.parameters[0].value:
            unit.setFlag(FLAG_GUARD, 0)
            return
        # Hat die Einheit das Flag schon gesetzt?
        if unit.getFlag(FLAG_GUARD) and self.parameters[0].value:
            return
        # Einheit muss bewaffnet sein, um bewachen zu koennen
        if not unit.isArmed(aw):
            self.output += [Message(CAT_ERR, 54, line = self.line)]
            return
        # Feststellen, ob eine andere Partei die Region bewacht
        if unit.region.isGuarded(aw):
            self.output += [Message(CAT_HINT, 128, line = self.line)]
        # Loescht, wenn vorhanden, das Vermeide-Flag
        if unit.getFlag(FLAG_AVOID):
            unit.setFlag(FLAG_AVOID,0)
            self.output += [Message(CAT_HINT, 129, line = self.line)]
        # Setzt das Bewache-Flag
        unit.setFlag(FLAG_GUARD,1)
        return

class CommandBezahle(Command):
    def __init__(self, line):
        super(CommandBezahle, self).__init__(line)
        self.syntax = "bezahle <Anzahl> <Gegenstand>"

    def parse(self):
        try:
            m = TypeAmount()
            if m.parse():
                if not ref.hasDefinedValue():
                    self.output += [Message(CAT_ERR, 7, ("BEZAHLE"), self.line)]
                else:
                    self.parameters += [m]
                    ref = RefProduct()
                    if ref.parse():
                        self.parameters += [ref]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("BEZAHLE"), self.line)]
                    else:
                        self.output += [Message(CAT_ERR, 7, ("BEZAHLE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("BEZAHLE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BEZAHLE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        payAmount  = self.parameters[0].value
        payProduct = self.parameters[1].obj.getKey()
        # Einheit muss den Gegenstand besitzen
        if not unit.inventory.has_key(payProduct):
            self.output += [Message(CAT_ERR, 55, (payProduct), self.line)]
            return
        # Einheit muss den Gegenstand in ausreichender Menge besitzen
        if (unit.inventory[payProduct].amount < payAmount):
            self.output += [Message(CAT_ERR, 56, (payProduct), self.line)]
            payAmount = unit.inventory[payProduct].amount
        # Menge des Gegenstands abziehen
        unit.delProduct(payProduct, payAmount)
        return

class CommandBotschaft(Command):
    def __init__(self, line):
        super(CommandBotschaft, self).__init__(line)
        self.syntax = "botschaft Einheitsnummer|region \"Botschaftstext\""
        self.regionsbotschaft = False

    def parse(self):
        ok = True
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                if value == "region":
                    self.regionsbotschaft = True
                else:
                    self.output += [Message(CAT_ERR, 7, ("BOTSCHAFT"), self.line)]
                    ok = False
            else:
                PushbackEntry((type, value))
                refUnit = RefUnit()
                if refUnit.parse():
                    self.regionsbotschaft = False
                    self.parameters += [refUnit]
                else:
                    self.output += [Message(CAT_ERR, 7, ("BOTSCHAFT"), self.line)]
                    ok = False
            if ok:
                # Naechsten Parameter
                (type, value) = GetEntry()
                if type == TOK_STRING:
                    self.parameters += [value[1:-1]]
                    return True
                else:
                    self.output += [Message(CAT_ERR, 7, ("BOTSCHAFT"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("BOTSCHAFT"), self.line)]
            return False

class CommandDauersteuer(Command):
    def __init__(self, line):
        super(CommandDauersteuer, self).__init__(line)
        self.syntax = "dauersteuer 0|1"
        self.value = False

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.value = f.value
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("DAUERSTEUER"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("DAUERSTEUER"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("DAUERSTEUER"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Hat die Einheit das Flag schon gesetzt?
        if unit.getFlag(FLAG_TAXING) and self.value:
            return
        # Setzt das Dauersteuer-Flag
        unit.setFlag(FLAG_TAXING, self.value)
        # Treibebefehl entsprechen hinzufuegen oder entfernen
        if self.value:
            unit.addCommand(CommandTreibe(0))
        else:
            unit.delCommand(CommandTreibe(0))
        return

class CommandEinheit(Command):
    def __init__(self, line):
        super(CommandEinheit, self).__init__(line)
        self.syntax = "einheit <Einheitsnummer>"

    def parse(self):
        try:
            ref = RefUnit()
            if ref.parse():
                self.parameters += [ref]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("EINHEIT"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("EINHEIT"), self.line)]
            ReadUntilNL()
        except NewlineException:
            if (len(self.parameters) == 1):
                return True
            self.output += [Message(CAT_ERR, 8, ("EINHEIT"), self.line)]
            return False

class CommandEinschiffen(Command):
    def __init__(self, line):
        super(CommandEinschiffen, self).__init__(line)
        self.syntax = "einschiffen  [<Einheitsnummer>]"

    def parse(self):
        try:
            ref = RefUnit()
            if ref.parse():
                self.parameters += [ref]
                if ReadNewline():
                    return True
            else:
                self.output += [Message(CAT_ERR, 7, ("EINSCHIFFEN"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            if (len(self.parameters) == 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("EINSCHIFFEN"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.fleetNumber != 0):
            # Pruefen, ob der Kapitain der Flotte nochmals eine Flotte bilden soll:
            if ((len(self.parameters) == 0) or (self.parameters[0].obj == unit)) and (unit.fleetNumber == unit.getKey()):
                self.output += [Message(CAT_ERR, 159, line = self.line)]
                return
            region.getFleet(unit.fleetNumber).disembark(unit)
        if (len(self.parameters) == 0) or (self.parameters[0].obj == unit):
            hasShip = False
            items = unit.inventory.values()
            for i in items:
                if i.hasType(TYPE_P_SHIP):
                    hasShip = True
                    break
            if not hasShip:
                self.output += [Message(CAT_ERR, 58, line = self.line)]
                return
            id = unit.getKey()
            region.fleets += [RorFleet(region, id)]
        else:
            id = self.parameters[0].obj.getKey()
        if (region.getFleet(id) is None):
            self.output += [Message(CAT_ERR, 152, (id), self.line)]
            return
        region.getFleet(id).embark(unit)
        return

class CommandEinzeln(Command):
    def __init__(self, line):
        super(CommandEinzeln, self).__init__(line)
        self.syntax = "einzeln 0|1"
        self.value = False

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.value = f.value
            else:
                self.output += [Message(CAT_ERR, 7, ("EINZELN"), self.line)]
            if ReadNewline():
                return True
            else:
                self.output += [Message(CAT_ERR, 8, ("EINZELN"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("EINZELN"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        unit.setFlag(FLAG_SINGLE, self.value)
        return

class CommandEnde(Command):
    def __init__(self, line):
        super(CommandEnde, self).__init__(line)
        self.syntax = "ende"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("ENDE"), self.line)]
        ReadUntilNL()
        return False

class CommandErklaere(Command):
    def __init__(self, line):
        super(CommandErklaere, self).__init__(line)
        self.syntax = "erklaere Parteinummer|standard [politischer Status]"
        self.standard = False

    def parse(self):
        ok = True
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                if value == "standard":
                    self.standard = True
                else:
                    self.output += [Message(CAT_ERR, 7, ("ERKLAERE"), self.line)]
                    ok = False
            else:
                PushbackEntry((type, value))
                ref = RefParty()
                if ref.parse():
                    self.parameters += [ref]
                else:
                    self.output += [Message(CAT_ERR, 7, ("ERKLAERE"), self.line)]
                    ok = False
            if ok:
                if not self.standard:
                    if ReadNewline():
                        return True
                status = TypeStatus()
                if status.parse():
                    self.parameters += [status]
                    return True
                else:
                    self.output += [Message(CAT_ERR, 7, ("ERKLAERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            if not self.standard:
                self.output += [Message(CAT_ERR, 8, ("ERKLAERE"), self.line)]
                return False
            else:
                return True

class CommandErobere(Command):
    def __init__(self, line):
        super(CommandErobere, self).__init__(line)
        self.fLong         = True
        self.syntax        = "erobere [neutral]"
        self.neutral = False
        self.name = "erobere"

    def parse(self):
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                if value == "neutral":
                    self.neutral = True
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("EROBERE"), self.line)]
                else:
                    self.output += [Message(CAT_ERR, 7, ("EROBERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            return True

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        # Einheit muss bewaffnet sein
        if not unit.isArmed(aw):
            self.output += [Message(CAT_ERR, 59, line = self.line)]
            return
        # Die Einheit muss genuegend Personen enthalten
        if unit.getPersons() < 100:
            self.output += [Message(CAT_ERR, 60, line = self.line)]
        if (len(self.parameters) == 0): # zum eigenen Reichsgebiet
            if (unit.region.ownerNumber == aw.partynumber):
                self.output += [Message(CAT_ERR, 61, line = self.line)]
                return
        else: # neutral
            if unit.region.ownerNumber == 0:
                self.output += [Message(CAT_ERR, 62, line = self.line)]
                return
        allUnits = region.getAllUnits()
        for u in allUnits:
            if (u.conqueringProgress > 0):
                if u == unit:
                    continue
                if (u.partynumber == aw.partynumber):
                    self.output += [Message(CAT_ERR, 63, line = self.line)]
                else:
                    self.output += [Message(CAT_ERR, 138, line = self.line)]
                return
        region.isConquered = True
        return

class CommandFoerdere(Command):
    def __init__(self, line):
        super(CommandFoerdere, self).__init__(line)
        self.syntax   = "foerdere region|ansiedlung"
        self.keywords = {"region": 1, "ansiedlung": 2}
        self.target   = 0

    def parse(self):
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                try:
                    self.target = self.keywords[value]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("FOERDERE"), self.line)]
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("FOERDERE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("FOERDERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("FOERDERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.target == 1): # Region wird gefoerdert
            if region.isSupported:
                self.output += [Message(CAT_ERR, 64, line = self.line)]
                return
            if (region.maxPopulation == region.population):
                self.output += [Message(CAT_ERR, 111, line = self.line)]
                return
            missingMoney = neededMoney = (region.population + 1) * 3000
        else: # Ansiedlung wird gefoerdert
            if (region.homestead is None):
                self.output += [Message(CAT_ERR, 47, line = self.line)]
                return
            if region.homestead.isSupported:
                self.output += [Message(CAT_ERR, 65, line = self.line)]
                return
            missingMoney = neededMoney = (region.homestead.size + 1) * 5000
        if unit.inventory.has_key(ID_P_SILB) and (unit.inventory[ID_P_SILB].amount >= neededMoney):
            unit.delProduct(ID_P_SILB, neededMoney)
        else: # Einheit hat nicht genuegend Silber, um zu foerdern --> in der Region schaun
            if unit.inventory.has_key(ID_P_SILB):
                missingMoney -= unit.inventory[ID_P_SILB].amount
            # Schaun, ob in der Region genuegend Silber vorhanden ist
            ownUnits = region.getUnitsFromPartyAsList(aw.partynumber)
            for u in ownUnits:
                if not u.getFlag(FLAG_SUPPLY):
                    continue
                if u.isSacrificed or u.isSurrendered:
                    continue
                if u.inventory.has_key(ID_P_SILB):
                    missingMoney -= u.inventory[ID_P_SILB].amount
            if (missingMoney > 0):
                # In der Region ist nicht genuegend Silber zum Foerdern vorhanden
                self.output += [Message(CAT_ERR, 66, line = self.line)]
                return
            missingMoney = neededMoney
            # Evtl. vorhandenes Silber der Einheit ausgeben
            if unit.inventory.has_key(ID_P_SILB):
                missingMoney -= unit.inventory[ID_P_SILB].amount
                unit.delProduct(ID_P_SILB, unit.inventory[ID_P_SILB].amount)
            # Restliches Silber aus der Region holen
            for u in ownUnits:
                if not u.getFlag(FLAG_SUPPLY):
                    continue
                if u.isSacrificed or u.isSurrendered:
                    continue
                if u.inventory.has_key(ID_P_SILB):
                    deletable = (u.inventory[ID_P_SILB].amount - u.inventory[ID_P_SILB].keepAmount)
                    if (missingMoney < deletable):
                        deletable = missingMoney
                    u.delProduct(ID_P_SILB, deletable)
                    missingMoney -= deletable
                if (missingMoney <= 0):
                    break
        # Region bzw. Ansiedlung als gefoerdert kennzeichnen
        if (self.target == 1):
            region.isSupported = True
        else:
            region.homestead.isSupported = True
        return

class CommandGib(Command):
    def __init__(self, line):
        super(CommandGib, self).__init__(line)
        self.syntax  = "gib <Einheitsnummer> <Anzahl> <Gegenstand>"
        self.surrenderUnit = False

    def parse(self):
        try:
            unit = RefUnit()
            if unit.parse():
                self.parameters += [unit]
                (type, value) = GetEntry()
                if ((type == TOK_KEYWORD) and (value == "einheit")):
                    self.surrenderUnit = True
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("GIB"), self.line)]
                        return False
                PushbackEntry((type, value))
                menge = TypeAmount()
                if menge.parse():
                    self.parameters += [menge]
                    produkt = RefProduct()
                    if produkt.parse():
                        self.parameters += [produkt]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("GIB"), self.line)]
                            return False
            self.output += [Message(CAT_ERR, 7, ("GIB"), self.line)]
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("GIB"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        targetUnit = self.parameters[0].obj

        if self.surrenderUnit:
            items = unit.inventory.values()

            # Einheit wird fremder Partei uebergeben
            if (unit.partynumber != targetUnit.partynumber):
                unit.isSurrendered = True
                if unit.isLeader():
                    aw.quantityLeaders -= unit.getPersons()
                else:
                    aw.quantityRegulars -= unit.getPersons()
                for i in items:
                    unit.delProduct(i.getKey(), i.amount)
                return
            targetRace = targetUnit.getRace()
            # Einheit wird mit eigener Einheit fusioniert
            if (targetUnit.getKey() != 0) and not (targetRace is None) and (unit.getRace().getKey() != targetRace.getKey()): # Rasse muss stimmen
                self.output += [Message(CAT_ERR, 67, line = self.line)]
                return
            # Einheit hat Schiffe dabei, Schiffstypen duerfen in einer Einheit nicht gemischt werden
            if (targetUnit.getKey() != 0) and unit.hasProductType(TYPE_P_SHIP):
                for i in items:
                    if i.hasType(TYPE_P_SHIP):
                        shipType = i.getKey()
                        break
                targetItems = targetUnit.inventory.values()
                for i in targetItems:
                    if i.hasType(TYPE_P_SHIP):
                        if i.getKey() != shipType:
                            self.output += [Message(CAT_ERR, 68, line = self.line)]
                            return
                        break
            unit.isSurrendered = True
            for i in items:
                unit.delProduct(i.getKey(), i.amount)
                targetUnit.addProduct(i.getKey(), i.amount)
            targetPersons   = targetUnit.getPersons()
            unitPersons     = unit.getPersons()
            newPersonAmount = targetPersons + unitPersons
            talentsTarget   = targetUnit.talents.values()
            talents         = unit.talents.values()
            talentChange    = False
            for t in talentsTarget:
                tkey = t.getKey()
                talentpoints = (t.level * 5 + t.xp) * targetPersons
                if unit.talents.has_key(tkey):
                    talentpoints += (unit.talents[tkey].level * 5 + unit.talents[tkey].xp) * unitPersons
            for t in talents:
                if not targetUnit.talents.has_key(t.getKey()):
                    targetUnit.talents[t.getKey()] = t
            if not targetRace is None:
                targetUnit.output += [Message(CAT_WARN, 112, (unit.getKey()) , self.line)]
            return

        # Hat die gebende Einheit den Gegenstand in genannter Menge?
        product    = self.parameters[2].obj
        productKey = product.getKey()
        if not unit.inventory.has_key(productKey): # Einheit besitzt den zu uebergebenden Gegenstand gar nicht
            self.output += [Message(CAT_ERR, 55, (productKey), self.line)]
            return
        delAmount = unit.inventory[productKey].amount
        if self.parameters[1].hasDefinedValue():   # gibt nicht alles weg
            if (delAmount >= self.parameters[1].value): # Einheit besitzt mindestens soviel, wie sie weggeben soll
                delAmount = self.parameters[1].value
            else:                                       # Einheit besitzt weniger als sie weggeben soll
                self.output += [Message(CAT_ERR, 56, (productKey), self.line)]
        if (targetUnit.getKey() != 0) and product.hasType(TYPE_P_HUMANOID): # Rassen duerfen nicht gemischt werden
            targetRace = targetUnit.getRace()
            if  not(targetRace is None) and (targetRace.getKey() != productKey):
                self.output += [Message(CAT_ERR, 69, line = self.line)]
                return
        elif (targetUnit.getKey() != 0) and product.hasType(TYPE_P_SHIP):   # Schiffe duerfen nicht gemischt werden
            targetItems = targetUnit.inventory.values()
            for i in targetItems:
                if i.hasType(TYPE_P_SHIP) and (i.getKey() != productKey):
                    self.output += [Message(CAT_ERR, 68, line = self.line)]
                    return
        if product.hasType(TYPE_P_HUMANOID):
            if (unit.partynumber != targetUnit.partynumber):
                if unit.isLeader():
                    aw.quantityLeaders -= delAmount
                else:
                    aw.quantityRegulars -= delAmount
            else:
                talents = unit.talents.values()
                if (talents != []) and not (targetRace is None):
                    targetUnit.output += [Message(CAT_WARN, 112, (unit.getKey()) , self.line)]
                for t in talents:
                    if not targetUnit.talents.has_key(t.getKey()):
                        targetUnit.talents[t.getKey()] = t
        unit.delProduct(productKey, delAmount)
        targetUnit.addProduct(productKey, delAmount)
        return

class CommandGlaubenstendenz(Command):
    def __init__(self, line):
        super(CommandGlaubenstendenz, self).__init__(line)
        self.syntax       = "glaubenstendenz <Richtung>"

    def parse(self):
        try:
            glaube = TypeReligion()
            if glaube.parse():
                self.parameters += [glaube]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("GLAUBENSTENDENZ"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("GLAUBENSTENDENZ"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("GLAUBENSTENDENZ"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (aw.religion == "keine"):
            aw.religion = self.parameters[0].value
            return
        self.output += [Message(CAT_ERR, 70, line = self.line)]
        return

class CommandGott(Command):
    def __init__(self, line):
        super(CommandGott, self).__init__(line)
        self.syntax       = "gott <Goetterparteinummer>"

    def parse(self):
        try:
            gott = RefParty()
            if gott.parse():
                self.parameters += [gott]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("GOTT"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("GOTT"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("GOTT"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (aw.god == "keiner"):
            aw.god = self.parameters[0].id
            return
        self.output += [Message(CAT_ERR, 71, line = self.line)]
        return

class CommandHalte(Command):
    def __init__(self, line):
        super(CommandHalte, self).__init__(line)
        self.syntax = "halte 0|1"
        self.value = False

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.value = f.value
            else:
                self.output += [Message(CAT_ERR, 7, ("HALTE"), self.line)]
            if ReadNewline():
                return True
            else:
                self.output += [Message(CAT_ERR, 8, ("HALTE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("HALTE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        unit.setFlag(FLAG_HOLD_POSITION, self.value)
        return

class CommandHinten(Command):
    def __init__(self, line):
        super(CommandHinten, self).__init__(line)
        self.syntax = "hinten 0|1"
        self.value = False

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.value = f.value
            else:
                self.output += [Message(CAT_ERR, 7, ("HINTEN"), self.line)]
            if ReadNewline():
                return True
            else:
                self.output += [Message(CAT_ERR, 8, ("HINTEN"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("HINTEN"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        unit.setFlag(FLAG_BACKWARD, self.value)
        return

class CommandKampfzauber(Command):
    def __init__(self, line):
        super(CommandKampfzauber, self).__init__(line)
        self.syntax = "kampfzauber [<Zauber>]"

    def parse(self):
        try:
            produkt = RefTalent()
            if produkt.parse():
                self.parameters += [produkt]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("KAMPFZAUBER"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("KAMPFZAUBER"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            if (len(self.parameters) == 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("KAMPFZAUBER"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        newCombatSpell = self.parameters[0].obj
        if not unit.isMagician():
            self.output += [Message(CAT_ERR, 72, line = self.line)]
            return
        if not unit.talents.has_key(newCombatSpell.getKey()):
            self.output += [Message(CAT_ERR, 100, (newCombatSpell.getKeyAsString()), self.line)]
            return
        if not newCombatSpell.hasType(TYPE_T_COMBATSPELL):
            self.output += [Message(CAT_WARN, 113, (newCombatSpell.getKeyAsString()), self.line)]
        unit.combatSpell = newCombatSpell
        return

class CommandKaufe(Command):
    def __init__(self, line):
        super(CommandKaufe, self).__init__(line)
        self.syntax = "kaufe <Anzahl> <Gegenstand>"

    def parse(self):
        try:
            amount = TypeAmount()
            if amount.parse():
                self.parameters += [amount]
                product = RefProduct()
                if product.parse():
                    self.parameters += [product]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("KAUFE"), self.line)]
                        return False
            self.output += [Message(CAT_ERR, 7, ("KAUFE"), self.line)]
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("KAUFE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        product = self.parameters[1].obj
        if (self.parameters[1].name.lower() == "bauern") or (self.parameters[1].name.lower() == "bauer"):
            products = region.sales.values()
            for p in products:
                if p.hasType(TYPE_P_HUMANOID) and not (p.getKey() == ID_P_ANFU):
                    product = p
                    break
        productKey = product.getKey()
        if not region.sales.has_key(productKey): # Den Gegenstand kann man in der Region gar nicht kaufen
            self.output += [Message(CAT_ERR, 73, (productKey), self.line)]
            return
        if product.hasType(TYPE_P_HUMANOID):
            race = unit.getRace()
            if ((race != None) and (productKey != race.getKey())):
                self.output += [Message(CAT_ERR, 69, line = self.line)]
                return
        addAmount = region.sales[productKey].amount - region.sales[productKey].tradedAmount
        if (addAmount <= 0): # Produkt wurde schon komplett aufgekauft
            self.output += [Message(CAT_ERR, 74, (productKey), self.line)]
            return
        if self.parameters[0].hasDefinedValue():
            if (addAmount < self.parameters[0].value):
                self.output += [Message(CAT_ERR, 75, (productKey), self.line)]
            else:
                addAmount = self.parameters[0].value
        productFee = region.sales[productKey].cost
        missingMoney = neededMoney = addAmount * productFee
        if unit.inventory.has_key(ID_P_SILB) and (unit.inventory[ID_P_SILB].amount >= neededMoney):
            unit.delProduct(ID_P_SILB, neededMoney)
        else: # Einheit hat nicht genuegend Silber --> in der Region schaun
            if unit.inventory.has_key(ID_P_SILB):
                missingMoney -= unit.inventory[ID_P_SILB].amount
            # Schaun, ob in der Region genuegend Silber vorhanden ist
            ownUnits = region.getUnitsFromPartyAsList(aw.partynumber)
            for u in ownUnits:
                if not u.getFlag(FLAG_SUPPLY):
                    continue
                if u.isSacrificed or u.isSurrendered:
                    continue
                if u.inventory.has_key(ID_P_SILB):
                    missingMoney -= u.inventory[ID_P_SILB].amount
            if (missingMoney > 0):
                addAmount = int((neededMoney - missingMoney) / productFee)
                missingMoney = neededMoney = addAmount * productFee
                self.output += [Message(CAT_ERR, 160, (productKey), self.line)]
            else:
                missingMoney = neededMoney
            # Evtl. vorhandenes Silber der Einheit ausgeben
            if unit.inventory.has_key(ID_P_SILB):
                missingMoney -= unit.inventory[ID_P_SILB].amount
                unit.delProduct(ID_P_SILB, unit.inventory[ID_P_SILB].amount)
            # Restliches Silber aus der Region holen
            for u in ownUnits:
                if not u.getFlag(FLAG_SUPPLY):
                    continue
                if u.isSacrificed or u.isSurrendered:
                    continue
                if u.inventory.has_key(ID_P_SILB):
                    deletable = u.inventory[ID_P_SILB].amount
                    if (missingMoney < deletable):
                        deletable = missingMoney
                    u.delProduct(ID_P_SILB, deletable)
                if (missingMoney <= 0):
                    break
        if product.hasType(TYPE_P_HUMANOID):
            if not (race is None) and (race.amount > 0):
                newPersons = race.amount + addAmount
                talents = unit.talents.values()
                for t in talents:
                    xp = race.amount * ((t.level * 5) + t.xp)
                    t.level = int(xp / (5 * newPersons))
                    t.xp = int((xp - (t.level * newPersons * 5)) / newPersons)
                if talents != []:
                    self.output += [Message(CAT_WARN, 158, line = self.line)]
            if product.getKey() == ID_P_ANFU:
                aw.quantityLeaders += addAmount
            else:
                aw.quantityRegulars += addAmount
        region.sales[productKey].tradedAmount += addAmount
        region.MoneySales += (addAmount * productFee)
        unit.addProduct(productKey, addAmount)
        if product.hasType(TYPE_P_TRADE):
            region.ppTrade = True
        return

class CommandKontakt(Command):
    def __init__(self, line):
        super(CommandKontakt, self).__init__(line)
        self.syntax = "kontakt einheitsnummer|alle"
        self.alles  = False

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_NUMBER):
                self.parameters += [RefUnit(int(value))]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("KONTAKT"), self.line)]
            elif (type == TOK_KEYWORD):
                if (value == "alle"):
                    self.alles = True
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("KONTAKT"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("KONTAKT"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("KONTAKT"), self.line)]
            return False

class CommandLehre(Command):
    def __init__(self, line):
        super(CommandLehre, self).__init__(line)
        self.fLong  = True
        self.syntax = "lehre <Einheitsnummer(n)>"
        self.name = "lehre"

    def parse(self):
        try:
            while(True):
                ref = RefUnit()
                if ref.parse():
                    self.parameters += [ref]
                else:
                    self.output += [Message(CAT_ERR, 7, ("LEHRE"), self.line)]
                    ReadUntilNL()
                    return False
        except NewlineException:
            if (len(self.parameters) != 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("LEHRE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.longCommand != "") and (unit.longCommand != self.name):
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        if not unit.inventory.has_key(ID_P_ANFU):
            self.output += [Message(CAT_ERR, 77, line = self.line)]
            return
        for p in self.parameters:
            unit.teachedPersons += p.obj.getPersons()
            if (unit.teachedPersons > (unit.getPersons() * 10)):
                self.output += [Message(CAT_ERR, 78, (unit.teachedPersons, unit.getPersons() * 10), self.line)]
            if (p.obj.partynumber == aw.partynumber):
                if (p.obj.learnedTalent is None):
                    self.output += [Message(CAT_WARN, 114, (p.obj.getKey()), self.line)]
                    continue
                if not unit.talents.has_key(p.obj.learnedTalent):
                    self.output += [Message(CAT_ERR, 79, (p.obj.learnedTalent), self.line)]
                    continue
                if (unit.talents[p.obj.learnedTalent].level <= p.obj.talents[p.obj.learnedTalent].level):
                    self.output += [Message(CAT_ERR, 97, (p.obj.getKey(), p.obj.learnedTalent), self.line)]
                    continue
                p.obj.isTeached = True
        return

class CommandLerne(Command):
    def __init__(self, line):
        super(CommandLerne, self).__init__(line)
        self.fLong  = True
        self.syntax = "lerne <Talent>"
        self.name = "lerne"

    def parse(self):
        try:
            tal = RefTalent()
            if tal.parse():
                self.parameters += [tal]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("LERNE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("LERNE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("LERNE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        learnTalent = self.parameters[0].obj
        key = learnTalent.getKey()
        if not unit.canLearn(learnTalent): # Einheit kann das Talent nicht erlernen
            self.output += [Message(CAT_ERR, 80, (key), self.line)]
            return
        if unit.talents.has_key(key) and (unit.talents[key].title == DIV_MASTER): # Einheit ist schon Meister
            self.output += [Message(CAT_ERR, 81, (key), self.line)]
            return
        if (unit.isMagician() and (learnTalent.hasType(TYPE_T_SPELL))): # Bei Magiern hier noch die 'Kann erlenen'-Liste checken
            if not unit.learnable.has_key(key):
                self.output += [Message(CAT_ERR, 80, (key), self.line)]
                return
        missingMoney = neededMoney = learnTalent.learningFee * unit.getPersons()
        if (neededMoney <= 0): # Talent ohne Lernkosten kann nicht erlernt werden
            self.output += [Message(CAT_ERR, 82, (key), self.line)]
            return
        if unit.inventory.has_key(ID_P_SILB) and (unit.inventory[ID_P_SILB].amount >= neededMoney):
            unit.delProduct(ID_P_SILB, neededMoney)
        else: # Einheit hat nicht genuegend Silber --> in der Region schaun
            if unit.inventory.has_key(ID_P_SILB):
                missingMoney -= unit.inventory[ID_P_SILB].amount
            # Schaun, ob in der Region genuegend Silber vorhanden ist
            ownUnits = region.getUnitsFromPartyAsList(aw.partynumber)
            for u in ownUnits:
                if not u.getFlag(FLAG_SUPPLY):
                    continue
                if u.isSacrificed or u.isSurrendered:
                    continue
                if u.inventory.has_key(ID_P_SILB):
                    missingMoney -= u.inventory[ID_P_SILB].amount
            if (missingMoney > 0):
                # In der Region ist nicht genuegend Silber vorhanden
                self.output += [Message(CAT_ERR, 147, line = self.line)]
                return
            missingMoney = neededMoney
            # Evtl. vorhandenes Silber der Einheit ausgeben
            if unit.inventory.has_key(ID_P_SILB):
                missingMoney -= unit.inventory[ID_P_SILB].amount
                unit.delProduct(ID_P_SILB, unit.inventory[ID_P_SILB].amount)
            # Restliches Silber aus der Region holen
            for u in ownUnits:
                if not u.getFlag(FLAG_SUPPLY):
                    continue
                if u.isSacrificed or u.isSurrendered:
                    continue
                if u.inventory.has_key(ID_P_SILB):
                    deletable = u.inventory[ID_P_SILB].amount
                    if (missingMoney < deletable):
                        deletable = missingMoney
                    u.delProduct(ID_P_SILB, deletable)
                if (missingMoney <= 0):
                    break
        if not unit.talents.has_key(key):
            unit.talents[key] = learnTalent
            unit.talents[key].title = "Laie"
        unit.learnedTalent = key
        region.MoneyLearning += neededMoney

class CommandMeuchle(Command):
    def __init__(self, line):
        super(CommandMeuchle, self).__init__(line)
        self.syntax      = "meuchle <Zieleinheit>"

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_NUMBER):
                ref = RefUnit(int(value), False, None)
                self.parameters += [ref]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("MEUCHLE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("MEUCHLE"), self.line)]
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("MEUCHLE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.rougeCommands < unit.getPersons()):
            unit.rougeCommands += 1
            return
        self.output += [Message(CAT_ERR, 83, line = self.line)]
        return

class CommandNeu(Command):
    def __init__(self, line):
        super(CommandNeu, self).__init__(line)
        self.syntax = "neu <alias>"

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_NUMBER):
                self.parameters += [int(value)]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("NEU"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("NEU"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("NEU"), self.line)]
            return False

class CommandOffenbare(Command):
    def __init__(self, line):
        super(CommandOffenbare, self).__init__(line)
        self.syntax = "offenbare [einheit|partei]"

        self.keywords = {"einheit": 1, "partei": 2, "default": 3}
        self.target   = 0

    def parse(self):
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                try:
                    self.target = self.keywords[value]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("OFFENBARE"), self.line)]
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("OFFENBARE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("OFFENBARE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            if (len(self.parameters) == 0):
                self.target = 3
                return True
            self.output += [Message(CAT_ERR, 8, ("OFFENBARE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.target == 1):
            unit.setFlag(FLAG_REVEAL_UNIT, 1)
            unit.setFlag(FLAG_REVEAL_PARTY, 0)
            unit.setFlag(FLAG_REVEAL, 0)
        elif (self.target == 2):
            unit.setFlag(FLAG_REVEAL_UNIT, 0)
            unit.setFlag(FLAG_REVEAL_PARTY, 1)
            unit.setFlag(FLAG_REVEAL, 0)
        else:
            unit.setFlag(FLAG_REVEAL_UNIT, 0)
            unit.setFlag(FLAG_REVEAL_PARTY, 0)
            unit.setFlag(FLAG_REVEAL, 1)
        return

class CommandOpfere(Command):
    def __init__(self, line):
        super(CommandOpfere, self).__init__(line)
        self.syntax        = "opfere <GoetterparteiNr.> <Anzahl|alle|alles> <Gegenstand>"
        self.isSacrificed = False

    def parse(self):
        try:
            gott = RefParty()
            if gott.parse():
                if ((int(gott.id) < 1000) or (int(gott.id) > 1013)):
                    self.output += [Message(CAT_ERR, 84, line = self.line)]
                    ReadUntilNL()
                    return False
                self.parameters += [gott]
                (type, value) = GetEntry()
                if ((type == TOK_KEYWORD) and (value == "einheit")):
                    self.isSacrificed = True
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("OPFERE"), self.line)]
                        ReadUntilNL()
                        return False
                else:
                    PushbackEntry((type, value))
                menge = TypeAmount()
                if menge.parse():
                    self.parameters += [menge]
                    produkt = RefProduct()
                    if produkt.parse():
                        self.parameters += [produkt]
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("OPFERE"), self.line)]
                            return False
            self.output += [Message(CAT_ERR, 7, ("OPFERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("OPFERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        god = self.parameters[0].id
        if aw.oblations.has_key(god):
            if (aw.oblations[god] != unit):
                self.output += [Message(CAT_ERR, 85, (aw.oblations[god].getKey()), self.line)]
                return
        else:
            aw.oblations[god] = unit
        if self.isSacrificed: # Einheit wird geopfert
            self.output += [Message(CAT_HINT, 127, line = self.line)]
            unit.isSacrificed = True
            if unit.isLeader():
                aw.quantityLeaders -= unit.getPersons()
            else:
                aw.quantityRegulars -= unit.getPersons()
            return
        productKey = self.parameters[2].obj.getKey()
        if not unit.inventory.has_key(productKey): # Einheit hat den Gegenstand nicht
            self.output += [Message(CAT_ERR, 55, (productKey), self.line)]
            return
        productAmount = unit.inventory[productKey].amount
        if self.parameters[1].hasDefinedValue():
            if unit.inventory[productKey].amount >= self.parameters[1].value: # nicht genug davon da
                productAmount = self.parameters[1].value
            else:
                self.output += [Message(CAT_ERR, 56, (productKey), self.line)]
        if (self.parameters[2].obj.hasType(TYPE_P_HUMANOID)): # schaun, ob es sich um eine Rasse handelt
            if productKey == ID_P_ANFU:
                aw.quantityLeaders -= productAmount
            else:
                aw.quantityRegulars -= productAmount
        unit.delProduct(productKey, productAmount)
        return

class CommandOption(Command):
    def __init__(self, line):
        super(CommandOption, self).__init__(line)
        self.syntax = "option <Optionstyp> <Schalter>"
        self.vl_values = {"aus": 0, "kurz":1, "lang":2, "beginner":3}
        self.desc_values = {"aus": 0, "ein":1}
        self.vorlage = -1
        self.desc = -1
        self.cr = False
        self.normal = False
        self.zeilenlaenge = 0

    def parse(self):
        ok = True
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                if value == "vorlagebeschreibung":
                    (type, value) = GetEntry()
                    if type == TOK_KEYWORD:
                        try:
                            self.desc = self.desc_values[value]
                        except KeyError:
                            self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                            ok = False
                    else:
                        self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                        ok = False
                elif value == "vorlage":
                    (type, value) = GetEntry()
                    if type == TOK_KEYWORD:
                        try:
                            self.vorlage = self.vl_values[value]
                        except KeyError:
                            self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                            ok = False
                    else:
                        self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                        ok = False
                elif value == "cr":
                    self.cr = True
                elif value == "normal":
                    self.normal = True
                elif value == "zeilenlaenge":
                    (type, value) = GetEntry()
                    if type == TOK_NUMBER:
                        self.zeilenlaenge = int(value)
                    else:
                        self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                        ok = False
                else:
                    self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                    ok = False
            else:
                self.output += [Message(CAT_ERR, 7, ("OPTION"), self.line)]
                ok = False
            if ok:
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("OPTION"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("OPTION"), self.line)]
            return False

class CommandPartei(Command):
    def __init__(self, line):
        super(CommandPartei, self).__init__(line)
        self.syntax      = "partei krieg <Punkte> handel <Punkte> magie <Punkte>"
        self.ppWar   = 0
        self.ppMagic = 0
        self.ppTrade = 0

    def parse(self):
        try:
            (type, value) = GetEntry()
            if ((type == TOK_KEYWORD) and (value == "krieg")):
                (type, value) = GetEntry()
                if (type == TOK_NUMBER):
                    self.ppWar = int(value)
                    (type, value) = GetEntry()
                    if ((type == TOK_KEYWORD) and (value == "handel")):
                        (type, value) = GetEntry()
                        if (type == TOK_NUMBER):
                            self.ppTrade = int(value)
                            (type, value) = GetEntry()
                            if ((type == TOK_KEYWORD) and (value == "magie")):
                                (type, value) = GetEntry()
                                if (type == TOK_NUMBER):
                                    self.ppMagic = int(value)
                                    if ReadNewline():
                                        return True
                                    else:
                                        self.output += [Message(CAT_ERR, 8, ("PARTEI"), self.line)]
            self.output += [Message(CAT_ERR, 7, ("PARTEI"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("PARTEI"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if aw.ppNewlySet:
            self.output += [Message(CAT_WARN, 115, line = self.line)]
            return
        if ((self.ppTrade + self.ppMagic + self.ppWar) > aw.ppEntire):
            self.output += [Message(CAT_ERR, 35, line = self.line)]
            return
        aw.ppWar   = self.ppWar
        aw.ppTrade = self.ppTrade
        aw.ppMagic = self.ppMagic
        return

class CommandPasswort(Command):
    def __init__(self, line):
        super(CommandPasswort, self).__init__(line)
        self.syntax      = "passwort \"passwort\" "

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_STRING):
                self.parameters += [value]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("PASSWORT"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("PASSWORT"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("PASSWORT"), self.line)]
            return False

class CommandPluendere(Command):
    def __init__(self, line):
        super(CommandPluendere, self).__init__(line)
        self.syntax = "pluendere"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("PLUENDERE"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Einheit muss bewaffnet sein, um Pluendern zu koennen
        if not unit.isArmed(aw):
            self.output += [Message(CAT_ERR, 87, line = self.line)]
            return
        # Ist die Einheit getarnt und soll pluendern?
        if (unit.getFlag(FLAG_MASKED)):
            self.output += [Message(CAT_HINT, 130, line = self.line)]
            unit.setFlag(FLAG_MASKED, 0)
            unit.setFlag(FLAG_REVEAL_UNIT, 1)
        # Merken, dass die Einheit pluendert
        unit.isPlundering = True
        unitPersons = unit.getArmedPersons(aw)
        money = region.incomeTaxes - region.incomeTaxesUsed
        region.IncomeTaxesUsed += unitPersons * 50
        # Ist noch genuegend Steuersilber fuer alle Personen in der Einheit da?
        if (money >= unitPersons * 50):
            unit.addProduct(ID_P_SILB, (unitPersons * 50 * 2))
            self.output += [Message(CAT_INFO, 150, para = (unitPersons * 50 * 2, "Pluenderung"))]
        # Ist ueberhaupt noch Arbeitssilber in der Region uebrig?
        elif (money > 0):
            unit.addProduct(ID_P_SILB, (money * 2))
            self.output += [Message(CAT_WARN, 116, line = self.line)]
            self.output += [Message(CAT_INFO, 150, para = (money * 2, "Pluenderung"))]
        else:
            self.output += [Message(CAT_WARN, 117, line = self.line)]
        return

class CommandProduziere(Command):
    def __init__(self, line):
        super(CommandProduziere, self).__init__(line)
        self.fLong  = True
        self.syntax = "produziere <Gegenstand>"
        self.name = "produziere"

    def parse(self):
        try:
            produkt = RefProduct()
            if produkt.parse():
                self.parameters += [produkt]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("PRODUZIERE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("PRODUZIERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("PRODUZIERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        product = self.parameters[0].obj
        # Ermitteln, ob die Einheit den Gegenstand ueberhaupt produzieren kann
        if not unit.canProduce(product):
            self.output += [Message(CAT_ERR, 86, line = self.line)]
            return
        # Produzierbare Menge ermitteln
        (amount, materialPerPiece) = unit.getProductionMaterial(product)
        # Ermitteln ob die Gegenstaende zur Produktion prinzipiell vorhanden sind
        if (amount == 0):
            self.output += [Message(CAT_ERR, 88, line = self.line)]
            return
        productKey = product.getKey()
        if (materialPerPiece != []):
            for p in materialPerPiece:
                unit.delProduct(p.getKey(), (p.amount * amount))
        else: # Produkt aus der Region, da nur dieses aus nichts erschaffen werden kann
            if not region.producable.has_key(productKey):
                self.output += [Message(CAT_ERR, 89, (productKey), self.line)]
                return
            leftAmount = region.producable[productKey].amount - region.producable[productKey].tradedAmount
            region.producable[productKey].tradedAmount += amount
            if (leftAmount <= 0):
                self.output += [Message(CAT_HINT, 142, (productKey), self.line)]
                return
            if (leftAmount < amount):
                self.output += [Message(CAT_HINT, 141, (productKey, leftAmount, amount), self.line)]
                amount = leftAmount
        unit.addProduct(productKey, amount)
        unit.output += [Message(CAT_INFO, 151, (amount, product.plural))]
        # Handels-PP setzen
        unit.region.ppTrade = True
        return

class CommandReihenfolge(Command):
    def __init__(self, line):
        super(CommandReihenfolge, self).__init__(line)
        self.syntax   = "reihenfolge <Option> [Einheitsnr]"
        self.keywords = {"hoch": 1, "runter": 2, "vor": 3, "hinter": 4}
        self.target   = 0

    def parse(self):
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                try:
                    self.target = self.keywords[value]
                    if (self.target > 2):
                        unit = RefUnit()
                        if unit.parse():
                            self.parameters += [unit]
                            if ReadNewline():
                                return True
                            else:
                                self.output += [Message(CAT_ERR, 8, ("REIHENFOLGE"), self.line)]
                        else:
                            self.output += [Message(CAT_ERR, 7, ("REIHENFOLGE"), self.line)]
                    else:
                        if ReadNewline():
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("REIHENFOLGE"), self.line)]
                    ReadUntilNL()
                    return False
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("REIHENFOLGE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("REIHENFOLGE"), self.line)]
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("REIHENFOLGE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.target == 1):   # hoch
            index = unit.object.sortedUnits.index(unit) - 1
        elif (self.target == 2): # runter
            index = unit.object.sortedUnits.index(unit) + 2
        elif (self.target == 3): # vor
            index = unit.object.sortedUnits.index(self.parameters[0].obj)
        elif (self.target == 4): # hinter
            index = unit.object.sortedUnits.index(self.parameters[0].obj) + 1
        if (index < 0):
            index = 0
        elif (index > (len(unit.object.sortedUnits) - 1)):
            index = (len(unit.object.sortedUnits) - 1)
        unit.object.sortedUnits.remove(unit)
        unit.object.sortedUnits.insert(index, unit)
        return

class CommandReise(Command):
    def __init__(self, line):
        super(CommandReise, self).__init__(line)
        self.fLong  = True
        self.Mindestbewegung = True
        self.syntax = "reise <Richtung(en)>|[pause]"
        self.name = "reise"

    def parse(self):
        try:
            while True:
                (type, value) = GetEntry()
                if (type == TOK_NUMBER):
                    self.parameters += [RefObject(int(value))]
                    continue
                PushbackEntry((type, value))
                dir = TypeDirection()
                if dir.parse():
                    self.parameters += [dir]
                    continue
                self.output += [Message(CAT_ERR, 7, ("REISE"), self.line)]
                return False
        except NewlineException:
            if (len(self.parameters) != 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("REISE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.longCommand != "") and (unit.longCommand != self.name):
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        parameterNr      = 0
        if (unit.fleetNumber == 0): # Bewegungspunkte und Kapazitaet berechnen
            movingObject = unit
        else:
            movingObject = region.getFleet(unit.fleetNumber)
            if movingObject is None:
                self.output += [Message(CAT_ERR, 152, (unit.fleetNumber), self.line)]
                return
        movingObject.calcEncumbrance()
        movingObject.calcCapacity()
        movingObject.calcBP()
        while parameterNr <= (len(self.parameters) - 1): # erste Richtung ermitteln
            if (self.parameters[parameterNr].__class__.__name__ == "RefObject"):
                # erstmal: es darf sich nicht um eine Flotte handeln
                if (unit.fleetNumber != 0):
                    unit.output += [Message(CAT_ERR, 96, line = self.line)]
                    return
                unit.object.delUnit(unit)
                unit.object = self.parameters[parameterNr].obj
                unit.object.addUnit(unit)
                parameterNr += 1
                continue
            if self.parameters[parameterNr].through: # hindurch: Warnung ausgeben
                # erstmal: es darf sich nicht um eine Flotte handeln
                if (unit.fleetNumber != 0):
                    unit.output += [Message(CAT_ERR, 156, line = self.line)]
                    return
                if (unit.object == region.getHinterland()): # Einheit steht im Umland
                    self.output += [Message(CAT_ERR, 90, line = self.line)]
                    return
                self.output += [Message(CAT_WARN, 118, line = self.line)]
                return
            if self.parameters[parameterNr].wait: # pause: 1 BP verbrauchen
                movingObject.usedBP += 1
                parameterNr += 1
                continue
            newRegion = unit.region.getNeighbour(self.parameters[parameterNr], aw)
            movingObject.usedBP += newRegion.getMovementCost(unit.fleetNumber != 0)
            movingResult = movingObject.move(newRegion)
            if (movingResult == 0): # Es hat alles geklappt
                if newRegion.terrain == "unbekannt":
                    self.output += [Message(CAT_WARN, 119, line = self.line)]
                parameterNr += 1
                continue
            elif (movingResult == 1): # Einheit kann sich nicht schwimmend bewegen
                self.output += [Message(CAT_ERR, 92, line = self.line)]
                return
            elif (movingResult == 2): # Einheit hat nicht mehr genuegend BPs
                self.output += [Message(CAT_WARN, 94, line = self.line)]
                return
            elif (movingResult == 3): # Einheit ist ueberladen
                self.output += [Message(CAT_ERR, 93, line = self.line)]
                return
        return

class CommandSammle(Command):
    def __init__(self, line):
        super(CommandSammle, self).__init__(line)
        self.syntax = "sammle alles|alle|Anzahl <Gegenstand>"
        self.type = None  # normal = 0, limit = 1, beute = 2
        self.types = {"normal":0, "limit": 1, "beute": 2}
        self.limit = -1  # Gewichtlimit, gueltig, falls type = 1
        self.weg = False # True, falls sammle beute weg, gueltig falls type = beute

    def parse(self):
        ok = True
        weiter = False
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                if value == "limit":
                    self.type = self.types["limit"]
                    (type, value) = GetEntry()
                    if type == TOK_NUMBER:
                        self.limit = int(value)
                    else:
                        self.output += [Message(CAT_ERR, 7, ("SAMMLE"), self.line)]
                        ok = False
                elif value == "beute":
                    self.type = self.types["beute"]
                    if not ReadNewline():
                        (type, value) = GetEntry()
                        if (type == TOK_KEYWORD) and (value == "weg"):
                            self.weg = True
                        else:
                            self.output += [Message(CAT_ERR, 7, ("SAMMLE"), self.line)]
                            ok = False
                    else:
                        return True
                elif (value == "alles") or (value == "alle"):
                    weiter = True
                    PushbackEntry((type, value))
                else:
                    self.output += [Message(CAT_ERR, 7, ("SAMMLE"), self.line)]
                    ok = False
            else:
                PushbackEntry((type, value))
                weiter = True
            if weiter:
                self.type = self.types["normal"]
                menge = TypeAmount()
                if menge.parse():
                    self.parameters += [menge]
                    ref = RefProduct()
                    try:
                        if ref.parse():
                            self.parameters += [ref]
                        else:
                            self.output += [Message(CAT_ERR, 7, ("SAMMLE"), self.line)]
                            ok = False
                    except NewlineException:
                        if menge.value == TypeAmount.ALLES:
                            return True
                        else:
                            self.output += [Message(CAT_ERR, 8, ("SAMMLE"), self.line)]
                            ok = False
                else:
                    self.output += [Message(CAT_ERR, 7, ("SAMMLE"), self.line)]
                    ok = False
            if ok:
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("SAMMLE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("SAMMLE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.type == self.types["beute"]):
            return
        elif (self.type == self.types["limit"]):
            unit.limitWeight = self.limit
            return

        # self.types["normal"]
        limit = (unit.limitWeight > 0)
        if limit:
            unit.calcEncumbrance()
            weightLeft = unit.limitWeight - unit.encumbrance
        collectAll = (len(self.parameters) == 1)
        if not collectAll:
            definedAmount = self.parameters[0].hasDefinedValue()
            collectAmount = self.parameters[0].value
            collectItem   = self.parameters[1].obj.getKey()
            if unit.inventory.has_key(collectItem):
                collectAmount -= unit.inventory[collectItem].amount
        ownUnits = region.getUnitsFromPartyAsList(aw.partynumber)

        for u in ownUnits:
            if (u == unit):              # Es handelt sich um die sammelnde Einheit
                continue
            if u.getFlag(FLAG_KEEP_ALL): # Einheit ist egoistisch und gibt nix ab
                continue
            items = u.inventory.values()
            for i in items:
                if i.hasType(TYPE_P_HUMANOID): # Rassen werden nicht gesammelt
                    continue
                if (i.keepAmount < 0):         # Nicht ganz so egoistosch, behaelt nur alles von diesem Gegenstand
                    continue
                if (i.amount <= i.keepAmount): # Wuerde ja was abgeben, aber hat selber nicht genug
                    continue
                if not collectAll and (collectItem != i.getKey()): # Falsches Produkt
                    continue
                addAmount = i.amount - i.keepAmount
                if limit:
                    if (i.weight != 0) and (weightLeft < (i.weight * addAmount)):
                        addAmount = weightLeft / i.weight
                if (addAmount <= 0):           # Von dem Gegenstand bekommt die sammelnde Einheit nix
                    continue
                if not collectAll and definedAmount:
                    if (collectAmount < addAmount):
                        addAmount = collectAmount
                u.delProduct(i.getKey(), addAmount)    # beim Besitzer abziehen
                unit.addProduct(i.getKey(), addAmount) # beim Sammler hinzufuegen
                if not collectAll and definedAmount:
                    collectAmount -= addAmount
                    if (collectAmount == 0):
                      return
                if limit:
                    weightLeft -= (addAmount * i.weight)

        if not collectAll:
            if not unit.inventory.has_key(collectItem) or (unit.inventory[collectItem].amount == 0):
                self.output += [Message(CAT_HINT, 131, (collectItem), self.line)]
            elif definedAmount and (unit.inventory[collectItem].amount != self.parameters[0].value):
                self.output += [Message(CAT_HINT, 132, (collectItem), self.line)]
        return

class CommandSegle(CommandReise):
    def __init__(self, line):
        CommandReise.__init__(self, line)
        self.fLong  = True
        self.Mindestbewegung = False
        self.syntax = "segle [<Richtung(en)>]"
        self.name = "segle"

    def parse(self):
        try:
            while True:
                dir = TypeDirection()
                if dir.parse():
                    self.parameters += [dir]
                    continue
                self.output += [Message(CAT_ERR, 7, ("SEGLE"), self.line)]
                return False
        except NewlineException:
            return True

    def execute(self, unit, region, aw):
        if (len(self.parameters) != 0):
            CommandReise.execute(self, unit, region, aw)
            self.output += [Message(CAT_HINT, 133, ("SEGLE", "REISE"), self.line)]
            return
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        if (unit.fleetNumber == 0): # Einheit ist gar nicht auf einer Flotte
            self.output += [Message(CAT_ERR, 98, line = self.line)]
            return
        if (unit.fleetNumber == unit.getKey()): # Einheit ist der Kapitaen und kann daher nicht unterstuetzen
            self.output += [Message(CAT_ERR, 99, line = self.line)]
            return
        if not unit.talents.has_key(ID_T_SEGE):
            self.output += [Message(CAT_ERR, 100, (ID_T_SEGE), self.line)]
            return
        fleet = region.getFleet(unit.fleetNumber)
        fleet.talentlevel += (unit.getPersons() * unit.talents[ID_T_SEGE].level)
        return

class CommandStammrasse(Command):
    def __init__(self, line):
        super(CommandStammrasse, self).__init__(line)
        self.fUniqueRealm = True
        self.syntax       = "stammrasse <Rassenname>"

    def parse(self):
        try:
            produkt = RefProduct()
            if produkt.parse():
                self.parameters += [produkt]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("STAMMRASSE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("STAMMRASSE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("STAMMRASSE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (aw.optedRace == "keine"):
            race = self.parameters[0].obj
            if race.optableRace:
                aw.optedRace = race.plural
                return
            self.output += [Message(CAT_ERR, 101, (race.getKeyAsString()), self.line)]
            return
        self.output += [Message(CAT_ERR, 102, line = self.line)]
        return

class CommandStehle(Command):
    def __init__(self, line):
        super(CommandStehle, self).__init__(line)
        self.syntax      = "stehle <Zieleinheit> <Gegenstand>"

    def parse(self):
        try:
            unit = RefUnit()
            if unit.parse():
                self.parameters += [unit]
                produkt = RefProduct()
                if produkt.parse():
                    self.parameters += [produkt]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("STEHLE"), self.line)]
                        return False
            self.output += [Message(CAT_ERR, 7, ("STEHLE"), self.line)]
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("STEHLE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.rougeCommands < unit.getPersons()):
            unit.rougeCommands += 1
            return
        self.output += [Message(CAT_ERR, 83, line = self.line)]
        return

class CommandStirb(Command):
    def __init__(self, line):
        super(CommandStirb, self).__init__(line)
        self.syntax = "stirb \"passwort\" "

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_STRING):
                self.parameters += [value]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("STIRB"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("STIRB"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("STIRB"), self.line)]
            return False

class CommandTreibe(Command):
    def __init__(self, line):
        super(CommandTreibe, self).__init__(line)
        self.syntax = "treibe"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("TREIBE"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Wenn eine Einheit aufegloest wird (keine Personen mehr), wird der
        # Befehl nicht weiter abgearbeitet
        if unit.getRace() is None:
            return
        # Region darf nicht gepluendert wurden sein
        if region.isPlundered:
            self.output += [Message(CAT_ERR, 84, line = self.line)]
            return
        # Einheit muss bewaffnet sein, um Treiben zu koennen
        if not unit.isArmed(aw):
            self.output += [Message(CAT_ERR, 57, line = self.line)]
            return
        # Ist die Einheit getarnt und soll treiben?
        if (unit.getFlag(FLAG_MASKED)):
            self.output += [Message(CAT_HINT, 130, line = self.line)]
            unit.setFlag(FLAG_MASKED, 0)
            unit.setFlag(FLAG_REVEAL_UNIT, 1)
        # Merken, dass die Einheit treibt
        unit.isTaxing = True
        region.ppWar = True
        unitPersons = unit.getArmedPersons(aw)
        money = region.IncomeTaxes - region.IncomeTaxesUsed
        region.IncomeTaxesUsed += unitPersons * 50
        # Ist noch genuegend Steuersilber fuer alle Personen in der Einheit da?
        if (money >= unitPersons * 50):
            unit.addProduct(ID_P_SILB, (unitPersons * 50))
            self.output += [Message(CAT_INFO, 150, para = (unitPersons * 50, "Steuereintreibung"))]
        # Ist ueberhaupt noch Steuersilber in der Region uebrig?
        elif (money > 0):
            unit.addProduct(ID_P_SILB, money)
            self.output += [Message(CAT_WARN, 120, line = self.line)]
            self.output += [Message(CAT_INFO, 150, para = (money, "Steuereintreibung"))]
        else:
            self.output += [Message(CAT_WARN, 121, line = self.line)]
        return

class CommandUnterhalte(Command):
    def __init__(self, line):
        super(CommandUnterhalte, self).__init__(line)
        self.fLong  = True
        self.syntax = "unterhalte"
        self.name = "unterhalte"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("UNTERHALTE"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        # Die Einheit muss das Talent Unterhaltung  beherrschen
        if not unit.talents.has_key(ID_T_UNTE):
            self.output += [Message(CAT_ERR, 86, line = self.line)]
            return
        unitPersons = unit.getPersons()
        wages = unit.talents[ID_T_UNTE].level * 20
        money = region.IncomeEntertainment - region.IncomeEntertainmentUsed
        region.IncomeEntertainmentUsed += unitPersons * wages
        # Ist noch genuegend Unterhaltungssilber fuer alle Personen in der Einheit da?
        if (money >= unitPersons * wages):
            unit.addProduct(ID_P_SILB, (unitPersons * wages))
            self.output += [Message(CAT_INFO, 150, para = (unitPersons * wages, "Unterhaltung"))]
        # Ist ueberhaupt noch Unterhaltungssilber in der Region uebrig?
        elif (money > 0):
            unit.addProduct(ID_P_SILB, money)
            self.output += [Message(CAT_WARN, 122, line = self.line)]
            self.output += [Message(CAT_INFO, 150, para = (unitPersons * wages, "Unterhaltung"))]
        else:
            self.output += [Message(CAT_WARN, 123, line = self.line)]
        # Handels-PPs an der Region merken
        region.ppTrade = True
        return

class CommandVerbrauche(Command):
    def __init__(self, line):
        super(CommandVerbrauche, self).__init__(line)
        self.syntax   = "verbrauche [Modus]"
        self.keywords = {"einheit": 1, "partei": 2, "default": 3}
        self.target   = 0

    def parse(self):
        try:
            (type, value) = GetEntry()
            if type == TOK_KEYWORD:
                try:
                    self.target = self.keywords[value]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("VERBRAUCHE"), self.line)]
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("VERBRAUCHE"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("VERBRAUCHE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            if (len(self.parameters) == 0):
                self.target = 3
                return True
            self.output += [Message(CAT_ERR, 8, ("VERBRAUCHE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (self.target == 1): # einheit
            unit.setFlag(FLAG_CONSUME_PARTY, 0)
            unit.setFlag(FLAG_CONSUME_UNIT, 1)
        elif (self.target == 2): # partei
            unit.setFlag(FLAG_CONSUME_PARTY, 1)
            unit.setFlag(FLAG_CONSUME_UNIT, 0)
        elif (self.target == 3): # default
            unit.setFlag(FLAG_CONSUME_PARTY, 0)
            unit.setFlag(FLAG_CONSUME_UNIT, 0)
        return

class CommandVergiss(Command):
    def __init__(self, line):
        super(CommandVergiss, self).__init__(line)
        self.syntax = "vergiss <Talent>"

    def parse(self):
        try:
            tal = RefTalent()
            if tal.parse():
                self.parameters += [tal]
                if ReadNewline():
                    return True
                else:
                    self.output += [Message(CAT_ERR, 8, ("VERGISS"), self.line)]
            else:
                self.output += [Message(CAT_ERR, 7, ("VERGISS"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("VERGISS"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        talentKey = self.parameters[0].obj.getKey()
        if not unit.talents.has_key(talentKey):
            self.output += [Message(CAT_ERR, 100, (talentKey), self.line)]
            return
        del unit.talents[talentKey]
        return

class CommandVerkaufe(Command):
    def __init__(self, line):
        super(CommandVerkaufe, self).__init__(line)
        self.syntax = "verkaufe alle|alles|Anzahl <Gegenstand>"

    def parse(self):
        try:
            menge = TypeAmount()
            if menge.parse():
                self.parameters += [menge]
                produkt = RefProduct()
                if produkt.parse():
                    self.parameters += [produkt]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("VERKAUFE"), self.line)]
                        return False
            self.output += [Message(CAT_ERR, 7, ("VERKAUFE"), self.line)]
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("VERKAUFE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        soldProductKey = self.parameters[1].obj.getKey()
        if not unit.inventory.has_key(soldProductKey):
            self.output += [Message(CAT_ERR, 55, (soldProductKey), self.line)]
            return
        if not region.purchases.has_key(soldProductKey):
            self.output += [Message(CAT_ERR, 103,(soldProductKey), self.line)]
            return
        regionProduct = region.purchases[soldProductKey]
        unitProduct   = unit.inventory[soldProductKey]
        if regionProduct.tradedAmount >= regionProduct.amount:
            self.output += [Message(CAT_ERR, 104, (soldProductKey), self.line)]
            return
        if ((regionProduct.amount - regionProduct.tradedAmount) > unitProduct.amount):
            tradedAmount = unitProduct.amount
        else:
            tradedAmount = (regionProduct.amount - regionProduct.tradedAmount)
        if self.parameters[0].hasDefinedValue():
            if (unitProduct.amount < self.parameters[0].value):
                self.output += [Message(CAT_ERR, 56, (unitProduct.getKeyAsString()), self.line)]
            else:
                if (tradedAmount < self.parameters[0].value):
                    tradedAmount = self.parameters[0].value
        money = tradedAmount * regionProduct.cost
        region.MoneyPurchases += money
        regionProduct.tradedAmount += tradedAmount
        unit.delProduct(soldProductKey, tradedAmount)
        unit.addProduct(ID_P_SILB, money)
        if self.parameters[1].obj.hasType(TYPE_P_TRADE):
            region.ppTrade = True
        return

class CommandVerlasse(Command):
    def __init__(self, line):
        super(CommandVerlasse, self).__init__(line)
        self.syntax = "verlasse"

    def parse(self):
        if ReadNewline():
            return True
        else:
            self.output += [Message(CAT_ERR, 8, ("VERLASSE"), self.line)]
        ReadUntilNL()
        return False

    def execute(self, unit, region, aw):
        self.executed = True
        # Einheit aus dem Objekt entfernen ...
        unit.object.delUnit(unit)
        hinterland = region.getHinterland()
        # ... und ins Umland packen
        hinterland.addUnit(unit)
        return

class CommandVermeide(Command):
    def __init__(self, line):
        super(CommandVermeide, self).__init__(line)
        self.syntax = "vermeide 0|1"
        self.value = False

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.value = f.value
            else:
                self.output += [Message(CAT_ERR, 7, ("VERMEIDE"), self.line)]
            if ReadNewline():
                return True
            else:
                self.output += [Message(CAT_ERR, 8, ("VERMEIDE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("VERMEIDE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.getFlag(FLAG_GUARD) and self.value:
            unit.setFlag(FLAG_GUARD, 0)
            self.output += [Message(CAT_HINT, 134, line = self.line)]
        unit.setFlag(FLAG_AVOID, self.value)
        return

class CommandVersorge(Command):
    def __init__(self, line):
        super(CommandVersorge, self).__init__(line)
        self.syntax = "versorge 0|1"
        self.value = False

    def parse(self):
        try:
            f = TypeFlag()
            if f.parse():
                self.value = f.value
            else:
                self.output += [Message(CAT_ERR, 7, ("VERSORGE"), self.line)]
            if ReadNewline():
                return True
            else:
                self.output += [Message(CAT_ERR, 8, ("VERSORGE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("VERSORGE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        unit.setFlag(FLAG_SUPPLY, self.value)

class CommandVertretung(Command):
    def __init__(self, line):
        super(CommandVertretung, self).__init__(line)
        self.syntax = "vertretung <eMail-Adresse> <Dauer> \"Erklaerung\""
        self.output = [Message(CAT_HINT, 135, line = self.line)]

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type != TOK_IDENT):
                self.output += [Message(CAT_ERR, 7, ("VERTRETUNG"), self.line)]
                return False
            (type, value) = GetEntry()
            if (type != TOK_NUMBER):
                self.output += [Message(CAT_ERR, 7, ("VERTRETUNG"), self.line)]
                return False
            (type, value) = GetEntry()
            if (type != TOK_STRING):
                self.output += [Message(CAT_ERR, 7, ("VERTRETUNG"), self.line)]
                return False
            return True
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("VERTRETUNG"), self.line)]
            return False

class CommandVerwerte(Command):
    def __init__(self, line):
        super(CommandVerwerte, self).__init__(line)
        self.syntax = "verwerte Anzahl|alle|alles Gegenstand"

    def parse(self):
        try:
            menge = TypeAmount()
            if menge.parse():
                self.parameters += [menge]
                produkt = RefProduct()
                if produkt.parse():
                    self.parameters += [produkt]
                    if ReadNewline():
                        return True
                    else:
                        self.output += [Message(CAT_ERR, 8, ("VERWERTE"), self.line)]
                        return False
            self.output += [Message(CAT_ERR, 7, ("VERWERTE"), self.line)]
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("VERWERTE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if unit.longCommand != "":
            self.output += [Message(CAT_ERR, 19, line = self.line)]
            return
        unit.longCommand = self.name
        recycelProduct = self.parameters[1].obj
        recycelProductKey = recycelProduct.getKey()
        amount = unit.inventory[recycelProductKey].amount
        if not unit.canRecycle(recycelProduct):
            self.output += [Message(CAT_ERR, 105, (recycelProductKey), self.line)]
            return
        if self.parameters[0].hasDefniedValue:
            if self.parameters[0].value < amount:
                amount = self.parameters[0].value
        (possibleAmount, materialPerPiece) = unit.getRecyclingMaterial(recycelProduct)
        if (possibleAmount < amount):
            amount = possibleAmount
        unit.delProduct(recycelProductKey, amount)
        amount = int(amount / 4)
        for p in materialPerPiece:
            unit.addProduct(p.getKey(), amount)
        return

class CommandVorruecken(CommandReise):
    def __init__(self, line):
        CommandReise.__init__(self, line)
        self.fLong  = True
        self.Mindestbewegung = False
        self.syntax = "vorruecken Richtung(en)|[pause]"
        self.name = "vorruecken"

    def parse(self):
        try:
            while True:
                (type, value) = GetEntry()
                if (type == TOK_NUMBER):
                    self.parameters += [RefObject(int(value))]
                    continue
                PushbackEntry((type, value))
                dir = TypeDirection()
                if dir.parse():
                    self.parameters += [dir]
                    continue
                self.output += [Message(CAT_ERR, 7, ("VORRUECKEN"), self.line)]
                return False
        except NewlineException:
            if (len(self.parameters) != 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("VORRUECKEN"), self.line)]
            return False

    def execute(self, unit, region, aw):
        CommandReise.execute(self, unit, region, aw)
        self.output += [Message(CAT_HINT, 136, line = self.line)]
        unit.advancing = True
        return

class CommandZaubere(Command):
    def __init__(self, line):
        super(CommandZaubere, self).__init__(line)
        self.syntax = "zaubere <Zauber> [<Zauberoptionen>]"

    def parse(self):
        try:
            tal = RefTalent()
            if tal.parse():
                self.parameters += [tal]
                ReadUntilNL()
                return True
            else:
                self.output += [Message(CAT_ERR, 7, ("ZAUBERE"), self.line)]
                ReadUntilNL()
                return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("ZAUBERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if not unit.isMagician():
            self.output += [Message(CAT_ERR, 72, line = self.line)]
            return
        spec = self.parameters[0].obj
        if not spec.hasType(TYPE_T_SPELL):
            self.output += [Message(CAT_WARN, 124, (spec.getKeyAsString()), self.line)]
        unit.hasConjured = True
        return

class CommandZeige(Command):
    def __init__(self, line):
        super(CommandZeige, self).__init__(line)
        self.syntax = "zeige rasse|talent|gegenstand <Untertyp>"
        self.target = 0
        self.keywords = {"rasse" : 1, "talent" : 2, "gegenstand" : 3}
        self.talentlevel = 0

    def parse(self):
        try:
            (type, value) = GetEntry()
            if (type == TOK_KEYWORD):
                try:
                    self.target = self.keywords[value]
                    if (self.target == 2):
                        ref = RefTalent()
                        if ref.parse():
                            self.parameters += [ref]
                            (type, value) = GetEntry()
                            if (type != TOK_NUMBER):
                                self.output += [Message(CAT_ERR, 7, ("ZEIGE"), self.line)]
                                ReadUntilNL()
                                return False
                            else:
                                self.talentlevel = int(value)
                        else:
                            self.output += [Message(CAT_ERR, 7, ("ZEIGE"), self.line)]
                    else:
                        ref = RefProduct()
                        if ref.parse():
                            self.parameters += [ref]
                        else:
                            self.output += [Message(CAT_ERR, 7, ("ZEIGE"), self.line)]
                    if ReadNewline():
                        return True
                    self.output += [Message(CAT_ERR, 8, ("ZEIGE"), self.line)]
                except KeyError:
                    self.output += [Message(CAT_ERR, 7, ("ZEIGE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            self.output += [Message(CAT_ERR, 8, ("ZEIGE"), self.line)]
            return False

class CommandZerstoere(Command):
    def __init__(self, line):
        super(CommandZerstoere, self).__init__(line)
        self.syntax = "zerstoere [<Walltyp> <Richtung>]"

    def parse(self):
        try:
            obj = RefObject()
            if obj.parse():
                self.parameters += [obj]
                dir = TypeDirection()
                if dir.parse():
                    self.parameters += [dir]
                    if ReadNewline():
                        return True
                    self.output += [Message(CAT_ERR, 7, ("ZERSTOERE"), self.line)]
                    return False
            self.output += [Message(CAT_ERR, 8, ("ZERSTOERE"), self.line)]
            ReadUntilNL()
            return False
        except NewlineException:
            if (len(self.parameters) == 0):
                return True
            self.output += [Message(CAT_ERR, 8, ("ZERSTOERE"), self.line)]
            return False

    def execute(self, unit, region, aw):
        self.executed = True
        if (unit.object.sortedUnits[0] != unit):
            self.output += [Message(CAT_ERR, 22, line = self.line)]
            return
        if (unit.object == region.getHinterland()):
            self.output += [Message(CAT_ERR, 149, line = self.line)]
            return
        if not unit.canDestroy(unit.object):
            self.output += [Message(CAT_ERR, 106, line = self.line)]
            return
        (amount, addMaterial) = unit.getDestructionMaterial(unit.object)
        if not (addMaterial is None):
            for p in addMaterial:
                # TODO: PRUEFEN!!!
                unit.addProduct(p.getKey(), amount * p.amount)
        delObject = unit.object
        hinterland = region.getHinterland()
        for e in delObject.sortedUnits: # Leute vom Objekt ins Umland packen
            delObject.delUnit(e)
            hinterland.addUnit(e)
        hinterland.sortedUnits += delObject.sortedUnits
        del region.objects[delObject.getKey()]
        region.sortedObjects.remove(delObject)
        return

_commands = {}
_commands["adresse"]         = CommandAdresse
_commands["arbeite"]         = CommandArbeite
_commands["attackiere"]      = CommandAttackiere
_commands["ausbauen"]        = CommandAusbauen
_commands["ausschiffen"]     = CommandAusschiffen
_commands["baue"]            = CommandBaue
_commands["beanspruche"]     = CommandBeanspruche
_commands["befoerdere"]      = CommandBefoerdere
_commands["behalte"]         = CommandBehalte
_commands["belagere"]        = CommandBelagere
_commands["benenne"]         = CommandBenenne
_commands["beschreibe"]      = CommandBeschreibe
_commands["besiedeln"]       = CommandBesiedeln
_commands["betrete"]         = CommandBetrete
_commands["bewache"]         = CommandBewache
_commands["bezahle"]         = CommandBezahle
_commands["botschaft"]       = CommandBotschaft
_commands["dauersteuer"]     = CommandDauersteuer
_commands["einheit"]         = CommandEinheit
_commands["einschiffen"]     = CommandEinschiffen
_commands["einzeln"]         = CommandEinzeln
_commands["ende"]            = CommandEnde
_commands["erklaere"]        = CommandErklaere
_commands["erobere"]         = CommandErobere
_commands["foerdere"]        = CommandFoerdere
_commands["gib"]             = CommandGib
_commands["glaubenstendenz"] = CommandGlaubenstendenz
_commands["gott"]            = CommandGott
_commands["halte"]           = CommandHalte
_commands["hinten"]          = CommandHinten
_commands["kampfzauber"]     = CommandKampfzauber
_commands["kaufe"]           = CommandKaufe
_commands["kontakt"]         = CommandKontakt
_commands["lehre"]           = CommandLehre
_commands["lerne"]           = CommandLerne
_commands["meuchle"]         = CommandMeuchle
_commands["neu"]             = CommandNeu
_commands["offenbare"]       = CommandOffenbare
_commands["opfere"]          = CommandOpfere
_commands["option"]          = CommandOption
_commands["partei"]          = CommandPartei
_commands["passwort"]        = CommandPasswort
_commands["pluendere"]       = CommandPluendere
_commands["produziere"]      = CommandProduziere
_commands["reihenfolge"]     = CommandReihenfolge
_commands["reise"]           = CommandReise
_commands["sammle"]          = CommandSammle
_commands["segle"]           = CommandSegle
_commands["stammrasse"]      = CommandStammrasse
_commands["stehle"]          = CommandStehle
_commands["stirb"]           = CommandStirb
_commands["treibe"]          = CommandTreibe
_commands["unterhalte"]      = CommandUnterhalte
_commands["verbrauche"]      = CommandVerbrauche
_commands["vergiss"]         = CommandVergiss
_commands["verkaufe"]        = CommandVerkaufe
_commands["verlasse"]        = CommandVerlasse
_commands["vermeide"]        = CommandVermeide
_commands["versorge"]        = CommandVersorge
_commands["vertretung"]      = CommandVertretung
_commands["verwerte"]        = CommandVerwerte
_commands["vorruecken"]      = CommandVorruecken
_commands["zaubere"]         = CommandZaubere
_commands["zeige"]           = CommandZeige
_commands["zerstoere"]       = CommandZerstoere
_commands["Kommentar"]       = Comment

def createCommand(name, line):
    try:
        return _commands[name](line)
    except KeyError:
        return None
