#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: vdf.py,v 2.5 2005/04/04 17:54:53 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Enthaelt Klassen und Methoden, die sich mit dem Parsen und Schreiben des
# VDF-Formats befassen. Ebenso ist die Klasse VDFObject enthalten, die
# Zugriffsfunktionen auf das VDF-Format kapselt.
#
# ParseEntry():
#    Parst einen einzelnen VDF-Eintrag. Bei Gruppen werden die Unterein-
#    traege als eigenstaendige VDF-Eintraege aufgefasst und muessen damit in
#    nachfolgenden Aufrufen von ParseEntry gelesen werden.
#    Liefert Quadrupel bestehend aus Name, Typ, Value und Zeile der ge-
#    parsten Datei. Im Fehlerfall wird eine VDFParserException ausgeloest,
#    ein unerwartetes End of file loest einen IOError aus.
#
# ResetParser(filename):
#    Initialisiert den Parser neu, sodass er nun die angegebene Datei parst.
#
# VDFWrite(out, key, t, item, indent):
#    Schreibt das angegebene item mit zugehoerigem Typ und Key als VDF
#    Eintrag in die angegebene Ausgabedatei.
#    Parameter:
#    out    - Ausgabedatei
#    item   - VDFObjekt, das ausgegeben werden soll
#    key    - Name des VDF Eintrags, unter dem das Objekt ausgegeben werden
#             soll
#    t      - VDF Typ des VDFObjektes
#    indent - Anzahl der Whitespaces die bei der Ausgabe eingerueckt werden
#             soll
#
# Klasse VDFParserException(Exception):
#    Exception Klasse fuer Parserfehler der VDFParsers.
#
# Klasse VDFObject:
#    Ein VDFObjekt beinhaltet die Daten eines einzelnen VDF Eintrages. Es
#    ist in der Lage, sich im VDF Format zu speichern oder aus einem VDF-
#    Eintrag zu erstellen.
#
#    def init(self, val):
#        Setzt die Daten des Objektes auf val. Dabei werden fuer Objekte des
#        Typs GROUP auch die subitems geparst und der internen Hashtabelle
#        hinzugefuegt.
#        self.data ist dabei der Datenwert des VDFObjektes, fuer den Fall
#        dass es sich nicht um ein Objekt des Typen GROUP handelt. Ist is
#        vom Typ GROUP, so ist self.data eine Hashtabelle, dessen Datenein-
#        traege Listen von VDFObjekten sind.
#
#    def getLine(self):
#        Liefert die Zeile des CRs, in der der Eintrag steht..
#
#    def printVDF(self, out, indent):
#        Schreibt Objekt als VDF Eintrag in die Datei out, mit dem Indent
#        indent.
#
#    def getKey(self):
#        Liefert den key des VDFEintrages. Unter diesem Key wird das Objekt
#        in der Hashtabelle des Parentobjects abgelegt. Standardmaessig ist
#        das der Key des VDF Eintrags. Bei Abgeleitetet Objekten kann das
#        aber durchaus differieren, um z.B. unterschiedliche VDFObjects von-
#        einander unterscheiden zu koennen, die den gleichen Namen haben.
#
#    def isGroup(self):
#        Liefert true, wenn das Objekt den Typ GROUP besitzt.
#
#    def isList(self):
#        Liefert true, wenn die Daten des Objektes eine Liste sind.
#
#    def addSubItem(self, key, val):
#        Fuegt der Gruppe ein subitem hinzu.
#        key  - Key des hinzuzufuegenden VDFObjektes
#        val  - Hinzuzufuegendes VDFObjekt.
#        Exception raised:
#        TypeError, wenn val kein VDFObjekt ist oder
#                   wenn self kein VDFObjekt mit dem Typ "GROUP" ist.
#
#    def getSubItem(self, key):
#        Liefert alle Subitems des zugehoerigen Keys, falls das Objekt eine
#        Gruppe ist als Liste von VDF Objekten.
#        Liefert eine leere Liste wenn es kein Subitem zum angegebenen
#        Key gibt.
#        Exception raised:
#        TypeError, wenn self kein VDFObjekt des Typs GROUP ist.
#
#    def getAllSubItems(self):
#        Liefert eine Liste aller Subitems des VDFObjekts.
#        Liefert eine leere Liste wenn es keine Subitems gibt.
#        Die Liste enthaelt nur VDFObjekte.
#
#    def getSingleSubItem(self, key):
#        Liefert das zu key gehoerige Subitem als VDF-Objekt zurueck.
#        Liefert None, wenn zum key kein Subitem exsitiert.
#        Exception raised:
#        TypeError, wenn self kein VDFObjekt des Typs GROUP ist oder
#        wenn mehr als ein Eintrag unter dem Key abgelegt sind.
#
#    def getSimpleValue(self, key):
#        Liefert den Wert des unter dem angegebenen Keys abgelegten Subitems.
#        Dieser Wert ist vom Typ: int, string, float, list oder Tupel
#        bei Text-Zahl-Paaren.
#        Die Excpetion TypeError wird generiert, wenn das Objekt keine
#        Gruppe ist und somit auch keine Subitems enthalten kann,
#        wenn es mehrere Subitems gibt oder wenn das Subitem eine Gruppe ist.
#
#    def getAllSimpleValues(self, key):
#        Liefert eine Liste zurueck, die alle Subitems des angegebenen Keys
#        enthaelt. Jedoch enthaelt die Liste keine VDF-Objekte sondern die
#        bereits umgewandelten typen wie bei getSimpleValue.
#        Die Excpetion TypeError wird generiert, wenn das Objekt keine
#        Gruppe ist und somit auch keine Subitems enthalten kann,
#        oder wenn eines der Subitems eine Gruppe ist.
#
#    def setSimpleValue(self, key, value):
#        Setzt den Wert eines einfachen Subitems oder generiert ein Subitem
#        mit entsprechendem Wert, wenn das Subitem noch nicht existiert.
#
#    def hasValue(self, key):
#        Liefert True falls zum angegebenen Key ein Subitem existiert.
#        Die Excpetion TypeError wird generiert, wenn das Objekt keine
#        Gruppe ist und somit auch keine Subitems enthalten kann.
#
#    def hasSimpleValue(self, key):
#        Liefert True falls zum angegebenen Key ein Subitem existiert und es
#        nur einen Eintrag besitzt. Wenn hasSimpleValue True liefert, kann
#        gefahrlos getSimpleValue aufgerufen werden.
#        Die Excpetion TypeError wird generiert, wenn das Objekt keine
#        Gruppe ist und somit auch keine Subitems enthalten kann.
#
#    def len(self):
#        Liefert die Laenge einer Liste, wenn es ein Listentyp ist.
#
#    def __int__(self):
#        Liefert die Daten des Objektes als integer, falls dies moeglich ist.
#
#    def __float__(self):
#        Liefert die Daten des Objektes als float, falls dies moeglich ist.
#
#    def __str__(self):
#        Liefert die Daten des Objektes als string, falls dies moeglich ist.
#
# ---------------------------------------------------------------------------

