#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
# $Id: kb.py,v 2.5 2005/04/04 21:43:45 kdm Exp $                              #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#                                                                             #
#                                                                             #
# --------------------------------------------------------------------------- #

from vdf.vdfparser import InitParser
from vdf.vdf import ParseEntry, VDFObject
from rorqual.constants import *
from util.messages import *
from util.dictionaries import KeyInsensitiveDict

__all__ = ["KnowledgeBase", "GetKB", "readConfigfile"]

class ConfigException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def createBoolTerm(item):
    o = None
    key = item.getKey()
    if key == KB_BOOL_OR:
        o = OrTerm(key)
        o.init(item)
    elif key == KB_BOOL_AND:
        o = AndTerm(key)
        o.init(item)
    elif key == KB_BOOL_NOT:
        o = NotTerm(key)
        o.init(item)
    elif key == KB_BOOL_PRODUCT:
        o = ProductTerm(key)
        o.init(item)
    elif key == KB_BOOL_PRODUCTTYPE:
        o = ProducttypeTerm(key)
        o.init(item)
    elif key == KB_BOOL_TALENT:
        o = TalentTerm(key)
        o.init(item)
    elif key == KB_BOOL_TALENTTYPE:
        o = TalenttypeTerm(key)
        o.init(item)
    elif key == KB_BOOL_TALENTLEVEL:
        o = TalentlevelTerm(key)
        o.init(item)
    else:
        raise ConfigException("Unknown Group(" + key + ")")
    return o
    
class BoolTerm(object):
    def __init__(self, key):
        self.subterms = []
        self.last = False
        self.key = key
        self.possibleAmount = 0 
        self.calculatedConsumption = [] 
    
    def addSubTerm(self, term):
        self.subterms += [term]
        
    def initCheck(self):
        self.possibleAmount = 0 
        self.calculatedConsumption = [] 

    def check(self, unit):
        self.last = False
        return self.last
    
    def getLast(self):
        return self.last
    
    def init(self, vdfobj):
        items = vdfobj.getAllSubItems()
        for item in items:
            t = createBoolTerm(item)
            self.addSubTerm(t)

    def __str__(self):
        return self.__class__.__name__ + ":" + self.key

class AtomTerm(BoolTerm):
    def __init__(self, key):
        super(AtomTerm, self).__init__(key)
        self.data = {}
        
    def init(self, vdfobj):
        items = vdfobj.getAllSubItems()
        for item in items:
            self.data[item.getKey()] = item

class ProductTerm(AtomTerm):
    def __init__(self, key):
        super(ProductTerm, self).__init__(key)

    def init(self, vdfobj):
        super(ProductTerm, self).init(vdfobj)
        kb = GetKB()
        self.product = kb.findProduct(self.getKey())

    def check(self, unit):
        self.initCheck()
        id = self.getKey()
        amount = self.getAmount()
        credit = 0
        if unit.inventory.has_key(id):
            item = unit.inventory[id]
            credit = item.amount
        self.last = credit >= amount
        if self.last:
            consumption = self.getConsumption()
            if consumption > 0:
                self.possibleAmount = credit / amount
                self.calculatedConsumption += [(self.product, consumption)]
            else:
                self.possibleAmount = 0
        return self.last
    
    def getAmount(self):
        if self.data.has_key(KB_PRODUCT_AMOUNT):
            return int(self.data[KB_PRODUCT_AMOUNT])
        elif self.data.has_key(KB_PRODUCT_COUNT):
            return int(self.data[KB_PRODUCT_COUNT])
        else:
            return 0

    def getKey(self):
        return str(self.data[KB_PRODUCT_ID])

    def getConsumption(self):
        if self.data.has_key(KB_PRODUCT_CONSUMPTION):
            return int(self.data[KB_PRODUCT_CONSUMPTION])
        else:
            return 0
 
    def __str__(self):
        return "ProductTerm: " + self.getKey() + " " + str(self.getAmount())
        
   
