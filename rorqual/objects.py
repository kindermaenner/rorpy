#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: objects.py,v 2.18 2005/05/12 22:04:38 kdm Exp $
#
# ---------------------------------------------------------------------------
#
#
#
# ---------------------------------------------------------------------------

__all__ = ["RorAW", "RorBuilding", "RorFleet", "RorHomestead", "RorLanes", "RorProduct", "RorRegion", "RorTalent", "RorUnit"]

import string
from constants import *
from util.dictionaries import KeyInsensitiveDict
from rorqual.kb import *
from util.messages import *
from copy import deepcopy

class RorBaseObject(object):
    def __init__(self, cr = None):
        self.cr = cr

    def getKey(self):
        raise NotImplementedError("getKey")

    def getKeyAsString(self):
        raise NotImplementedError("getKeyAsString")

    def clone(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        new = self.__class__()
        new.cr = self.cr
        return new

    def getCRObject(self):
        return self.cr

class RorAW(RorBaseObject):
    def __init__(self, cr = None):
        super(RorAW, self).__init__(cr)
        self.turn               = 1
        self.partyname          = ""
        self.partynumber        = 0
        self.treasury           = 0
        self.quantityLeaders    = 0
        self.quantityRegulars   = 0
        self.ppEntire           = 0
        self.ppTrade            = 0
        self.ppWar              = 0
        self.ppMagic            = 0
        self.ppWarUsed          = 0
        self.ppTradeUsed        = 0
        self.ppMagicUsed        = 0
        self.ppWarMax           = 0
        self.ppTradeMax         = 0
        self.ppMagicMax         = 0
        self.ppNewlySet         = False         # PPs im Zug neu gesetzt
        self.optedRace          = "keine"       # gewaehlte Stammrasse
        self.month              = ""
        self.religion           = "keine"
        self.god                = "keiner"
        self.year               = 1
        self.ets                = ""
        self.version            = ""            # CR-Version
        self.email              = ""
        self.gameStart          = 0
        self.contact            = ""
        self.ownUnits           = 0
        self.fragmentation      = 0
        self.gunmen             = 0
        self.rank               = 0
        self.income_entire      = 0
        self.msgBattles           = []
        self.msgDispatch          = []            # Botschaften
        self.msgContacts          = []
        self.msgErrors            = []
        self.msgEvents            = []
        self.msgTalents           = []
        self.msgTransfers         = []
        self.msgProduction        = []
        self.msgTrade             = []            # An- und Verkaeufe
        self.msgIncome            = []
        self.msgForeignActivities = []
        self.msgMagical           = []
        self.output               = []
        self.regions = KeyInsensitiveDict()
        self.oblations = {}                     # Opferungen
        self.standard_diplomacy = None
        self.diplomacy = {DIPLOMACY_ALLIED:[], DIPLOMACY_FRIENDLY:[], DIPLOMACY_NEUTRAL:[], DIPLOMACY_UNFRIENDLY:[], DIPLOMACY_HOSTILE:[]}
        if not self.cr is None:
            self.initFromCR()

    def __deepcopy__(self, memo):
        new = super(RorAW, self).__deepcopy__(memo)
        new.turn = self.turn
        new.partyname = self.partyname
        new.partynumber = self.partynumber
        new.treasury = self.treasury
        new.quantityLeaders = self.quantityLeaders
        new.quantityRegulars = self.quantityRegulars
        new.ppEntire = self.ppEntire
        new.ppTrade = self.ppTrade
        new.ppWar = self.ppWar
        new.ppMagic = self.ppMagic
        new.ppWarUsed = self.ppWarUsed
        new.ppTradeUsed = self.ppTradeUsed
        new.ppMagicUsed = self.ppMagicUsed
        new.ppWarMax = self.ppWarMax
        new.ppTradeMax = self.ppTradeMax
        new.ppMagicMax = self.ppMagicMax
        new.ppNewlySet = self.ppNewlySet
        new.optedRace = self.optedRace
        new.month = self.month
        new.religion = self.religion
        new.god = self.god
        new.year = self.year
        new.ets = self.ets
        new.version = self.version
        new.email = self.email
        new.gameStart = self.gameStart
        new.contact = self.contact
        new.ownUnits = self.ownUnits
        new.fragmentation = self.fragmentation
        new.gunmen = self.gunmen
        new.rank = self.rank
        new.income_entire = self.income_entire
        new.msgBattles = deepcopy(self.msgBattles, memo)
        new.msgDispatch = deepcopy(self.msgDispatch, memo)
        new.msgContacts = deepcopy(self.msgContacts, memo)
        new.msgErrors = deepcopy(self.msgErrors, memo)
        new.msgEvents = deepcopy(self.msgEvents, memo)
        new.msgTalents = deepcopy(self.msgTalents, memo)
        new.msgTransfers = deepcopy(self.msgTransfers, memo)
        new.msgProduction = deepcopy(self.msgProduction, memo)
        new.msgTrade = deepcopy(self.msgTrade, memo)
        new.msgIncome = deepcopy(self.msgIncome, memo)
        new.msgForeignActivities = deepcopy(self.msgForeignActivities, memo)
        new.msgMagical = deepcopy(self.msgMagical, memo)
        new.output = deepcopy(self.output, memo)
        new.regions = deepcopy(self.regions, memo)
        new.oblations = deepcopy(self.oblations, memo)
        new.standard_diplomacy = self.standard_diplomacy
        new.diplomacy = deepcopy (self.diplomacy, memo)
        return new

    def initFromCR(self):
        self.turn = self.cr.getSimpleValue(IDENT_MOVE)
        self.partyname = self.cr.getSimpleValue(IDENT_PARTYNAME)[0][:-1]
        self.partynumber = self.cr.getSimpleValue(IDENT_PARTYNUMBER)
        self.treasury = self.cr.getSimpleValue(IDENT_TREASURY)
        self.quantityLeaders = self.cr.getSimpleValue(IDENT_QUANTITY_LEADERS)
        self.quantityRegulars = self.cr.getSimpleValue(IDENT_QUANTITY_REGULARS)
        self.ppEntire = self.cr.getSimpleValue(IDENT_PP_ENTIRE)
        self.ppTrade = self.cr.getSimpleValue(IDENT_TRADE_PP)
        self.ppWar = self.cr.getSimpleValue(IDENT_WAR_PP)
        self.ppMagic = self.cr.getSimpleValue(IDENT_MAGIC_PP)
        self.ppWarUsed = self.cr.getSimpleValue(IDENT_WAR_PP_USED)
        self.ppTradeUsed = self.cr.getSimpleValue(IDENT_TRADE_PP_USED)
        self.ppMagicUsed = self.cr.getSimpleValue(IDENT_MAGIC_PP_USED)
        self.ppWarMax = self.cr.getSimpleValue(IDENT_WAR_PP_MAX)
        self.ppTradeMax = self.cr.getSimpleValue(IDENT_TRADE_PP_MAX)
        self.ppMagicMax = self.cr.getSimpleValue(IDENT_MAGIC_PP_MAX)
        if self.cr.hasSimpleValue(IDENT_OPTED_RACE):
            self.optedRace = self.cr.getSimpleValue(IDENT_OPTED_RACE)
        self.month = self.cr.getSimpleValue(IDENT_MONTH)
        if self.cr.hasSimpleValue(IDENT_RELIGION):
            self.religion = self.cr.getSimpleValue(IDENT_RELIGION)
        if self.cr.hasSimpleValue(IDENT_GOD):
            self.god = self.cr.getSimpleValue(IDENT_GOD)
        self.year = self.cr.getSimpleValue(IDENT_YEAR)
        self.ets = self.cr.getSimpleValue(IDENT_ETS)
        self.version = self.cr.getSimpleValue(IDENT_VERSION)
        self.email = self.cr.getSimpleValue(IDENT_EMAIL)
        self.gameStart = self.cr.getSimpleValue(IDENT_GAME_START)
        self.contact = self.cr.getSimpleValue(IDENT_CONTACT)
        self.ownUnits = self.cr.getSimpleValue(IDENT_OWN_UNITS)
        self.fragmentation = self.cr.getSimpleValue(IDENT_FRAGMENTATION)
        self.gunmen = self.cr.getSimpleValue(IDENT_ARMED)
        self.rank = self.cr.getSimpleValue(IDENT_RANKING)
        self.income_entire = self.cr.getSimpleValue(IDENT_INCOME_ENTIRE)
        if self.cr.hasValue(IDENT_MSG_BATTLES):
            self.msgBattles = map(lambda(x):x.replace("\\", "\n"), self.cr.getAllSimpleValues(IDENT_MSG_BATTLES))
        if self.cr.hasValue(IDENT_MSG_DISPATCH):
            self.msgDispatch = self.cr.getAllSimpleValues(IDENT_MSG_DISPATCH)
            if self.msgDispatch is None: self.msgDispatch = []
        if self.cr.hasValue(IDENT_MSG_CONTACTS):
            self.msgContacts = self.cr.getAllSimpleValues(IDENT_MSG_CONTACTS)
            if self.msgContacts is None: self.msgContacts = []
        if self.cr.hasValue(IDENT_MSG_ERRORS):
            self.msgErrors = self.cr.getAllSimpleValues(IDENT_MSG_ERRORS)
            if self.msgErrors is None: self.msgErrors = []
        if self.cr.hasValue(IDENT_MSG_EVENTS):
            self.msgEvents = self.cr.getAllSimpleValues(IDENT_MSG_EVENTS)
            if self.msgEvents is None: self.msgEvents = []
        if self.cr.hasValue(IDENT_MSG_TALENTS):
            self.msgTalents = self.cr.getAllSimpleValues(IDENT_MSG_TALENTS)
            if self.msgTalents is None: self.msgTalents = []
        if self.cr.hasValue(IDENT_MSG_TRANSFERS):
            self.msgTransfers = self.cr.getAllSimpleValues(IDENT_MSG_TRANSFERS)
            if self.msgTransfers is None: self.msgTransfers = []
        if self.cr.hasValue(IDENT_MSG_PRODUCTION):
            self.msgProduction = self.cr.getAllSimpleValues(IDENT_MSG_PRODUCTION)
            if self.msgProduction is None: self.msgProduction = []
        if self.cr.hasValue(IDENT_MSG_TRADE):
            self.msgTrade = self.cr.getAllSimpleValues(IDENT_MSG_TRADE)
            if self.msgTrade is None: self.msgTrade = []
        if self.cr.hasValue(IDENT_MSG_INCOME):
            self.msgIncome = self.cr.getAllSimpleValues(IDENT_MSG_INCOME)
            if self.msgIncome is None: self.msgIncome = []
        if self.cr.hasValue(IDENT_MSG_FOREIGN_ACTIVITIES):
            self.msgForeignActivities = self.cr.getAllSimpleValues(IDENT_MSG_FOREIGN_ACTIVITIES)
            if self.msgForeignActivities is None: self.msgForeignActivities = []
        if self.cr.hasValue(IDENT_MSG_MAGIC):
            self.msgMagical = self.cr.getAllSimpleValues(IDENT_MSG_MAGIC)
            if self.msgMagical is None: self.msgMagical = []
        self.initDiplomacyFromCR()
        cr_regionen = self.cr.getSubItem(IDENT_REGION)
        for cr_region in cr_regionen:
            region = RorRegion(cr_region)
            region.initFromCR(self)
            self.regions[region.getKeyAsString()] = region
        self.cr.ignoreIdent(IDENT_WAR_MAX)
        self.cr.ignoreIdent(IDENT_MAGICIANS_MAX)
        self.cr.ignoreIdent(IDENT_TRADE_MAX)
        self.cr.ignoreIdent(IDENT_GAME)
        self.cr.ignoreIdent(IDENT_PROPORTION_LEADERS)
        self.cr.ignoreIdent(IDENT_POPULATION)

    def initDiplomacyFromCR(self):
        dipl = self.cr.getSingleSubItem(IDENT_DIPLOMACY)
        for k in [DIPLOMACY_ALLIED, DIPLOMACY_FRIENDLY, DIPLOMACY_NEUTRAL, DIPLOMACY_UNFRIENDLY, DIPLOMACY_HOSTILE]:
            liste = dipl.getSimpleValue(k)
            for l in liste:
                self.setDiplomaticPosition(l, k)
        self.standard_diplomacy = dipl.getSimpleValue(IDENT_DIPLOMACY_STANDARD)

    def getKey(self):
        return self.turn

    def getKeyAsString(self):
        return str(self.turn)

    def setDiplomaticPosition(self, party, position):
        if not position in [DIPLOMACY_ALLIED, DIPLOMACY_FRIENDLY, DIPLOMACY_NEUTRAL, DIPLOMACY_UNFRIENDLY, DIPLOMACY_HOSTILE]:
            raise ValueError(position +  " is not a leagal value for diplomatic position")
        self.diplomacy[position].append(party)

    def removeDiplomaticPosition(self, party, position):
        if not position in [DIPLOMACY_ALLIED, DIPLOMACY_FRIENDLY, DIPLOMACY_NEUTRAL, DIPLOMACY_UNFRIENDLY, DIPLOMACY_HOSTILE]:
            raise ValueError(position +  " is not a leagal value for diplomatic position")
        temp = self.diplomacy[position]
        if party in temp:
            i = temp.index(party)
            del temp[i]

    def getRegion(self, x, y, ort):
        return self.getRegionByKey(RorRegion.makeRegionKey(x, y, ort))

    def getRegionByKey(self, key):
        if self.regions.has_key(key):
            return self.regions[key]
        else:
            return None

    def getUnits(self):
        """Liefert eine Liste aller Einheiten der AW."""
        units = []
        for region in self.regions.values():
            for building in region.sortedObjects:
                units += building.sortedUnits
        return units

    def getUnitsFromParty(self, partynr = None):
        """Gibt ohne Parameter die Einheiten der eigenen Partei zurueck."""
        units = {}
        regions = self.regions.values()
        for region in regions:
            for building in region.sortedObjects:
                for unit in building.sortedUnits:
                    if unit.partynumber == partynr:
                        units[unit.getKey()] = unit
        return units

    def getSortedRegionsAsList(self):
        sortedWorlds = {WORLD_RORQUAL: 0, WORLD_ABYSS: 1, WORLD_HOVECAN: 2, WORLD_ELYSIUM:3}
        worldCount   = len(sortedWorlds)
        regions      = self.regions.values()
        result       = [regions[0]]
        for r in regions:
            if not sortedWorlds.has_key(r.world):
                sortedWorlds[r.world] = worldCount
                worldCount += 1
        for x in regions[1:]:
            inserted = False
            for y in result:
                if (sortedWorlds[x.world] < sortedWorlds[y.world]):
                    inserted = True
                    index = result.index(y)
                    result.insert(index, x)
                    break
                elif (sortedWorlds[x.world] == sortedWorlds[y.world]):
                    if (x.y < y.y):
                        inserted = True
                        index = result.index(y)
                        result.insert(index, x)
                        break
                    elif (x.y == y.y):
                        if (x.x < y.x):
                            inserted = True
                            index = result.index(y)
                            result.insert(index, x)
                            break
            if not inserted:
                result += [x]
        return result

class RorBuilding(RorBaseObject):
    def __init__(self, cr = None):
        super(RorBuilding, self).__init__(cr)
        self.id =                -1
        self.region =            None
        self.size =              0
        self.maxSize =           0
        self.abk =               None
        self.singular =          None
        self.plural =            None
        self.types =             []
        self.underConstruction = False
        self.kbobj =             None
        self.expandableTo =      None
        self.canEnter = False
        self.description = None
        self.favour = None
        self.name = None
        self.units =             {}
        self.sortedUnits =       []
        self.hasRunes = False
        self.dir = None

    def __deepcopy__(self, memo):
        new = super(RorBuilding, self).__deepcopy__(memo)
        memo[id(self)] = new
        new.id = self.id
        new.region = deepcopy(self.region, memo)
        new.size = self.size
        new.maxSize = self.maxSize
        new.abk = self.abk
        new.singular = self.singular
        new.plural = self.plural
        new.types = deepcopy(self.types, memo)
        new.underConstruction = self.underConstruction
        new.kbobj = self.kbobj
        new.expandableTo = deepcopy(self.expandableTo, memo)
        new.canEnter = self.canEnter
        new.description = self.description
        new.favor = self.favour
        new.name = self.name
        new.units = deepcopy(self.units, memo)
        new.sortedUnits = deepcopy(self.sortedUnits, memo)
        new.hasRunes = self.hasRunes
        new.dir = self.dir
        return new

    def initFromCR(self, region, aw):
        self.id = self.cr.getSimpleValue(IDENT_OBJECT_KEY)
        self.region = region
        if self.cr.hasSimpleValue(IDENT_OBJECT_SIZE):
            self.size = self.cr.getSimpleValue(IDENT_OBJECT_SIZE)
        self.singular = self.cr.getSimpleValue(IDENT_OBJECT_SINGULAR)
        self.name = self.cr.getSimpleValue(IDENT_OBJECT_NAME)
        if self.id != 0:
            if (string.find(self.name, DIV_WALL) != -1): # PATCH: Name unterteilen in Walltyp und Richtung
                index = string.rindex(self.singular, " ")
                self.dir      = self.singular[index+1:]
                self.singular = self.singular[:index]
            self.kbobj = self.getKBObject()
            if self.kbobj is None:
                GetKB().addMissingBuilding(self.singular)
            else:
                self.initValuesFromKB()
            if (self.id > 9): # PATCH: Name eines Objektes ist grundsaetzlich als Variante des Textzahlpaars im CR angegeben
                self.name = self.name[:-5]
            else:
                self.name = self.name[:-4]
        else:
            self.singular = "Umland"
        cr_units = self.cr.getSubItem(IDENT_UNIT)
        self.description = self.cr.getSimpleValue(IDENT_OBJECT_DESCRIPTION)
        self.underConstruction = (self.maxSize > self.size)
        if self.cr.hasSimpleValue(IDENT_OBJECT_RUNES):
            self.hasRunes = (self.cr.getSimpleValue(IDENT_OBJECT_RUNES) == 1)
        region.objects[self.getKey()] = self
        region.sortedObjects += [self]
        if not cr_units is None:
            for cr_unit in cr_units:
                unit = RorUnit(cr_unit)
                unit.initFromCR(self.region, self, aw)
                self.units[unit.getKey()] = unit
                self.sortedUnits += [unit]
        self.cr.ignoreIdent(IDENT_OBJECT_UNTREADABLE)

    def initValuesFromKB(self):
        self.maxSize = self.kbobj.maxSize
        self.types = self.kbobj.types
        self.expandableTo = self.kbobj.expandableTo
        self.singular = self.kbobj.singular
        self.plural = self.kbobj.plural
        self.abk = self.kbobj.key
        self.canEnter = self.kbobj.canEnter
        self.favour = self.kbobj.favour

    def getKey(self):
        return self.id

    def getKeyAsString(self):
        return str(self.id)

    def getKBObject(self):
        kb = GetKB()
        return kb.findBuilding(self.singular)

    def hasType(self, type):
        return (type in self.types)

    def isHinterland(self):
        return (self.id == 0)

    def isExpandable(self):
        return not (self.expandableTo is None)

    def addUnit(self, unit):
        self.units[unit.getKey()] = unit
        self.sortedUnits += [unit]
        unit.object = self

    def delUnit(self, unit):
        del self.units[unit.getKey()]
        self.sortedUnits.remove(unit)

    def getUnitCountFromParty(self, partynumber):
        count = 0
        for unit in self.sortedUnits:
            if (unit.partynumber == partynumber):
                count += 1
        return count

    def getPersonAmountFromParty(self, partynumber):
        count = 0
        for unit in self.sortedUnits:
            if (unit.partynumber == partynumber):
                count += unit.getPersons()
        return count

class RorFleet(RorBaseObject):
    def __init__(self, region = None, id = None):
        super(RorFleet, self).__init__(None)
        self.id          = id
        self.region      = region
        self.encumbrance = 0
        self.encumbranceWithoutOwnWeight = {}
        self.talentlevel = 0
        self.sortedUnits = []
        self.bp          = {}
        self.capacity    = {}
        self.capacityWithoutOwnWeight = {}
        self.output = []
        self.usedBP      = 0
        self.minMove     = False
        if not (region is None): # abgefangen fuer __deepcopy__
            self.object = region.getHinterland()

    def __deepcopy__(self, memo):
        new = super(RorFleet, self).__deepcopy__(memo)
        memo[id(self)] = new
        new.id = self.id
        new.region = deepcopy(self.region, memo)
        new.encumbrance = self.encumbrance
        new.encumbranceWithoutOwnWeight = deepcopy(self.encumbranceWithoutOwnWeight, memo)
        new.talentlevel = self.talentlevel
        new.sortedUnits = deepcopy(self.sortedUnits, memo)
        new.bp = deepcopy(self.bp, memo)
        new.capacity = deepcopy(self.capacity, memo)
        new.capacityWithoutOwnWeight = deepcopy(self.capacityWithoutOwnWeight, memo)
        new.output = deepcopy(self.output, memo)
        new.usedBP = self.usedBP
        new.minMove = self.minMove
        new.object = self.object
        return new

    def getKey(self):
        return self.id

    def getKeyAsString(self):
        return str(self.id)

    def disembark(self, unit):
        self.sortedUnits.remove(unit)
        unit.fleetNumber = 0
        return

    def embark(self, unit):
        self.sortedUnits += [unit]
        unit.fleetNumber = self.id
        if (unit.object != self.object):
            unit.object.delUnit(unit)
            unit.object = self.region.getHinterland()
            unit.object.addUnit(unit)
        return

    def move(self, newRegion):
        if (self.bp[MOVE_FLYING] > 0):
            if (self.bp[MOVE_FLYING] < self.usedBP) and self.minMove:
                return 2
            elif (self.encumbrance > self.capacity[MOVE_FLYING]):
                return 3
        else:
            if (self.bp[MOVE_SWIMMING] < self.usedBP) and self.minMove:
                return 2
            elif (self.encumbrance > self.capacity[MOVE_SWIMMING]):
                return 3
        oldObject = self.sortedUnits[0].object
        newObject = newRegion.getHinterland()
        for unit in self.sortedUnits:
            oldObject.delUnit(unit)
            newObject.addUnit(unit)
            unit.region = newRegion
        self.region.fleets.remove(self)
        self.region = newRegion
        self.object = newRegion.getHinterland()
        newRegion.fleets += [self]
        self.minMove = True
        return 0

    def getMovementType(self):
        raise NotImplementedError("getMovementType")

    def calcEncumbrance(self):
        self.encumbrance = 0
        self.encumbranceWithoutOwnWeight[MOVE_SWIMMING] = 0
        self.encumbranceWithoutOwnWeight[MOVE_WALKING] = 0
        self.encumbranceWithoutOwnWeight[MOVE_RIDING] = 0
        self.encumbranceWithoutOwnWeight[MOVE_FLYING] = 0
        for unit in self.sortedUnits:
            itemList = unit.inventory.values()
            for item in itemList:
                if item.kbobj is None:
                    self.output += [Message(CAT_HINT, 145, para = (item.getKey()))]
                    continue
                self.encumbrance += (item.amount * item.weight)
                if (unit == self.sortedUnits[0]) and item.hasType(TYPE_P_SHIP):
                    continue
                capacity = item.kbobj.capacity
                self.encumbranceWithoutOwnWeight[MOVE_SWIMMING] += (item.amount * item.weight)
                self.encumbranceWithoutOwnWeight[MOVE_WALKING] += (item.amount * item.weight)
                self.encumbranceWithoutOwnWeight[MOVE_RIDING] += (item.amount * item.weight)
                self.encumbranceWithoutOwnWeight[MOVE_FLYING] += (item.amount * item.weight)

    def calcCapacity(self):
        self.capacity[MOVE_SWIMMING] = 0
        self.capacity[MOVE_WALKING] = 0
        self.capacity[MOVE_RIDING] = 0
        self.capacity[MOVE_FLYING] = 0
        self.capacityWithoutOwnWeight[MOVE_SWIMMING] = 0
        self.capacityWithoutOwnWeight[MOVE_WALKING] = 0
        self.capacityWithoutOwnWeight[MOVE_RIDING] = 0
        self.capacityWithoutOwnWeight[MOVE_FLYING] = 0
        captainItems = self.sortedUnits[0].inventory.values()
        for item in captainItems:
            if not item.hasType(TYPE_P_SHIP):
                continue
            capacity = item.kbobj.capacity
            if capacity == {}:
                continue
            if capacity.has_key(MOVE_SWIMMING):
                self.capacity[MOVE_SWIMMING] += (item.amount * (item.weight + capacity[MOVE_SWIMMING]))
                self.capacityWithoutOwnWeight[MOVE_SWIMMING] += (item.amount * capacity[MOVE_SWIMMING])
            if capacity.has_key(MOVE_WALKING):
                self.capacity[MOVE_WALKING] += (item.amount * (item.weight + capacity[MOVE_WALKING]))
                self.capacityWithoutOwnWeight[MOVE_WALKING] += (item.amount * capacity[MOVE_WALKING])
            if capacity.has_key(MOVE_RIDING):
                self.capacity[MOVE_RIDING] += (item.amount * (item.weight + capacity[MOVE_RIDING]))
                self.capacityWithoutOwnWeight[MOVE_RIDING] += (item.amount * capacity[MOVE_RIDING])
            if capacity.has_key(MOVE_FLYING):
                self.capacity[MOVE_FLYING] += (item.amount * (item.weight + capacity[MOVE_FLYING]))
                self.capacityWithoutOwnWeight[MOVE_FLYING] += (item.amount * capacity[MOVE_FLYING])

    def calcBP(self):
        self.bp[MOVE_SWIMMING] = -1
        self.bp[MOVE_WALKING] = -1
        self.bp[MOVE_RIDING] = -1
        self.bp[MOVE_FLYING] = -1
        captainItems = self.sortedUnits[0].inventory.values()
        for item in captainItems:
            if not item.hasType(TYPE_P_SHIP):
                continue
            bp = item.kbobj.bp
            if bp == {}:
                continue
            if bp.has_key(MOVE_SWIMMING):
                if (self.bp[MOVE_SWIMMING] > bp[MOVE_SWIMMING]) or (self.bp[MOVE_SWIMMING] == -1):
                    self.bp[MOVE_SWIMMING] = bp[MOVE_SWIMMING]
            else:
                self.bp[MOVE_SWIMMING] = 0
            if bp.has_key(MOVE_WALKING):
                if (self.bp[MOVE_WALKING] > bp[MOVE_WALKING]) or (self.bp[MOVE_WALKING] == -1):
                    self.bp[MOVE_WALKING] = bp[MOVE_WALKING]
            else:
                self.bp[MOVE_WALKING] = 0
            if bp.has_key(MOVE_RIDING):
                if (self.bp[MOVE_RIDING] > bp[MOVE_RIDING]) or (self.bp[MOVE_RIDING] == -1):
                    self.bp[MOVE_RIDING] = bp[MOVE_RIDING]
            else:
                self.bp[MOVE_RIDING] = 0
            if bp.has_key(MOVE_FLYING):
                if (self.bp[MOVE_FLYING] > bp[MOVE_FLYING]) or (self.bp[MOVE_FLYING] == -1):
                    self.bp[MOVE_FLYING] = bp[MOVE_FLYING]
            else:
                self.bp[MOVE_FLYING] = 0

    def getUnitCountFromParty(self, partynumber):
        count = 0
        for unit in self.sortedUnits:
            if (unit.partynumber == partynumber):
                count += 1
        return count

    def getPersonAmountFromParty(self, partynumber):
        count = 0
        for unit in self.sortedUnits:
            if (unit.partynumber == partynumber):
                count += unit.getPersons()
        return count

    def getShipItem(self):
        items = self.sortedUnits[0].inventory.values()
        for i in items:
            if i.hasType(TYPE_P_SHIP):
                return i
        return None

    def hasUnitsFromParty(self, nr):
        for unit in self.sortedUnits:
            if unit.partynumber == nr:
                return True
        return False

class RorHomestead(RorBaseObject):
    def __init__(self, cr = None):
        super(RorHomestead, self).__init__(cr)
        self.region      = None
        self.name        = ""
        self.type        = ""
        self.size        = 0
        self.isSupported = False

    def __deepcopy__(self, memo):
        new = super(RorHomestead, self).__deepcopy__(memo)
        memo[id(self)] = new
        new.region = deepcopy(self.region, memo)
        new.name = self.name
        new.type = self.type
        new.size = self.size
        new.isSupported = self.isSupported
        return new

    def initFromCR(self, region):
        self.region = region
        self.name = self.cr.getSimpleValue(IDENT_HOMESTEAD_NAME)
        self.type = self.cr.getSimpleValue(IDENT_HOMESTEAD_TYPE)
        # self.size = self.cr.getSimpleValue(IDENT_HOMESTEAD_POPULATION)
        # PATCH: verschoben wegen cr-Fehler nach RorRegion

    def getPPCost(self):
        if (self.type == TYPE_HS_ABANDONED_VILLAGE): cost =  0
        elif (self.type == TYPE_HS_SETTLEMENT):      cost =  1
        elif (self.type == TYPE_HS_SMALL_VILLAGE):   cost =  2
        elif (self.type == TYPE_HS_VILLAGE):         cost =  3
        elif (self.type == TYPE_HS_SMALL_TOWN):      cost =  4
        elif (self.type == TYPE_HS_CITY):            cost =  6
        elif (self.type == TYPE_HS_LARGE_CITY):      cost =  8
        elif (self.type == TYPE_HS_METROPOLIS):      cost = 10
        else:
            self.region.output += [Message(CAT_WARN, 140)]
            cost = 0
        return cost

def makeDirection(s):
    if (s == "Norden"):
        return DIR_NORTH
    elif (s == "Sueden"):
        return DIR_SOUTH
    elif (s == "Nordosten"):
        return DIR_NORTHEAST
    elif (s == "Nordwesten"):
        return DIR_NORTHWEST
    elif (s == "Suedosten"):
        return DIR_SOUTHEAST
    elif (s == "Suedwesten"):
        return DIR_SOUTHWEST
    return None

class RorLanes(RorBaseObject):
    def __init__(self, cr = None):
        super(RorLanes, self).__init__(cr)
        self.direction = None
        self.x = 0
        self.y = 0
        self.world = ""
        self.terrain = ""
        self.name = ""
        self.province = ""
        self.homestead = None
        self.wall = None
        self.ban = False

    def __deepcopy__(self, memo):
        new = super(RorLanes, self).__deepcopy__(memo)
        new.direction = self.direction
        new.x = self.x
        new.y = self.y
        new.world = self.world
        new.terrain = self.terrain
        new.name = self.name
        new.province = self.province
        new.homestead = deepcopy(self.homestead, memo)
        new.wall = deepcopy(self.wall, memo)
        new.ban = self.ban
        return new

    def initFromCR(self):
        self.x = self.cr.getSimpleValue(IDENT_LANE_X)
        self.y = self.cr.getSimpleValue(IDENT_LANE_Y)
        self.world = self.cr.getSimpleValue(IDENT_LANE_WORLD)
        self.terrain = self.cr.getSimpleValue(IDENT_LANE_TERRAIN)
        self.wall = self.cr.getSimpleValue(IDENT_LANE_WALL)
        if self.cr.hasSimpleValue(IDENT_LANE_NAME):
            self.name = self.cr.getSimpleValue(IDENT_LANE_NAME)
        if self.cr.hasSimpleValue(IDENT_LANE_PROVINCE):
            self.province = self.cr.getSimpleValue(IDENT_LANE_PROVINCE)
        if self.cr.hasSimpleValue(IDENT_LANE_HOMESTEAD_TYPE):
            self.homestead = RorHomestead()
            self.homestead.type = self.cr.getSimpleValue(IDENT_LANE_HOMESTEAD_TYPE)
            self.homestead.name = self.cr.getSimpleValue(IDENT_LANE_HOMESTEAD)
        if self.cr.hasSimpleValue(IDENT_LANE_FLAG_BAN):
            self.ban = (self.cr.getSimpleValue(IDENT_LANE_FLAG_BAN) == 1)
        dir = self.cr.getSimpleValue(IDENT_LANE_DIRECTION)
        self.direction = makeDirection(dir)

    def getKey(self):
        return self.direction

    def getKeyAsString(self):
        return str(self.direction)

class RorWall(RorBaseObject):
    def __init__(self, cr = None):
        super(RorWall, self).__init__(cr)
        self.direction = None
        self.type = ""

    def __deepcopy__(self, memo):
        new = super(RorWall, self).__deepcopy__(memo)
        memo[id(self)] = new
        new.direction = self.direction
        new.type = self.type
        return new

    def initFromCR(self):
        self.type = self.cr.getSimpleValue(IDENT_WALL_TYPE)
        dir = self.cr.getSimpleValue(IDENT_WALL_DIRECTION)
        self.direction = makeDirection(dir)

    def getKey(self):
        return self.direction

    def getKeyAsString(self):
        return str(self.direction)

class RorProduct(RorBaseObject):
    def __init__(self, cr = None):
        super(RorProduct, self).__init__(cr)
        self.id =           None
        self.singular =     None
        self.plural =       None
        self.amount =       0
        self.keepAmount =   0
        self.tradedAmount = 0
        self.weight =       0
        self.cost =         0
        self.types =        []
        self.kbobj = None
        self.optableRace = False
        self.livelihood = 0

    def __deepcopy__(self, memo):
        new = super(RorProduct, self).__deepcopy__(memo)
        new.id = self.id
        new.singular= self.singular
        new.plural = self.plural
        new.amount = self.amount
        new.keepAmount = self.keepAmount
        new.tradedAmount = self.tradedAmount
        new.weight = self.weight
        new.cost = self.cost
        new.types = deepcopy(self.types, memo)
        new.kbobj = self.kbobj
        new.optableRace = self.optableRace
        new.livelihood = self.livelihood
        return new

    def initFromCR(self):
        self.id = self.cr.getSimpleValue(IDENT_PRODUCT_KEY)
        if self.cr.hasSimpleValue(IDENT_PRODUCT_NAME2):
            self.singular =  self.cr.getSimpleValue(IDENT_PRODUCT_NAME2)
        self.amount = self.cr.getSimpleValue(IDENT_PRODUCT_AMOUNT1)
        if self.amount is None:
            self.amount = self.cr.getSimpleValue(IDENT_PRODUCT_AMOUNT2)
        if self.amount is None:
            self.amount = 0
        if self.cr.hasSimpleValue(IDENT_PRODUCT_COST):
            self.cost = self.cr.getSimpleValue(IDENT_PRODUCT_COST)
        self.kbobj = self.getKBObject()
        if not self.kbobj is None:
            self.initValuesFromKB()
        else:
            GetKB().addMissingProduct(self.singular)
            self.singular = "unbekannt: " + self.id
            self.plural   = "unbekannt: " + self.id
        self.cr.ignoreIdent(IDENT_PRODUCT_WEIGHT)
        self.cr.ignoreIdent(IDENT_PRODUCT_NAME1)

    def initValuesFromKB(self):
        if self.id is None:
            self.id = self.kbobj.key
        self.singular = self.kbobj.singular
        self.plural = self.kbobj.plural
        self.weight = self.kbobj.weight
        self.types = self.kbobj.types
        self.optableRace = self.kbobj.optableRace
        self.livelihood = self.kbobj.livelihood

    def getKey(self):
        return self.id

    def getKeyAsString(self):
        return self.id

    def getKBObject(self):
        kb = GetKB()
        product = kb.findProduct(self.id)
        if product is None:
            product = kb.findProduct(self.singular)
        return product

    def hasType(self, type):
        return (type in self.types)

    def getName(self):
        if self.amount == 1:
            return self.singular
        return self.plural

class RorRegion(RorBaseObject):
    def makeRegionKey(x, y, ort):
        "Hilfsfunktion: Erzeugt den Key fuer Regionen aus X-un Y-Koordinate und Ort."
        return "(" + str(x) + "," + str(y) + "," + str(ort) + ")"
    makeRegionKey = staticmethod(makeRegionKey)

    def __init__(self, cr = None):
        super(RorRegion, self).__init__(cr)
        self.objects = {}
        self.sortedObjects = []
        self.producable  =  KeyInsensitiveDict() # Produzierbare Waren
        self.purchases   =  KeyInsensitiveDict()
        self.sales =  KeyInsensitiveDict()
        self.lanes =  KeyInsensitiveDict()
        self.walls = KeyInsensitiveDict()
        self.IncomeWork = 0
        self.IncomeEntertainment = 0
        self.IncomeTaxes = 0
        self.IncomeWorkUsed = 0
        self.IncomeEntertainmentUsed = 0
        self.IncomeTaxesUsed = 0
        self.MoneyLearning = 0
        self.MoneyPurchases = 0
        self.MoneySales = 0
        self.MoneyLivelihood = 0
        self.isSettled = False
        self.isConquered = False
        self.isSupported = False
        self.isPlundered = False
        self.ppTrade = False
        self.ppWar = False
        self.name = None
        self.fleets = []
        self.terrain = None
        self.world = None
        self.x = 0
        self.y = 0
        self.wages = 0
        self.homestead = None
        self.race = None
        self.ownerNumber = 0
        self.ownerName = None
        self.province = None
        self.peasants = 0
        self.population = 0
        self.maxPopulation = False
        self.weather = None
        self.jobs = 0
        self.minder = []
        self.isShortReport = False
        self.output = []
        self.dimensionGate = 0
        self.buildingCost = 0
        self.ownProducts = []
        self.sum_leaders = 0
        self.sum_regulars = 0
        self.sum_livelihood = 0
        self.last_taxes = 0
        self.last_entertainment = 0
        self.last_work = 0

    def __deepcopy__(self, memo):
        new = super(RorRegion, self).__deepcopy__(memo)
        memo[id(self)] = new
        new.objects = deepcopy(self.objects, memo)
        new.sortedObjects = deepcopy(self.sortedObjects, memo)
        new.producable = deepcopy(self.producable, memo)
        new.purchases = deepcopy(self.purchases, memo)
        new.sales = deepcopy(self.sales, memo)
        new.lanes = deepcopy(self.lanes, memo)
        new.walls = deepcopy(self.walls, memo)
        new.IncomeWork = self.IncomeWork
        new.IncomeEntertainment = self.IncomeEntertainment
        new.IncomeTaxes = self.IncomeTaxes
        new.IncomeWorkUsed = self.IncomeWorkUsed
        new.IncomeEntertainmentUsed = self.IncomeEntertainmentUsed
        new.IncomeTaxesUsed = self.IncomeTaxesUsed
        new.MoneyLearning = self.MoneyLearning
        new.MoneyPurchases = self.MoneyPurchases
        new.MoneySales = self.MoneySales
        new.MoneyLivelihood = self.MoneyLivelihood
        new.isSettled = self.isSettled
        new.isConquered = self.isConquered
        new.isSupported = self.isSupported
        new.isPlundered = self.isPlundered
        new.ppTrade = self.ppTrade
        new.ppWar = self.ppWar
        new.name = self.name
        new.fleets = deepcopy(self.fleets, memo)
        new.terrain = self.terrain
        new.world = self.world
        new.x = self.x
        new.y = self.y
        new.wages = self.wages
        new.homestead = deepcopy(self.homestead, memo)
        new.race = self.race
        new.ownerNumber = self.ownerNumber
        new.ownerName = self.ownerName
        new.province = self.province
        new.peasants = self.peasants
        new.population = self.population
        new.maxPopulation = self.maxPopulation
        new.weather = self.weather
        new.jobs = self.jobs
        new.minder = deepcopy(self.minder, memo)
        new.isShortReport = self.isShortReport
        new.output = deepcopy(self.output, memo)
        new.dimensionGate = self.dimensionGate
        new.buildingCost = self.buildingCost
        new.ownProducts = deepcopy(self.ownProducts, memo)
        new.sum_leaders = self.sum_leaders
        new.sum_regulars = self.sum_regulars
        new.sum_livelihood = self.sum_livelihood
        new.last_taxes = self.last_taxes
        new.last_entertainment = self.last_entertainment
        new.last_work = self.last_work
        return new

    def getKey(self):
        return RorRegion.makeRegionKey(self.x, self.y, self.world)

    def getKeyAsString(self):
        return RorRegion.makeRegionKey(self.x, self.y, self.world)

    def initFromCR(self, aw):
        self.x = self.cr.getSimpleValue(IDENT_REGION_X)
        self.y = self.cr.getSimpleValue(IDENT_REGION_Y)
        self.world = self.cr.getSimpleValue(IDENT_REGION_WORLD)
        self.terrain = self.cr.getSimpleValue(IDENT_REGION_TERRAIN)
        self.name = self.cr.getSimpleValue(IDENT_REGION_NAME)
        self.province = self.cr.getSimpleValue(IDENT_REGION_PROVINCE)
        self.peasants = self.cr.getSimpleValue(IDENT_REGION_PEASANTS)
        self.race = self.cr.getSimpleValue(IDENT_REGION_RACE)
        self.population  = self.cr.getSimpleValue(IDENT_REGION_POPULATION)
        self.maxPopulation = self.cr.getSimpleValue(IDENT_REGION_MAX_POPULATION)
        if self.cr.hasSimpleValue(IDENT_REGION_TAXES):
            self.IncomeTaxes = self.cr.getSimpleValue(IDENT_REGION_TAXES)
        self.wages = self.cr.getSimpleValue(IDENT_REGION_WAGES)
        if self.cr.hasSimpleValue(IDENT_REGION_MAX_WORK):
            self.IncomeWork = self.cr.getSimpleValue(IDENT_REGION_MAX_WORK)
        if self.cr.hasSimpleValue(IDENT_REGION_ENTERTAINMENT):
            self.IncomeEntertainment = self.cr.getSimpleValue(IDENT_REGION_ENTERTAINMENT)
        self.weather = self.cr.getSimpleValue(IDENT_REGION_WEATHER)
        self.jobs = self.cr.getSimpleValue(IDENT_REGION_JOBS)
        if self.cr.hasSimpleValue(IDENT_REGION_DIMGATE):
            self.dimensionGate = self.cr.getSimpleValue(IDENT_REGION_DIMGATE)
        else:
            self.dimensionGate = 0
        if self.cr.hasSimpleValue(IDENT_REGION_BUILD_COST):
            self.buildingCost = self.cr.getSimpleValue(IDENT_REGION_BUILD_COST)
        territory = self.cr.getSimpleValue(IDENT_REGION_TERRITORY)
        if not territory is None:
            self.ownerNumber = territory[1]
            self.ownerName = territory[0][:-1]
        if self.cr.hasSimpleValue(IDENT_REGION_MINDER):
            self.minder = self.cr.getSimpleValue(IDENT_REGION_MINDER)
        self.isShortReport = self.cr.getSimpleValue(IDENT_REGION_SHORT_REPORT)
        temp = self.cr.getSubItem(IDENT_REGION_PRODUCTS)
        if not temp is None:
            for p in temp:
                rorProduct = RorProduct(p)
                rorProduct.initFromCR()
                self.producable[rorProduct.getKeyAsString()] = rorProduct
        temp = self.cr.getSubItem(IDENT_REGION_SALE)
        if not temp is None:
            for p in temp:
                rorProduct = RorProduct(p)
                rorProduct.initFromCR()
                self.sales[rorProduct.getKeyAsString()] = rorProduct
        temp = self.cr.getSubItem(IDENT_REGION_PURCHASE)
        if not temp is None:
            for p in temp:
                rorProduct = RorProduct(p)
                rorProduct.initFromCR()
                self.purchases[rorProduct.getKeyAsString()] = rorProduct
        temp = self.cr.getSubItem(IDENT_REGION_WAYS)
        if not temp is None:
            for p in temp:
                o = RorLanes(p)
                o.initFromCR()
                self.lanes[o.getKeyAsString()] = o
        temp = self.cr.getSubItem(IDENT_REGION_WALL)
        if not temp is None:
            for p in temp:
                o = RorWall(p)
                o.initFromCR()
                self.walls[o.getKeyAsString()] = o
        temp = self.cr.getSingleSubItem(IDENT_HOMESTEAD)
        if not temp is None:
            self.homestead = RorHomestead(temp)
            self.homestead.initFromCR(self)
            # PATCH: Folgende Zeile ist ein Patch, gehoert nach RorHomestead.initFromCR()
            self.homestead.size = self.cr.getSimpleValue(IDENT_HOMESTEAD_POPULATION)
        temp = self.cr.getSingleSubItem(IDENT_REGION_HINTERLAND)
        if not temp is None:
            hinterland = RorBuilding(temp)
            hinterland.initFromCR(self, aw)
        else:
            hinterland = RorBuilding()
            hinterland.id = 0
            hinterland.singular = "Umland"
            self.sortedObjects = [hinterland]
            self.objects[hinterland.getKey()] = hinterland
        temp = self.cr.getSubItem(IDENT_OBJECT)
        if not temp is None:
            for p in temp:
                o = RorBuilding(p)
                o.initFromCR(self, aw)
        temp = self.cr.getSingleSubItem(IDENT_REGION_OWN)
        if not temp is None:
            self.initOwn(aw, temp)
        
    def initOwn(self, aw, crobj):
        kb = GetKB()
        self.sum_leaders = crobj.getSimpleValue(IDENT_OWN_SUM_LEADER)
        self.sum_regulars = crobj.getSimpleValue(IDENT_OWN_SUM_REGULARS)
        self.sum_livelihood = crobj.getSimpleValue(IDENT_OWN_LIVELIHOOD)
        if crobj.hasSimpleValue(IDENT_OWN_LAST_TAXES):
            self.last_taxes = crobj.getSimpleValue(IDENT_OWN_LAST_TAXES)
        if crobj.hasSimpleValue(IDENT_OWN_LAST_ENTERTAINMENT):
            self.last_entertainment = crobj.getSimpleValue(IDENT_OWN_LAST_ENTERTAINMENT)
        if crobj.hasSimpleValue(IDENT_OWN_LAST_WORK):
            self.last_work = crobj.getSimpleValue(IDENT_OWN_LAST_WORK)
        objlist = crobj.getAllSubItems()
        for obj in objlist:
            key = obj.getKey()
            if not key in [IDENT_OWN_SUM_LEADER, IDENT_OWN_SUM_REGULARS, IDENT_OWN_LIVELIHOOD, IDENT_OWN_LAST_TAXES]:
                try:
                    obj.visited = True
                    name = key
                    amount = int(obj)
                    p = RorProduct()
                    p.kbobj = kb.findProduct(name)
                    if not p.kbobj is None:
                        p.initValuesFromKB()
                        p.amount = amount
                    self.ownProducts += [p]
                except TypeError:
                    obj.visited = False

    def initFromLane(self, lane):
        self.x = lane.x
        self.y = lane.y
        self.world = lane.world
        self.terrain = lane.terrain
        self.name = lane.name
        self.province = lane.province
        self.homestead = lane.homestead

    def getNeighbour(self, direction, aw):
        x = self.x
        y = self.y
        if (direction.value == DIR_NORTH):
            y = y - 2
        elif (direction.value == DIR_NORTHWEST):
            y = y - 1
            x = x - 1
        elif (direction.value == DIR_SOUTHWEST):
            y = y + 1
            x = x - 1
        elif (direction.value == DIR_SOUTH):
            y = y + 2
        elif (direction.value == DIR_SOUTHEAST):
            y = y + 1
            x = x + 1
        elif (direction.value == DIR_NORTHEAST):
            y = y - 1
            x = x + 1
        #TODO: Weltengrenzen beachten!!!
        #TODO: Bei Reise pruefen, ob Tunnel vorhanden sind!
        r = aw.getRegion(x, y, self.world)
        if r is None:
            r = RorRegion()
            r.x = x
            r.y = y
            r.world = self.world
            r.terrain = "unbekannt"
            hinterland = RorBuilding()
            hinterland.id = 0
            hinterland.singular = "Umland"
            r.sortedObjects = [hinterland]
            r.objects[hinterland.getKey()] = hinterland
            if self.lanes.has_key(direction.value):
                lane = self.lanes[direction.value]
                r.initFromLane(lane)
            aw.regions[r.getKey()] = r
        return r

    def getUnit(self, key = None):
        if key is None:
            lst = {}
            for object in self.sortedObjects:
                for unit in object.sortedUnits:
                    lst[unit.getKey()] = unit
            return lst
        else:
            for object in self.sortedObjects:
                for unit in object.sortedUnits:
                    if unit.getKey() == key:
                        return unit

    def getUnitByName(self, name):
        for object in self.sortedObjects:
            for unit in object.sortedUnits:
                if unit.name == name:
                    return unit
        return None

    def getUnitsFromParty(self, partynumber):
        lst = {}
        for object in self.sortedObjects:
            for unit in object.sortedUnits:
                if (unit.partynumber == partynumber):
                    lst[unit.getKey()] = unit
        return lst

    def getUnitsFromPartyAsList(self, partynumber):
        lst = []
        for object in self.sortedObjects:
            for unit in object.sortedUnits:
                if unit.partynumber == partynumber:
                    lst += [unit]
        return lst

    def getUnitCountFromParty(self, partynumber):
        count = 0
        for object in self.sortedObjects:
            for unit in object.sortedUnits:
                if (unit.partynumber == partynumber):
                    count += 1
        return count

    def getPersonAmountFromParty(self, partynumber):
        count = 0
        for object in self.sortedObjects:
            for unit in object.sortedUnits:
                if (unit.partynumber == partynumber):
                    count += unit.getPersons()
        return count

    def getAllUnits(self):
        lst = []
        for object in self.sortedObjects:
            lst += object.sortedUnits
        return lst

    def getUnitsAsKeylist(self):
        raise NotImplementedError("getUnitsAsKeyList")

    def isTerritory(self, partynr):
        return self.ownerNumber == partynr

    def getProductsFromParty(self, partynumber):
        lst = KeyInsensitiveDict()
        ownUnits = self.getUnitsFromPartyAsList(partynumber)
        for unit in ownUnits:
            items = unit.inventory.values()
            for i in items:
                key = i.getKey()
                if not lst.has_key(key):
                    newProduct = RorProduct()
                    newProduct.id = key
                    newProduct.kbobj = newProduct.getKBObject()
                    newProduct.amount = 0
                    if not newProduct.kbobj is None:
                        newProduct.initValuesFromKB()
                    else:
                        newProduct.singular = key
                        newProduct.plural = key
                    lst[key] = newProduct
                lst[key].amount += i.amount
        return lst

    def isGuarded(self, aw, partynr = None):
        """Funktion gibt an, ob ein Reich ungleich des eigenen die Region bewacht, wenn kein Parameter uebergeben wird.
        Wenn ein Parameter angegeben wird, liefert die Funktion ob das angegebene Reich bewacht.
        """
        if partynr is None:
            for x in self.minder:
                if x == aw.partynumber:
                    return True
        else:
            for x in self.minder:
                if x == aw.partynumber:
                    return True
        return False

    def getMovementCost(self, forFleet = False):
        if (self.weather is None):
            factor = 1
        elif (string.find(self.weather, DIV_WEATHER) != -1):
            factor = 1
        else:
            factor = 2
        if (self.terrain == TYPE_TER_OCEAN):
            cost = 1
        elif forFleet:
            cost = 1
        elif (self.terrain == TYPE_TER_PLAIN):
            cost = 1
        elif (self.terrain == TYPE_TER_HIGHLANDS):
            cost = 1
        elif (self.terrain == TYPE_TER_CAVERN):
            cost = 1
        elif (self.terrain == TYPE_TER_DESERT):
            cost = 2
        elif (self.terrain == TYPE_TER_MOUNTAINS):
            cost = 2
        elif (self.terrain == TYPE_TER_JUNGLE):
            cost = 2
        elif (self.terrain == TYPE_TER_SWAMP):
            cost = 2
        elif (self.terrain == TYPE_TER_TUNDRA):
            cost = 2
        elif (self.terrain == TYPE_TER_TUNNEL):
            cost = 2
        elif (self.terrain == TYPE_TER_SUBMONTANE_FOREST):
            cost = 2
        elif (self.terrain == TYPE_TER_FOREST):
            cost = 2
        else:
            cost = 1
        return (factor * cost)

    def getPPCost(self):
        if (self.terrain == TYPE_TER_PLAIN):
            cost = 4
        elif (self.terrain == TYPE_TER_HIGHLANDS):
            cost = 2
        elif (self.terrain == TYPE_TER_DESERT):
            cost = 1
        elif (self.terrain == TYPE_TER_MOUNTAINS):
            cost = 2
        elif (self.terrain == TYPE_TER_JUNGLE):
            cost = 1
        elif (self.terrain == TYPE_TER_SWAMP):
            cost = 1
        elif (self.terrain == TYPE_TER_TUNDRA):
            cost = 1
        elif (self.terrain == TYPE_TER_FOREST):
            cost = 2
        elif (self.terrain == TYPE_TER_ABYSS):
            cost = 1
        elif (self.terrain == TYPE_TER_CAVERN):
            cost = 0
        elif (self.terrain == TYPE_TER_OCEAN):
            cost = 0
        elif (self.terrain == TYPE_TER_TUNNEL):
            cost = 0
        elif (self.terrain == TYPE_TER_SUBMONTANE_FOREST):
            cost = 0
        else:
            self.output += [Message(CAT_WARN, 139)]
            cost = 0
        return cost

    def getHinterland(self):
        return self.sortedObjects[0]

    def getFleet(self, key):
        for f in self.fleets:
            if f.getKey() == key:
                return f
        return None

class RorTalent(RorBaseObject):
    def __init__(self, cr = None):
        super(RorTalent, self).__init__(cr)
        self.id = None
        self.name = None
        self.learningFee = 0
        self.types = []
        self.level = 0
        self.xp = 0
        self.title = None
        self.kbobj = None

    def __deepcopy__(self, memo):
        new = super(RorTalent, self).__deepcopy__(memo)
        new.id = self.id
        new.name = self.name
        new.learningFee = self.learningFee
        new.types = deepcopy(self.types, memo)
        new.level = self.level
        new.xp = self.xp
        new.title = self.title
        new.kbobj = self.kbobj
        return new

    def initFromCR(self):
        self.id = self.cr.getSimpleValue(IDENT_TALENT_KEY)
        if self.cr.hasSimpleValue(IDENT_TALENT_LEVEL):
            self.level = self.cr.getSimpleValue(IDENT_TALENT_LEVEL)
        if self.cr.hasSimpleValue(IDENT_TALENT_XP):
            self.xp = self.cr.getSimpleValue(IDENT_TALENT_XP)
        if self.cr.hasSimpleValue(IDENT_TALENT_TITEL):
            self.title = self.cr.getSimpleValue(IDENT_TALENT_TITEL)
        if self.cr.hasSimpleValue(IDENT_TALENT_NAME):
            self.name = self.cr.getSimpleValue(IDENT_TALENT_NAME)
        self.kbobj = self.getKBObject()
        if self.kbobj is None:
            GetKB().addMissingTalent(self.name)
        else:
            self.initValuesFromKB()

    def initValuesFromKB(self):
        if self.id is None:
            self.id = self.kbobj.key
        self.name = self.kbobj.singular
        self.learningFee = self.kbobj.learningFee
        self.types = self.kbobj.types

    def getKey(self):
        return self.id

    def getKeyAsString(self):
        return self.id

    def getKBObject(self):
        kb = GetKB()
        if not self.id is None:
          return kb.findTalent(self.id)
        return kb.findTalent(self.name)

    def hasType(self, type):
        return (type in self.types)

class RorUnit(RorBaseObject):
    def __init__(self, cr = None):
        super(RorUnit, self).__init__(cr)
        self.fleetNumber = 0
        self.flags = {}
        self.commands = []
        self.output    = []
        self.inventory    =  KeyInsensitiveDict()
        self.talents   =  KeyInsensitiveDict()
        self.encumbrance = 0
        self.encumbranceWithoutOwnWeight = {MOVE_SWIMMING:0, MOVE_WALKING:0, MOVE_RIDING:0, MOVE_FLYING:0}
        self.usedCapacity = {MOVE_SWIMMING:0, MOVE_WALKING:0, MOVE_RIDING:0, MOVE_FLYING:0}
        self.capacity = {MOVE_SWIMMING:0, MOVE_WALKING:0, MOVE_RIDING:0, MOVE_FLYING:0}
        self.capacityWithoutOwnWeight = {MOVE_SWIMMING:0, MOVE_WALKING:0, MOVE_RIDING:0, MOVE_FLYING:0}
        self.bp = {MOVE_SWIMMING:0, MOVE_WALKING:0, MOVE_RIDING:0, MOVE_FLYING:0}
        self.learnable = KeyInsensitiveDict()
        self.name      = None
        self.object = None
        self.region    = None
        self.combatSpell = None
        self.limitWeight = 0
        self.longCommand = ""
        self.learnedTalent = ""
        self.teachedPersons = 0
        self.rougeCommands = 0
        self.advancing = False
        self.id = 0
        self.partynumber = 0
        self.partyname = None
        self.isSacrificed = False
        self.isSurrendered = False
        self.isPlundering = False
        self.isTeached = False
        self.hasConjured = False
        self.settlingProgress = 0
        self.conqueringProgress = 0
        self.description = None
        self.isTaxing = False
        self.expartynumber = 0
        self.expartyname = None
        self.maskerade = None
        self.usedBP = 0
        self.minMove = False
        self.status = []

    def __deepcopy__(self, memo):
        new = super(RorUnit, self).__deepcopy__(memo)
        memo[id(self)] = new
        new.fleetNumber = self.fleetNumber
        new.flags = deepcopy(self.flags, memo)
        new.commands = deepcopy(self.commands, memo)
        new.output = deepcopy(self.output, memo)
        new.inventory = deepcopy(self.inventory, memo)
        new.talents = deepcopy(self.talents, memo)
        new.encumbrance = self.encumbrance
        new.encumbranceWithoutOwnWeight = deepcopy(self.encumbranceWithoutOwnWeight, memo)
        new.usedCapacity = deepcopy(self.usedCapacity, memo)
        new.capacity = deepcopy(self.capacity, memo)
        new.capacityWithoutOwnWeight = deepcopy(self.capacityWithoutOwnWeight, memo)
        new.bp = deepcopy(self.bp, memo)
        new.learnable = deepcopy(self.learnable, memo)
        new.name = self.name
        new.object = deepcopy(self.object, memo)
        new.region = deepcopy(self.region, memo)
        new.combatSpell = deepcopy(self.combatSpell, memo)
        new.limitWeight = self.limitWeight
        new.longCommand = self.longCommand
        new.learnedTalent = self.learnedTalent
        new.teachedPersons = self.teachedPersons
        new.rougeCommands = self.rougeCommands
        new.advancing = self.advancing
        new.id = self.id
        new.partynumber = self.partynumber
        new.partyname = self.partyname
        new.isSacrificed = self.isSacrificed
        new.isSurrendered = self.isSurrendered
        new.isPlundering = self.isPlundering
        new.isTeached = self.isTeached
        new.hasConjured = self.hasConjured
        new.settlingProgress = self.settlingProgress
        new.conqueringProgress = self.conqueringProgress
        new.description = self.description
        new.isTaxing = self.isTaxing
        new.expartynumber = self.expartynumber
        new.expartyname = self.expartyname
        new.maskerade = self.maskerade
        new.usedBP = self.usedBP
        new.minMove = self.minMove
        new.status = self.status
        return new

    def initFromCR(self, region, object, aw):
        self.object = object
        self.region = region
        if self.cr.hasSimpleValue(IDENT_UNIT_SETTLING):
            self.settlingProgress = self.cr.getSimpleValue(IDENT_UNIT_SETTLING)
        self.description = self.cr.getSimpleValue(IDENT_UNIT_DESCRIPTION)
        if self.cr.hasSimpleValue(IDENT_UNIT_CONQUERING):
            self.conqueringProgress = self.cr.getSimpleValue(IDENT_UNIT_CONQUERING)
        self.name = self.cr.getSimpleValue(IDENT_UNIT_NAME)[0][:-1]
        self.id = self.cr.getSimpleValue(IDENT_UNIT_KEY)
        self.maskerade = self.cr.getSimpleValue(IDENT_UNIT_MASKERADE)
        party = self.cr.getSimpleValue(IDENT_UNIT_PARTY)
        if not party is None:
            self.partynumber = party[1]
            self.partyname = party[0][:-1]
        exparty = self.cr.getSimpleValue(IDENT_UNIT_EXPARTYNAME)
        if not exparty is None:
            self.expartynumber = self.cr.getSimpleValue(IDENT_UNIT_EXPARTYNUMBER)
            self.expartyname = exparty[0][:-1]
        cr_inventory = self.cr.getSubItem(IDENT_UNIT_INVENTORY)
        if not cr_inventory is None:
            for cr_product in cr_inventory:
                p = RorProduct(cr_product)
                p.initFromCR()
                self.inventory[p.id] = p
        cr_talente = self.cr.getSubItem(IDENT_UNIT_TALENT)
        if not cr_talente is None:
            for cr_talent in cr_talente:
                p = RorTalent(cr_talent)
                p.initFromCR()
                self.talents[p.id] = p
        temp = self.cr.getSingleSubItem(IDENT_UNIT_LEARNABLE)
        if not temp is None:
            cr_talente = temp.getSubItem(IDENT_UNIT_TALENT)
            if not (cr_talente is None):
                for cr_talent in cr_talente:
                    p = RorTalent(cr_talent)
                    p.initFromCR()
                    self.learnable[p.id] = p
        temp = self.cr.getSimpleValue(IDENT_UNIT_COMBAT_SPELL)
        if not temp is None:
            p = RorTalent()
            p.name = temp
            p.kbobj = p.getKBObject()
            if p.kbobj is None:
                print "Unbekannter Kampfzauber: " + temp
                GetKB().output += [Message(CAT_ERR, 153, para = (temp))]
            else:
                p.initValuesFromKB()
            self.combatSpell = p
        if self.cr.hasSimpleValue(IDENT_UNIT_CONSUME_UNIT):
            self.flags[FLAG_CONSUME_UNIT] = self.cr.getSimpleValue(IDENT_UNIT_CONSUME_UNIT)
        if self.cr.hasSimpleValue(IDENT_UNIT_CONSUME_PARTY):
            self.flags[FLAG_CONSUME_PARTY] = self.cr.getSimpleValue(IDENT_UNIT_CONSUME_PARTY)
        if self.cr.hasSimpleValue(IDENT_UNIT_SUPPLY):
            self.flags[FLAG_SUPPLY] = self.cr.getSimpleValue(IDENT_UNIT_SUPPLY)
        if self.cr.hasSimpleValue(IDENT_UNIT_TAXING):
            self.flags[FLAG_TAXING] = self.cr.getSimpleValue(IDENT_UNIT_TAXING)
        if self.cr.hasSimpleValue(IDENT_UNIT_GUARD):
            self.flags[FLAG_GUARD] = self.cr.getSimpleValue(IDENT_UNIT_GUARD)
        if self.cr.hasSimpleValue(IDENT_UNIT_SINGLE):
            self.flags[FLAG_SINGLE] = self.cr.getSimpleValue(IDENT_UNIT_SINGLE)
        if self.cr.hasSimpleValue(IDENT_UNIT_AVOID):
            self.flags[FLAG_AVOID] = self.cr.getSimpleValue(IDENT_UNIT_AVOID)
        if self.cr.hasSimpleValue(IDENT_UNIT_BACKWARD):
            self.flags[FLAG_BACKWARD] = self.cr.getSimpleValue(IDENT_UNIT_BACKWARD)
        if self.cr.hasSimpleValue(IDENT_UNIT_HOLD_POSITION):
            self.flags[FLAG_HOLD_POSITION] = self.cr.getSimpleValue(IDENT_UNIT_HOLD_POSITION)
        if self.cr.hasSimpleValue(IDENT_UNIT_MASKED):
            self.flags[FLAG_MASKED] = self.cr.getSimpleValue(IDENT_UNIT_MASKED)
        if self.cr.hasSimpleValue(IDENT_UNIT_REVEAL_UNIT):
            self.flags[FLAG_REVEAL_UNIT] = self.cr.getSimpleValue(IDENT_UNIT_REVEAL_UNIT)
        if self.cr.hasSimpleValue(IDENT_UNIT_REVEAL_PARTY):
            self.flags[FLAG_REVEAL_PARTY] = self.cr.getSimpleValue(IDENT_UNIT_REVEAL_PARTY)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_MAX_WALK):
            self.capacity[MOVE_WALKING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_MAX_WALK)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_MAX_RIDE):
            self.capacity[MOVE_RIDING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_MAX_RIDE)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_MAX_SWIM):
            self.capacity[MOVE_SWIMMING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_MAX_SWIM)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_MAX_FLY):
            self.capacity[MOVE_FLYING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_MAX_FLY)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_WALK):
            self.usedCapacity[MOVE_WALKING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_WALK)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_RIDE):
            self.usedCapacity[MOVE_RIDING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_RIDE)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_SWIM):
            self.usedCapacity[MOVE_SWIMMING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_SWIM)
        if self.cr.hasSimpleValue(IDENT_UNIT_CAP_FLY):
            self.usedCapacity[MOVE_FLYING] = self.cr.getSimpleValue(IDENT_UNIT_CAP_FLY)
        if self.cr.hasSimpleValue(IDENT_UNIT_EMBARKED):
            self.fleetNumber = self.cr.getSimpleValue(IDENT_UNIT_EMBARKED)
            fleet = self.region.getFleet(self.fleetNumber)
            if fleet is None:
                fleet = RorFleet(self.region, self.fleetNumber)
                self.region.fleets += [fleet]
            fleet.embark(self)
        if self.cr.hasSimpleValue(IDENT_UNIT_STATUS1):
            self.status += [self.cr.getSimpleValue(IDENT_UNIT_STATUS1)]
        if self.cr.hasSimpleValue(IDENT_UNIT_STATUS2):
            self.status += [self.cr.getSimpleValue(IDENT_UNIT_STATUS2)]
        if self.cr.hasSimpleValue(IDENT_UNIT_STATUS3):
            self.status += [self.cr.getSimpleValue(IDENT_UNIT_STATUS3)]
        if self.cr.hasSimpleValue(IDENT_UNIT_STATUS4):
            self.status += [self.cr.getSimpleValue(IDENT_UNIT_STATUS4)]

        if (aw.turn >= 143):
            self.cr.ignoreIdent(IDENT_UNIT_CAN_LEARN)
        elif self.cr.hasSimpleValue(IDENT_UNIT_CAN_LEARN):
            temp = self.cr.getSimpleValue(IDENT_UNIT_CAN_LEARN)
            for t in temp:
                p = RorTalent()
                p.name = t
                p.kbobj = p.getKBObject()
                if p.kbobj is None:
                    print "Unbekannter Zauber: " + t
                    GetKB().output += [Message(CAT_ERR, 124, (t))]
                else:
                    p.initValuesFromKB()
                    self.learnable[p.id] = p

    def getKey(self):
        return self.id

    def getKeyAsString(self):
        return str(self.id)

    def getFlag(self, flag):
        if self.flags.has_key(flag):
            return (self.flags[flag] == 1)
        else:
            return False

    def setFlag(self, flag, value):
        self.flags[flag] = value

    def isArmed(self, aw):
        items = self.inventory.values()
        for item in items:
            if item.hasType(TYPE_P_WEAPON):
                if (self.partynumber != aw.partynumber):
                    return True
                if self.canUse(item):
                    return True
        return False

    def isMagician(self):
        talents = self.talents.values()
        for t in talents:
            if t.hasType(TYPE_T_MAGIC):
                return True
        return False

    def isLeader(self):
        items = self.inventory.values()
        for i in items:
            if (i.getKey() == ID_P_ANFU):
                return True
        return False

    def getPersons(self):
        persons = 0
        items = self.inventory.values()
        for item in items:
            if item.hasType(TYPE_P_HUMANOID):
                persons = persons + item.amount
        return persons

    def getArmedPersons(self, aw):
        weaponAmount = 0
        items = self.inventory.values()
        for item in items:
            if item.hasType(TYPE_P_WEAPON):
                if (self.partynumber != aw.partynumber):
                    weaponAmount += item.amount
                elif self.canUse(item):
                    weaponAmount += item.amount
        if (weaponAmount > self.getPersons()):
            return self.getPersons()
        return weaponAmount

    def getRace(self):
        inventory = self.inventory.values()
        for item in inventory:
            if item.hasType(TYPE_P_HUMANOID):
                if item.amount > 0:
                    return item
                else:
                    return None
        return None

    def addProduct(self, key, amount):
        if not self.inventory.has_key(key):
            newProduct = RorProduct()
            newProduct.id = key
            newProduct.kbobj = newProduct.getKBObject()
            if not newProduct.kbobj is None:
                newProduct.initValuesFromKB()
            else:
                newProduct.singular = "unbekannt: " + key
                newProduct.plural   = "unbekannt: " + key
            self.inventory[key] = newProduct
        self.inventory[key].amount += amount

    def delProduct(self, key, amount):
        if not self.inventory.has_key(key):
            raise ValueError("Produkt " + str(key) + " nicht vorhanden")
        if (self.inventory[key].amount <= amount):
            del self.inventory[key]
        else:
            self.inventory[key].amount -= amount

    def addCommand(self, c):
        self.commands += [c]

    def delCommand(self, c):
        " Loescht alle Befehle des uebergebenen Typs. "
        for x in self.commands:
            if (type(x) == type(c)):
                self.commands.remove(x)
                break
        return

    def calcLivelihood(self, persons = 0):
        race = self.getRace()
        if race is None:
            return 0
        livelihoodBase = race.livelihood
        foundCitadel  = False
        foundGarrison = False
        if self.region.ownerNumber == self.partynumber:
            for o in self.region.sortedObjects:
                if o.singular == NAME_B_ZITA:
                    foundCitadel = True
                    continue
                if o.singular == NAME_B_GARN:
                    foundGarrison = True
                    continue
        if foundCitadel:
            livelihoodBase -= 1
            if foundGarrison:
                livelihoodBase -= 1
        return (livelihoodBase * (self.getPersons() - persons))

    def calcEncumbrance(self):
        self.encumbrance = 0
        self.encumbranceWithoutOwnWeight[MOVE_SWIMMING] = 0
        self.encumbranceWithoutOwnWeight[MOVE_WALKING] = 0
        self.encumbranceWithoutOwnWeight[MOVE_RIDING] = 0
        self.encumbranceWithoutOwnWeight[MOVE_FLYING] = 0
        itemList = self.inventory.values()
        for item in itemList:
            if item.kbobj is None:
                self.output += [Message(CAT_HINT, 145, para = (item.getKey()))]
                continue
            self.encumbrance += (item.amount * item.weight)
            capacity = item.kbobj.capacity
            if (capacity == {}) or not capacity.has_key(MOVE_SWIMMING):
                self.encumbranceWithoutOwnWeight[MOVE_SWIMMING] += (item.amount * item.weight)
            if (capacity == {}) or not capacity.has_key(MOVE_WALKING):
                self.encumbranceWithoutOwnWeight[MOVE_WALKING] += (item.amount * item.weight)
            if (capacity == {}) or not capacity.has_key(MOVE_RIDING):
                self.encumbranceWithoutOwnWeight[MOVE_RIDING] += (item.amount * item.weight)
            if (capacity == {}) or not capacity.has_key(MOVE_FLYING):
                self.encumbranceWithoutOwnWeight[MOVE_FLYING] += (item.amount * item.weight)

    def calcCapacity(self):
        self.capacity[MOVE_SWIMMING] = 0
        self.capacity[MOVE_WALKING] = 0
        self.capacity[MOVE_RIDING] = 0
        self.capacity[MOVE_FLYING] = 0
        self.capacityWithoutOwnWeight[MOVE_SWIMMING] = 0
        self.capacityWithoutOwnWeight[MOVE_WALKING] = 0
        self.capacityWithoutOwnWeight[MOVE_RIDING] = 0
        self.capacityWithoutOwnWeight[MOVE_FLYING] = 0
        itemList = self.inventory.values()
        for item in itemList:
            if item.kbobj is None:
                self.output += [Message(CAT_HINT, 144, para = (item.getKey()))]
                continue
            if item.hasType(TYPE_P_SHIP):
                continue
            capacity = item.kbobj.capacity
            if capacity == {}:
                continue
            if capacity.has_key(MOVE_SWIMMING):
                self.capacity[MOVE_SWIMMING] += (item.amount * (item.weight + capacity[MOVE_SWIMMING]))
                self.capacityWithoutOwnWeight[MOVE_SWIMMING] += (item.amount * capacity[MOVE_SWIMMING])
            if capacity.has_key(MOVE_WALKING):
                self.capacity[MOVE_WALKING] += (item.amount * (item.weight + capacity[MOVE_WALKING]))
                self.capacityWithoutOwnWeight[MOVE_WALKING] += (item.amount * capacity[MOVE_WALKING])
            if capacity.has_key(MOVE_RIDING):
                self.capacity[MOVE_RIDING] += (item.amount * (item.weight + capacity[MOVE_RIDING]))
                self.capacityWithoutOwnWeight[MOVE_RIDING] += (item.amount * capacity[MOVE_RIDING])
            if capacity.has_key(MOVE_FLYING):
                self.capacity[MOVE_FLYING] += (item.amount * (item.weight + capacity[MOVE_FLYING]))
                self.capacityWithoutOwnWeight[MOVE_FLYING] += (item.amount * capacity[MOVE_FLYING])

    def calcBP(self):
        self.bp[MOVE_SWIMMING] = -1
        self.bp[MOVE_WALKING] = -1
        self.bp[MOVE_RIDING] = -1
        self.bp[MOVE_FLYING] = -1
        if (self.fleetNumber != 0) and (self.fleetNumber != self.getKey()):
            return
        if self.getRace() is None: # Einheit hat seine Rasse weggegeben
            return
        itemsRiding = 0
        itemsFlying = 0
        persons = self.getRace().amount
        itemList = self.inventory.values()
        for item in itemList:
            if item.kbobj is None:
                self.output += [Message(CAT_HINT, 143, para = (item.getKey()))]
                continue
            if item.hasType(TYPE_P_SHIP):
                continue
            bp = item.kbobj.bp
            if bp == {}:
                continue
            if bp.has_key(MOVE_SWIMMING):
                if (self.bp[MOVE_SWIMMING] > bp[MOVE_SWIMMING]) or (self.bp[MOVE_SWIMMING] == -1):
                    self.bp[MOVE_SWIMMING] = bp[MOVE_SWIMMING]
            else:
                if not item.hasType(TYPE_P_HUMANOID):
                    self.bp[MOVE_SWIMMING] = 0
            if bp.has_key(MOVE_WALKING):
                if (self.bp[MOVE_WALKING] > bp[MOVE_WALKING]) or (self.bp[MOVE_WALKING] == -1):
                    self.bp[MOVE_WALKING] = bp[MOVE_WALKING]
            else:
                if not item.hasType(TYPE_P_HUMANOID):
                    self.bp[MOVE_WALKING] = 0
            if bp.has_key(MOVE_RIDING):
                if (self.bp[MOVE_RIDING] > bp[MOVE_RIDING]) or (self.bp[MOVE_RIDING] == -1):
                    self.bp[MOVE_RIDING] = bp[MOVE_RIDING]
                    itemsRiding += item.amount
            else:
                if not item.hasType(TYPE_P_HUMANOID):
                    self.bp[MOVE_RIDING] = 0
            if bp.has_key(MOVE_FLYING):
                if (self.bp[MOVE_FLYING] > bp[MOVE_FLYING]) or (self.bp[MOVE_FLYING] == -1):
                    self.bp[MOVE_FLYING] = bp[MOVE_FLYING]
                    itemsFlying += item.amount
            else:
                if not item.hasType(TYPE_P_HUMANOID):
                    self.bp[MOVE_FLYING] = 0
        if (self.bp[MOVE_RIDING] != -1) and (persons > itemsRiding):
            self.bp[MOVE_RIDING] = -1
        if (self.bp[MOVE_FLYING] != -1) and (persons > itemsFlying):
            self.bp[MOVE_FLYING] = -1

    def canProduce(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findProduct(object.getKey())
        else:
            kbobj = object.kbobj
        return kbobj.unitCanProduce(self)

    def canBuild(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findBuilding(object.getKey())
        else:
            kbobj = object.kbobj
        return kbobj.unitCanBuild(self)

    def canLearn(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findTalent(object.getKey())
        else:
            kbobj = object.kbobj
        return kbobj.unitCanLearn(self)

    def canRecycle(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findProduct(object.getKey())
        else:
            kbobj = object.kbobj
        return kbobj.unitCanRecycle(self)

    def canDestroy(self, object):
        if self.talents.has_key(ID_T_BAUM):
            credit = self.talents[ID_T_BAUM].level * self.getPersons()
            return (float(object.size)/float(10) <= credit)
        return False

    def canUse(self, product):
        if product.kbobj is None:
            kb = GetKB()
            kbobj = kb.findProduct(product.getKey())
        else:
            kbobj = product.kbobj
        return kbobj.unitCanUse(self)

    def getProductionMaterial(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findProduct(object.getKey())
        else:
            kbobj = object.kbobj
        (amount, kbProducts) = kbobj.getProductionMaterial(self)
        products = []
        for k in kbProducts:
            newProduct = RorProduct()
            newProduct.kbobj = k[0]
            if not newProduct.kbobj is None:
                newProduct.initValuesFromKB()
            else:
                newProduct.singular = "unbekannt: " + object.getKey()
                newProduct.plural   = "unbekannt: " + object.getKey()
            newProduct.amount = k[1]
            products += [newProduct]
        return (amount, products)

    def getRecyclingMaterial(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findProduct(object.getKey())
        else:
            kbobj = object.kbobj
        (amount, kbProducts) = kbobj.getRecyclingMaterial(self)
        products = []
        for k in kbProducts:
            newProduct = RorProduct()
            newProduct.kbobj = k[0]
            if not newProduct.kbobj is None:
                newProduct.initValuesFromKB()
            else:
                newProduct.singular = "unbekannt: " + object.getKey()
                newProduct.plural   = "unbekannt: " + object.getKey()
            newProduct.amount = k[1]
            products += [newProduct]
        return (amount, products)

    def getBuildingMaterial(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findBuilding(object.singular)
        else:
            kbobj = object.kbobj
        (amount, kbProducts) = kbobj.getBuildingMaterial(self)
        products = []
        for k in kbProducts:
            newProduct = RorProduct()
            newProduct.kbobj = k[0]
            if not newProduct.kbobj is None:
                newProduct.initValuesFromKB()
            else:
                newProduct.singular = "unbekannt: " + object.singular
                newProduct.plural   = "unbekannt: " + object.singular
            newProduct.amount = k[1]
            products += [newProduct]
        return (amount, products)

    def getDestructionMaterial(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findBuilding(object.singular)
        else:
            kbobj = object.kbobj
        if kbobj.recycling is None:
            return (0, None)
        newProduct = RorProduct()
        newProduct.kbobj = kbobj.recycling
        if not newProduct.kbobj is None:
            newProduct.initValuesFromKB()
        else:
            newProduct.singular = "unbekannt: " + object.singular
            newProduct.plural   = "unbekannt: " + object.singular
        return (object.size/2, [newProduct])

    def getLearningMaterial(self, object):
        if object.kbobj is None:
            kb = GetKB()
            kbobj = kb.findTalent(object.getKey())
        else:
            kbobj = object.kbobj
        (amount, kbProducts) = kbobj.getLearningMaterial(object)
        products = []
        for k in kbProducts:
            newProduct = RorProduct()
            newProduct.kbobj = k[0]
            if not newProduct.kbobj is None:
                newProduct.initValuesFromKB()
            else:
                newProduct.singular = "unbekannt: " + object.getKey()
                newProduct.plural   = "unbekannt: " + object.getKey()
            newProduct.amount = k[1]
            products += [newProduct]
        return (amount, products)

    def move(self, newRegion):
        # Bewegungsart ermitteln
        if (newRegion.terrain == TYPE_TER_OCEAN):
            if self.bp[MOVE_SWIMMING] <= 0:
                return 1
            elif (self.bp[MOVE_SWIMMING] < self.usedBP) and self.minMove:
                return 2
            elif (self.encumbrance > self.capacity[MOVE_SWIMMING]):
                return 3
        elif (self.bp[MOVE_FLYING] > 0):
            if (self.bp[MOVE_FLYING] < self.usedBP) and self.minMove:
                return 2
            elif (self.encumbrance > self.capacity[MOVE_FLYING]):
                return 3
        elif (self.bp[MOVE_RIDING] > 0):
            if (self.bp[MOVE_RIDING] < self.usedBP) and self.minMove:
                return 2
            elif (self.encumbrance > self.capacity[MOVE_RIDING]):
                return 3
        elif (self.bp[MOVE_WALKING] > 0):
            if (self.bp[MOVE_WALKING] < self.usedBP) and self.minMove:
                return 2
            elif (self.encumbrance > self.capacity[MOVE_WALKING]):
                return 3
        newObject = newRegion.getHinterland()
        self.object.delUnit(self)
        self.region = newRegion
        newObject.addUnit(self)
        self.minMove = True
        return 0

    def hasProductType(self, type):
        items = self.inventory.values()
        for i in items:
            if i.hasType(type):
                return True
        return False