__all__  = ["VDFParserException", "ParseEntry", "VDFObject", "VDFWrite", "ResetParser"]

import sys
import getopt
from vdfparser import *

class VDFParserException(Exception):
    def __init__(self, str):
        self.str = str

    def __str__(self):
        return "VDFParserException: " + self.str
    pass

def ParseEntry():
    o = GetNextEntry()
    err = GetLastErrorMsg();
    if err != None:
        raise VDFParserException(err)
    if o is None:
        raise IOError("End of File")
    line = GetCurrentLine()
    (name, typ) = o;
    if typ in (GROUP, FLAG, INT):
        val = GetInt()
    elif typ == DOUBLE:
        val = GetDouble()
    elif typ == TEXT:
        val = GetText()
    elif typ == FORMATED_TEXT:
        val = GetFormatedText()
    elif typ == TZPAIR:
        val = GetTextNumberPair()
    elif typ == FLAG_LIST:
        val = GetFlagList()
    elif typ == INT_LIST:
        val = GetIntList()
    elif typ == DOUBLE_LIST:
        val = GetDoubleList()
    elif typ == TEXT_LIST:
        val = GetTextList()
    elif typ == FORMATED_TEXT_LIST:
        val = GetFormatedTextList()
    elif typ == TZPAIR_LIST:
        val = GetTextNumberPairList()
    err = GetLastErrorMsg();
    if err != None:
        raise VDFParserException(err)
    FinishEntry();
    err = GetLastErrorMsg();
    if err != None:
        raise VDFParserException(err)
    return (name, typ, val, line);

def ResetParser(filename):
    if InitParser(filename) != 0:
        raise IOError("ResetParser Failed on file " + str(filename))