class ProducttypeTerm(AtomTerm):
    def __init__(self, key):
        super(ProducttypeTerm, self).__init__(key)
    
    def check(self, unit):
        type = self.getType()
        amount = self.getAmount()
        items = unit.getInventory()
        credit = 0
        for i in items:
            if i.hasType(type):
                n = i.getAmount()
                if n > credit:
                    credit = n
        self.last = credit >= amount
        return self.last

    def getKey(self):
        return str(self.data[KB_PRODUCTTYPE_TYPE])

    def getAmount(self):
        return int(self.data[KB_PRODUCTTYPE_AMOUNT])

    def getType(self):
        raise ConfigException("Not implemented yet")

class TalentTerm(AtomTerm):
    def __init__(self, key):
        super(TalentTerm, self).__init__(key)
    
    def check(self, unit):
        self.initCheck()
        id = self.getKey()
        level = self.getLevel()
        credit = 0
        if unit.talents.has_key(id):
            credit = unit.talents[id].level
        self.last = credit >= level
        self.possibleAmount = 0
        if self.last:
            self.possibleAmount = (credit - level + 1) * unit.getPersons()
        return self.last

    def getKey(self):
        return str(self.data[KB_TALENT_ID])

    def getLevel(self):
        return int(self.data[KB_TALENT_LEVEL])

    def getType(self):
        raise ConfigException("Not implemented yet")

    def __str__(self):
        return "TalentTerm: " + self.getKey() + " " + str(self.getLevel())
        

class TalenttypeTerm(AtomTerm):
    def __init__(self, key):
        super(TalenttypeTerm, self).__init__(key)
    
    def check(self, unit):
        typ = self.getType()
        level = self.getLevel()
        talente = unit.getTalente()
        credit = 0
        for t in talente:
            if t.hasType(typ):
                lvl = t.getLevel()
                if lvl > credit:
                    credit = lvl
        self.last = credit >= level
        return self.last

    def getKey(self):
        return str(self.data[KB_TALENTTYPE_TYPE])

    def getLevel(self):
        return int(self.data[KB_TALENTTYPE_LEVEL])

    def getType(self):
        raise ConfigException("Not implemented yet")

class TalentlevelTerm(AtomTerm):
    def __init__(self, key):
        super(TalentlevelTerm, self).__init__(key)
    
    def check(self, unit):
        id = self.getKey()
        lvl = self.getLevel()
        credit = 0
        if unit.talents.has_key(id):
            credit = unit.talents[id].getLevel().level
        credit = credit * unit.getPersons()
        self.last = credit >= lvl
        return self.last

    def getKey(self):
        return str(self.data[KB_TALENTLEVEL_ID])

    def getLevel(self):
        return int(self.data[KB_TALENTLEVEL_LEVEL])

class NotTerm(BoolTerm):
    def __init__(self, key):
        super(NotTerm, self).__init__(key)
    
    def check(self, unit):
        self.initCheck()
        self.last = not (self.subterms[0].check(unit))
        return self.last

    def __str__(self):
        return "NOT (" +  str(self.subterms[0]) + ")"
       
class AndTerm(BoolTerm):
    def __init__(self, key):
        super(AndTerm, self).__init__(key)
    
    def check(self, unit):
        self.initCheck()
        self.last = True
        for t in self.subterms:
            self.last = (self.last and t.check(unit))
        if self.last:
            possibleAmountList = []
            for t in self.subterms:
                if isinstance (t, ProductTerm):
                    self.calculatedConsumption += t.calculatedConsumption
                    if t.getConsumption() > 0:
                        possibleAmountList += [t.possibleAmount]
                elif isinstance (t, TalentTerm):
                    possibleAmountList += [t.possibleAmount]
                elif isinstance (t, (AndTerm,OrTerm)):
                    possibleAmountList += [t.possibleAmount]
                    self.calculatedConsumption += t.calculatedConsumption
                else:
                    raise AssertionError("TODO")
            if not possibleAmountList == []:
                self.possibleAmount = min(possibleAmountList)
        return self.last
    
    def __str__(self):
        s = "AND(" + str(self.subterms[0])
        for t in self.subterms[1:]:
            s += ", " + str(t)
        s += ")"
        return s