def VDFWrite(out, key, t, item, indent):
    s = " " * indent
    s = s + "(" + key + ","
    if t == GROUP:
        s = s + "g," + str(item) + ")"
    elif t is FLAG:
        s = s + "f," + str(item) + ")"
    elif t is INT:
        s = s + "z," + str(item) + ")"
    elif t is DOUBLE:
        s = s + "r," + str(item) + ")"
    elif t is TEXT:
        s = s + "t,\"" + item + "\")"
    elif t is FORMATED_TEXT:
        s = s + "ft,\"" + item + "\")"
    elif t is TZPAIR:
        i = item
        s = s + 'tz,"' + i[0] + "(" + str(i[1]) + ')")'
    elif t is FLAG_LIST:
        s = s + "fl, "
        lst = item
        if not lst:
            s = s + "[])"
        else:
            s = s + "["
            s = s + str(lst[0])
            for i in lst[1:]:
                s = s + "," + str(i)
            s += "])"
    elif t is INT_LIST:
        s = s + "zl,"
        lst = item
        if not lst:
            s = s + "[])"
        else:
            s = s + "["
            s = s + str(lst[0])
            for i in lst[1:]:
                s = s + "," + str(i)
            s += "])"
    elif t is DOUBLE_LIST:
        s = s + "rl,"
        lst = item
        if not lst:
            s = s + "[])"
        else:
            s = s + "["
            s = s + str(lst[0])
            for i in lst[1:]:
                s = s + "," + str(i)
            s += "])"
    elif t is TEXT_LIST:
        s = s + "tl,"
        lst = item
        if not lst:
            s = s + "[])"
        else:
            s = s + "["
            s = s + '"'+ lst[0] + '"'
            for i in lst[1:]:
                s = s + "," + '"' + i + '"'
            s += "])"
    elif t is FORMATED_TEXT_LIST:
        s = s + "ftl,"
        lst = item
        if not lst:
            s = s + "[])"
        else:
            s = s + "["
            s = s + '"' + str(lst[0]) + '"'
            for i in lst[1:]:
                s = s + "," + '"' + i + '"'
            s += "])"
    elif t is TZPAIR_LIST:
        s = s + "tzl,"
        lst = item
        if not lst:
            s = s + "[])"
        else:
            s = s + "["
            s = s + '"' + lst[0][0] + "(" + lst[0][1] + ')"'
            for i in lst[1:]:
                s = s + "," + '"' + i[0] + "(" + i[1] + ')"'
            s += "])"
    out.write(s + "\n")

class VDFObject:
    def __init__(self, key, typ, line, data=None):
        self.key = key # Name des VDFObjects, welches ja folgende Form hat : (name, typ, daten)
        self.typ = typ # Typ des VDFObjektes
        self.line = line # Zeilennummer des Eingelesenen VDF Eintrags
        self.visited = False
        self.ignored = False
        if not data is None:
            self.data = data
        else:
            self.data = {}

    def visitCheck(self):
        if self.typ == GROUP:
            self.visited = True
            for o in self.getAllSubItems():
                result = o.visitCheck()
                self.visited = self.visited and result
        return (self.visited or self.ignored)

    def ignoreIdent(self, key):
        if self.typ == GROUP:
            if self.data.has_key(key):
                for o in self.data[key]:
                    o.ignored = True                
        return
    
    def init(self, val):
        if self.typ == GROUP:
            self.data = {}
            for i in range(val):
                (key, typ, value, l) = ParseEntry()
                o = VDFObject(key, typ, l)
                o.line = l
                o.init(value)
                self.addSubItem(key, o)
        else:
            self.data = val

    def getLine(self):
        return self.line

    def printVDF(self, out, indent = 0):
        if self.typ == GROUP:
            groupitems = 0
            for (k,i) in self.data.items():
                if type(i) is type([]):
                    groupitems += len(i)
                    continue
                groupitems += 1
            VDFWrite(out, self.key, self.typ, groupitems, indent)
            for (k,i) in self.data.items():
                for obj in i:
                    obj.printVDF(out, indent+2)
        else:
            if self.key == "Kaempfe": # PATCH
                self.data = self.data.replace("\n", "\\")[:-1]
            VDFWrite(out, self.key, self.typ, self.data, indent)

    def getKey(self):
        return self.key

    def isGroup(self):
        return self.typ == GROUP

    def isList(self):
        return isinstance(self.data, list)

    def addSubItem(self, key, val):
        if self.typ != GROUP:
            raise TypeError, "VDFObject is not a group."
        if not isinstance(val, VDFObject):
            raise TypeError, "VDFObject expected"
        if self.data.has_key(key):
            self.data[key].append(val)
        else:
            self.data[key] = [val]

    def getSubItem(self, key):
        "Liefert Liste von VDF-Objekten mit dem angegebenen Key, die Unterobjekte von self sind."
        if self.typ == GROUP:
            if self.data.has_key(key):
                for o in self.data[key]:
                    if not o.isGroup():
                        o.visited = True
                return self.data[key]
            else:
                return []
        else:
            raise TypeError, "VDFObject is not a group."

    def getAllSubItems(self):
        "Liefert Liste aller Unterobjekte von self. Die Liste enthaelt nur VDF-Objekte"
        if self.typ == GROUP:
            result = []
            for i in self.data.values():
                if isinstance(i, list):
                    result.extend(i)
                else:
                    result.append(i)
            return result
        else:
            raise TypeError, "VDFObject is not a group."

    def getSingleSubItem(self, key):
        "Liefert einzelnes Subobjekt als VDF-Objekt"
        if self.typ == GROUP:
            if self.data.has_key(key):
                val = self.data[key]
                if len(val) == 1:
                    val[0].visited = True
                    return val[0]
                else:
                    raise TypeError, "VDFObject has multiple entries for key " + key
            else:
                return None
        else:
            raise TypeError, "VDFObject is not a group"

    def getSimpleValue(self, key):
        if self.typ == GROUP:
            if self.data.has_key(key):
                val = self.data[key]
                if len(val) == 1:
                    if val[0].typ == GROUP:
                        raise TypeError, "Subobjekt ist nicht simple"
                    val[0].visited = True
                    return val[0].data # der eigentliche Wert (int, string,...)
                else:
                    if key == "Wetter": # PATCH: CR-Fehler, Wetter kam in aelteren CRs mehrfach pro Region vor.
                        if val[0].typ == GROUP:
                            raise TypeError, "Subobjekt ist nicht simple"
                        val[0].visited = True
                        return val[0].data
                    raise TypeError, "VDFObject has multiple entries for key " + key
            else:
                return None
        else:
            raise TypeError, "VDFObject is not a group"

    def getAllSimpleValues(self, key):
        if self.typ == GROUP:
            if self.data.has_key(key):
                val = self.data[key] # val ist eine Liste von VDF_Objekten!
                for v in val: v.visited = True
                if GROUP in map(lambda x: x.typ, val):
                    raise TypeError, "Subobjekt ist nicht simple"
                return map(lambda x: x.data, val) #     erzeugt Liste von Daten
            else:
                return []
        else:
            raise TypeError, "VDFObject is not a group"

    def setSimpleValue(self, key, value):
        if self.typ == GROUP:
            try:
                val = self.data[key]
                if len(val) == 1:
                    self.data[key] = [value]
                else:
                    raise TypeError, "VDFObject has multiple entries for key " + key
            except KeyError:
                self.data[key] = [value]
        else:
            raise TypeError, "VDFObject is not a group"

    def hasValue(self, key):
        if self.typ == GROUP:
            return self.data.has_key(key)
        else:
            raise TypeError, "VDFObject is not a group"

    def hasSimpleValue(self, key):
        if self.typ == GROUP:
            if self.data.has_key(key):
                val = self.data[key]
                return not (GROUP in map(lambda x: x.typ, val))
            else:
                return False
        else:
            raise TypeError, "VDFObject is not a group"

    def len(self):
        if not self.isList():
            raise TypeError, "VDFObject is not a List"
        else:
            return len(self.data)

    def __int__(self):
        t = self.typ
        if t is FLAG:
            i = self.data
        elif t is INT:
            i = self.data
        else:
            raise TypeError, "Not supported for this vdftype"
        return i

    def __float__(self):
        t = self.typ
        if t is DOUBLE:
            i = self.data
        else:
            raise TypeError, "Not supported for this vdftype"
        return i

    def __str__(self):
        t = self.typ
        if t is FLAG:
            s = str(self.data)
        elif t is INT:
            s = str(self.data)
        elif t is DOUBLE:
            s = str(self.data)
        elif t is TEXT:
            s = self.data
        elif t is FORMATED_TEXT:
            s = self.data
        elif t is TZPAIR:
            pair = self.data
            s = pair[0] + "(" + str(pair[1]) + ")"
        else:
            s = super(object, self).__str__()
        return s