class OrTerm(BoolTerm):
    def __init__(self, key):
        super(OrTerm, self).__init__(key)
    
    def check(self, unit):
        self.initCheck()
        self.last = False
        possibleAmountList = []
        for t in self.subterms:
            self.last = (self.last or t.check(unit))        
        if self.last:
            for t in self.subterms:
                if isinstance(t, ProductTerm):
                    self.calculatedConsumption += t.calculatedConsumption
                    if t.getConsumption() > 0:
                        possibleAmountList += [t.possibleAmount]
                elif isinstance(t, TalentTerm):
                    possibleAmountList += [t.possibleAmount]
                elif isinstance (t, (AndTerm,OrTerm)):
                    possibleAmountList += [t.possibleAmount]
                    self.calculatedConsumption += t.calculatedConsumption
                else:
                    raise AssertionError("TODO")
            if not possibleAmountList == []:
                self.possibleAmount = max(possibleAmountList)
        return self.last
    
    def __str__(self):
        s = "OR(" + str(self.subterms[0])
        for t in self.subterms[1:]:
            s += ", " + str(t)
        s += ")"
        return s
        
class KBProduct(object):
    def __init__(self):
        self.key = None
        self.singular = None
        self.plural = ""
        self.types = []
        self.weight = 0
        self.livelihood = 0
        self.optableRace = False
        self.production = None
        self.recycling = None
        self.use = None
        self.bp = {}
        self.capacity = {}
        
    def initFromVDF(self, vdfobj):
        self.key = vdfobj.getSimpleValue(KB_PRODUCT_ID)
        self.singular = vdfobj.getSimpleValue(KB_PRODUCT_SINGULAR)
        if vdfobj.hasSimpleValue(KB_PRODUCT_PLURAL):
            self.plural = vdfobj.getSimpleValue(KB_PRODUCT_PLURAL)
        self.types = vdfobj.getSimpleValue(KB_PRODUCT_TYPE)
        if vdfobj.hasSimpleValue(KB_PRODUCT_WEIGHT):
            self.weight = vdfobj.getSimpleValue(KB_PRODUCT_WEIGHT)
        if vdfobj.hasSimpleValue(KB_IDENT_PRODUCT_LIVELIHOOD):
            self.livelihood = vdfobj.getSimpleValue(KB_IDENT_PRODUCT_LIVELIHOOD)
        if vdfobj.hasSimpleValue(KB_IDENT_PRODUCT_OPTABLE_RACE):
            self.optableRace = vdfobj.getSimpleValue(KB_IDENT_PRODUCT_OPTABLE_RACE)
        temp = vdfobj.getSingleSubItem(KB_PRODUCT_NEEDS_FOR_PRODUCTION)
        if not temp is None:
            self.production = createBoolTerm(temp.getAllSubItems()[0])
        temp = vdfobj.getSingleSubItem(KB_PRODUCT_NEEDS_FOR_RECYCLING)
        if not temp is None:
            self.recycling = createBoolTerm(temp.getAllSubItems()[0])
        temp = vdfobj.getSingleSubItem(KB_PRODUCT_NEEDS_FOR_USE)
        if not temp is None:
            self.use = createBoolTerm(temp.getAllSubItems()[0])
        temp1 = vdfobj.getSingleSubItem(KB_PRODUCT_CAPACITY)
        temp2 = vdfobj.getSingleSubItem(KB_PRODUCT_BP)
        for key in [MOVE_SWIMMING, MOVE_WALKING, MOVE_RIDING, MOVE_FLYING]:
            if (not temp1 is None) and (temp1.hasValue(key)):
                self.capacity[key] = temp1.getSimpleValue(key)
            if (not temp2 is None) and (temp2.hasValue(key)):
                self.bp[key] = temp2.getSimpleValue(key)

    def getKey(self):
        return self.key

    def unitCanProduce(self, unit):
        if self.production is None:
            return False
        return self.production.check(unit)

    def unitCanRecycle(self, unit):
        if self.recycling is None:
            return False
        return self.recycling.check(unit)

    def unitCanUse(self, unit):
        if self.use is None:
            return False
        return self.use.check(unit)

    def getProductionMaterial(self, unit):
        if (self.production is None) or not self.production.check(unit):
            return (0, None)
        else:
            return (self.production.possibleAmount, self.production.calculatedConsumption)

    def getRecyclingMaterial(self, unit):
        if (self.recycling is None) or not self.recycling.check(unit):
            return (0, None)
        else:
            return (self.recycling.possibleAmount, self.recycling.calculatedConsumption)

class KBTalent(object):
    def __init__(self):
        self.key = None
        self.singular = None
        self.types = []
        self.learningFee = 0
        self.learning = None

    def initFromVDF(self, vdfobj):
        self.key = vdfobj.getSimpleValue(KB_TALENT_ID)
        self.singular = vdfobj.getSimpleValue(KB_TALENT_SINGULAR)
        self.types = vdfobj.getSimpleValue(KB_TALENT_TYPE)
        if vdfobj.hasSimpleValue(KB_TALENT_LEARNCOST):
            self.learningFee = vdfobj.getSimpleValue(KB_TALENT_LEARNCOST)
        temp = vdfobj.getSingleSubItem(KB_TALENT_NEEDS_FOR_LEARNING)
        if not temp is None:
            self.learning = createBoolTerm(temp.getAllSubItems()[0])

    def unitCanLearn(self, unit):
        if (self.learning is None) and (self.learningFee != 0):
            return True
        return self.learning.check(unit)

    def getLearningMaterial(self, unit):
        if (self.learning is None) or not self.learning.check(unit):
            return (0, None)
        else:
            return (self.learning.possibleAmount, self.learning.calculatedConsumption)

class KBBuilding(object):
    def __init__(self):
        self.key = None
        self.singular = None
        self.plural = None
        self.alias = None
        self.types = []
        self.canEnter = False
        self.maxSize = 0
        self.minSize = 0
        self.favour = {}
        self.expandableTo = None
        self.production = None
        self.recycling = None
        
    def initFromVDF(self, vdfobj):
        self.key = vdfobj.getSimpleValue(KB_BUILDING_ID)
        self.singular = vdfobj.getSimpleValue(KB_BUILDING_SINGULAR)
        self.plural = vdfobj.getSimpleValue(KB_BUILDING_PLURAL)
        self.alias = vdfobj.getSimpleValue(KB_BUILDING_ALIAS)
        self.types = vdfobj.getSimpleValue(KB_BUILDING_TYPE)
        if vdfobj.hasSimpleValue(KB_BUILDING_ENTERABLE):
            self.canEnter = vdfobj.getSimpleValue(KB_BUILDING_ENTERABLE)
        if vdfobj.hasSimpleValue(KB_BUILDING_MAX_SIZE):
            self.maxSize = vdfobj.getSimpleValue(KB_BUILDING_MAX_SIZE)
        if vdfobj.hasSimpleValue(KB_BUILDING_MIN_SIZE):
            self.minSize = vdfobj.getSimpleValue(KB_BUILDING_MIN_SIZE)
        temp = vdfobj.getSingleSubItem(KB_BUILDING_AIDS)
        if not temp is None:
            temp = temp.getAllSubItems()
            for item in temp:
                if item.getKey() == KB_BOOL_PRODUCT:
                    p = KBProduct()
                    p.initFromVDF(item)
                    self.favour[p.getKey()] = p
        temp = vdfobj.getSingleSubItem(KB_BUILDING_EXPANDABLE)
        if not temp is None:
            temp = temp.getAllSubItems()
            for item in temp:
                if item.getKey() == KB_BOOL_BUILDING:
                    p = KBBuilding()
                    p.initFromVDF(item)
                    self.expandableTo = p
        temp = vdfobj.getSingleSubItem(KB_BUILDING_NEEDS_FOR_PRODUCION)
        if not temp is None:
            self.production = createBoolTerm(temp.getAllSubItems()[0])

    def unitCanBuild(self, unit):
        if self.production is None:
            return False
        return self.production.check(unit)

    def getBuildingMaterial(self, unit):
        if (self.production is None) or not self.production.check(unit):
            return (0, None)
        else:
            return (self.production.possibleAmount, self.production.calculatedConsumption)

class KnowledgeBase(object):
    def __init__(self):
        self.products = KeyInsensitiveDict()
        self.buildings = KeyInsensitiveDict()
        self.talents = KeyInsensitiveDict()
        self.missingProducts = []
        self.missingBuildings = []
        self.missingTalents = []
        self.output = []
        
    def add(self, vdfobjlst):
        for obj in vdfobjlst:
            key = obj.getKey()
            if key == KB_IDENT_PRODUCTSPEC:
                p = KBProduct()
                p.initFromVDF(obj)
                self.products[p.key] = p
            elif key == KB_IDENT_TALENTSPEC:
                p = KBTalent()
                p.initFromVDF(obj)
                self.talents[p.key] = p
            elif key == KB_IDENT_BUILDINGSPEC:
                p = KBBuilding()
                p.initFromVDF(obj)
                self.buildings[p.key] = p
            elif key == KB_IDENT_VERSION:
                continue
                #print "Version: " + str(obj.getSimpleValue("CVSID"))
            else:
                raise ConfigException("unbekannte Gruppe: " + key)

    def addMissingProduct(self, name):
        if not (name in self.missingProducts):
            self.missingProducts += [name]
            self.output += [Message(CAT_ERR, 15, para = (name))]
            print "Unbekannter Gegenstand: ", name

    def addMissingBuilding(self, name):
        if not (name in self.missingBuildings):
            self.missingBuildings += [name]
            self.output += [Message(CAT_ERR, 12, para = (name))]
            print "Unbekanntes Bauwerk: ", name

    def addMissingTalent(self, name):
        if not (name in self.missingTalents):
            self.missingTalents += [name]
            self.output += [Message(CAT_ERR, 16, para = (name))]
            print "Unbekanntes Talent: ", name

    def findProduct(self, key):
        if self.products.has_key(key):
            return self.products[key]
        elif not key is None:
            key = key.lower()
            lst = self.products.values()
            for l in lst:
                if (l.singular.lower() == key) or (l.plural.lower() == key):
                    return l
            return None

    def findBuilding(self, key):
        if self.buildings.has_key(key):
            return self.buildings[key]
        else:
            key = key.lower()
            lst = self.buildings.values()
            for l in lst:
                if (l.singular.lower() == key):
                    return l
                if not (l.plural is None):
                    if (l.plural.lower() == key):
                        return l
                if not (l.alias is None):
                    for x in l.alias:
                        if x.lower() == key:
                            return l
            return None

    def findTalent(self, key):
        if self.talents.has_key(key):
            return self.talents[key]
        else:
            key = key.lower()
            lst = self.talents.values()
            for l in lst:
                if (l.singular.lower() == key):
                    return l
            return None

def readConfigfile(filename):
    result = []
    print "reading " + filename + "."*3 ,
    if InitParser(filename) != 0:
        raise IOError("File not found");
    try:
        while True:
            e = ParseEntry()
            (key, type, value, line) = e
            obj = VDFObject(key, type, line)
            obj.init(value)
            result += [obj]
    except IOError:
        print "done."
    return result

__kb__ = KnowledgeBase()
    
def GetKB():
    return __kb__
    

