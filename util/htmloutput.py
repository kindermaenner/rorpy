#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: htmloutput.py,v 2.1 2005/02/24 19:25:40 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Klasse HTMLPage:
#    HTMLPage.__init__(self, filename, title = None, creator = None):
#
#
#    HTMLPage.addStyleSheet(self, url):
#        Fuegt ein <link>-Tag fuer das angegebene CSS-File (url) hinzu.
#
#    HTMLPage.addHeadEntry(self, s):
#        Fuegt den angegebenen Kopfeintrag s hinzu.
#
#    HTMLPage.addNameMetaEntry(self, key, value):
#        Fuegt einen allgemeinen Metatag (key) hinzu und weist ihm den Wert
#        (value) hinzu.
#
#    HTMLPage.addHttpEquivMetaEntry(self, key, value):
#        Fuegt einen Metatag (key) hinzu, der vom Web-Server ausgelesen
#        werden soll, und weist ihm den Wert (value) hinzu.
#
#    HTMLPage.setBodyAttribute(self, key, value):
#        Fuegt dem Body den angegebenen Eintrag (key) mit Wert (value) hinzu.
#
#    HTMLPage.setTextColor(self, color):
#        Setzt die Standard-Textfarbe fuer die Seite.
#
#    HTMLPage.setBackgroundColor(self, color):
#        Setzt die Hintergrundfarbe der Seite.
#
#    HTMLPage.setLinkColor(self, color):
#        Setzt die Farbe fuer unbesuchte Links auf der Seite.
#
#    HTMLPage.setActiveLinkColor(self, color):
#        Setzt die Farbe fuer einen aktivierten Link.
#
#    HTMLPage.setVisitedLinkColor(self, color):
#        Setzt die Farbe fuer besuchte Links auf der Seite.
#
#    HTMLPage.startPage(self):
#        Schreibt den Kopf der Seite.
#
#    HTMLPage.endPage(self):
#        Beendet die Seite.
#
#    HTMLPage.startPar(self, align=None, style=None):
#        Beginnt einen neuen Abschnitt.
#
#    HTMLPage.endPar(self):
#        Beendet den aktuellen Abschnitt.
#
#    HTMLPage.newline(self):
#        Fuegt einen Zeilenumbruch hinzu.
#
#    HTMLPage.hline(self):
#        Fuegt eine horizontale Linie hinzu.
#
#    HTMLPage.heading(self, depth, text, align=None):
#        Fuegt eine Ueberschrift hinzu, die Ebene wird durch depth angegeben.
#
#    HTMLPage.startList(self, type=None):
#        Beginnt eine Liste.
#
#    HTMLPage.endList(self):
#        Beendet die aktuelle Liste.
#
#    HTMLPage.startListEntry(self):
#        Beginnt einen Listeneintrag.
#
#    HTMLPage.endListEntry(self):
#        Beendet den aktuellen Listeneintrag.
#
#    HTMLPage.startBold(self):
#        Beginnt einen Textbereich mit fetten Zeichen.
#
#    HTMLPage.endBold(self):
#        Beendet den aktuellen Textbereich mit fetten Zeichen.
#
#    HTMLPage.startItalic(self):
#        Beginnt einen Textbereich mit kursiven Zeichen.
#
#    HTMLPage.endItalic(self):
#        Beendet den aktuellen Textbereich mit kursiven Zeichnen.
#
#    HTMLPage.startUnderline(self):
#        Beginnt einen Textbereich mit unterstrichenen Zeichen.
#
#    HTMLPage.endUnterline(self):
#        Beendet den aktuellen Textbereich mit unterstrichenen Zeichnen.
#
#    HTMLPage.startTT(self):
#        Beginnt einen Textbereich mit proportionalen Zeichen.
#
#    HTMLPage.endTT(self):
#        Beendet den aktuellen Textbereich mit proportionalen Zeichen.
#
#    HTMLPage.startFont(self, color=None, size=None, face=None):
#        Beginnt einen Textbereich mit der angegebenen Schriftart (face).
#
#    HTMLPage.endFont(self):
#        Beginnt den aktuellen Textbereich mit eigener Schriftart.
#
#    HTMLPage.startAnchor(self, name):
#        Beginnt einen Anker.
#
#    HTMLPage.endAnchor(self):
#        Beendet einen Anker.
#
#    HTMLPage.setAnchor(self, text, name):
#        Kann als Ersatz fuer startAnchor und endAnchor benutzt werden.
#
#    HTMLPage.addRef(self, text, url = None, anchor = None, target = None,
#                    attributes = None):
#        Fuegt einen Link hinzu.
#
#    HTMLPage.addText(self, text):
#        Fuegt den angegebenen Text hinzu.
#
#    HTMLPage.addTextEx(self, text, attributes):
#        Fuegt den angegebenen Text hinzu und versieht ihn mit den an-
#        gegebenen Attributen.
#
#    HTMLPage.startNoBreak(self):
#        Beginnt einen Textbereich, in dem keine automatischen Umbrueche er-
#        laubt sind.
#
#    HTMLPage.endNoBreak(self):
#        Beendet den aktuellen Textbereich, in dem keine automatischen Um-
#        brueche erlaubt sind.
#
#    HTMLPage.beginTable(self, spalten, kopf, border = 1):
#        Beginnt eine Tabelle.
#
#    HTMLPage.addTableLine(self, cellText):
#        Fuegt eine Tabellenzeile hinzu.
#
#    HTMLPage.endTable(self):
#        Beendet die aktuelle Tabelle.
#
# ---------------------------------------------------------------------------

all = ["HTMLPage"]

DOCTYPE = '<!doctype html public "-//W3C//DTD HTML 4.0 //EN">\n'

class HTMLPage:
    def __init__(self, filename, title = None, creator = None):
        self.filename = filename
        self.f = None
        self.bodyAttributes = {}
        self.extraHeadEntries = []
        self.metaEntries_name = {}
        self.metaEntries_http = {}
        self.tablecolumn = 0
        if creator != None:
            self.addNameMetaEntry("generator", creator)
        else:
            self.addNameMetaEntry("generator", "Python HTML Generator")
        self.addHttpEquivMetaEntry("content-type", "text/html; charset=iso-8859-1")
        if title != None:
            self.addHeadEntry("<title>" + title + "</title>\n")
        else:
            self.addHeadEntry("<title>Unbenannt</title>\n")

    def addStyleSheet(self, url):
        self.addHeadEntry('<link rel="stylesheet" type="text/css" href="' + url +'">')

    def addHeadEntry(self, s):
        self.extraHeadEntries.append(s)

    def addNameMetaEntry(self, key, value):
        self.metaEntries_name[key] = value

    def addHttpEquivMetaEntry(self, key, value):
        self.metaEntries_http[key] = value

    def setBodyAttribute(self, key, value):
        self.bodyAttributes[key] = value

    def setTextColor(self, color):
        self.setBodyAttribute("text", color)

    def setBackgroundColor(self, color):
        self.setBodyAttribute("bgcolor", color)

    def setLinkColor(self, color):
        self.setBodyAttribute("link", color)

    def setVisitedLinkColor(self, color):
        self.setBodyAttribute("vlink", color)

    def setActiveLinkColor(self, color):
        self.setBodyAttribute("alink", color)

    def startPage(self):
        self.f = open(self.filename, "w")
        self.f.write(DOCTYPE)
        self.f.write("<html>\n")
        self.f.write("<head>\n")
        for (key, value) in self.metaEntries_http.items():
            self.f.write('<meta http-equiv="' + key + '" content="'+ value + '">\n')
        for (key, value) in self.metaEntries_name.items():
            self.f.write('<meta name="' + key + '" content="'+ value + '">\n')
        for line in self.extraHeadEntries:
            self.f.write(line)
        self.f.write("</head>\n")
        self.f.write("<body")
        if len(self.bodyAttributes) > 0:
            for (key, value) in self.bodyAttributes.items():
                self.f.write(" " + key + '="' + value + '"')
        self.f.write(">\n")

    def endPage(self):
        self.f.write("</body>\n")
        self.f.write("</html>\n")

    def startPar(self, align=None, style=None):
        text = "<p"
        if align != None:
            text += ' align="' + align + '"'
        if style != None:
            text += ' style="' + style + '"'
        text += ">"
        self.f.write(text)

    def endPar(self):
        self.f.write("</p>\n")

    def newline(self):
        self.f.write("<br/>\n")

    def hline(self):
        self.f.write("<hr/>\n")

    def heading(self, depth, text, align=None):
        tag = "h" + str(depth)
        if align is None:
            self.f.write("<" + tag+ ">" + text + "</" + tag + ">\n")
        else:
            self.f.write("<" + tag+ 'align="' + align + '">' + text + "</" + tag + ">\n")

    def startList(self, type=None):
        if type is None:
            self.f.write("<ul>\n")
        else:
            self.f.write('<ul type="' + type + '">\n')

    def endList(self):
        self.f.write('<ul>\n')

    def startListEntry(self):
        self.f.write('<li>')

    def endListEntry(self):
        self.f.write('</li>\n')

    def startBold(self):
        self.f.write('<b>')

    def endBold(self):
        self.f.write('</b>')

    def startItalic(self):
        self.f.write('<i>')

    def endItalic(self):
        self.f.write('</i>')

    def startUnderline(self):
        self.f.write('<u>')

    def endUnterline(self):
        self.f.write('</u>')

    def startTT(self):
        self.f.write('<tt>')

    def endTT(self):
        self.f.write('</tt>')

    def startFont(self, color=None, size=None, face=None):
        if (color, size, face) == (None, None, None):
            return
        text = "<font"
        if color != None:
            text += ' color="' + color + '"'
        if size != None:
            text += ' size="' + size + '"'
        if face != None:
            text += ' face="' + face + '"'
        text += ">"
        self.f.write(text)

    def endFont(self):
        self.f.write("</font>")

    def startAnchor(self, name):
        self.f.write('<a name="' + name + '">')

    def endAnchor(self):
        self.f.write('</a>')

    def setAnchor(self, text, name):
        self.f.write('<a name="' + name + '">' + text + '</a>')

    def addRef(self, text, url = None, anchor = None, target = None, attributes = None):
        if (url, anchor) == (None, None):
            return
        self.f.write('<a href="')
        if url != None:
            self.f.write(url)
        if anchor != None:
            self.f.write("#"+ anchor)
        self.f.write('"')
        if target != None:
            self.f.write(' target ="' + target + '"')
        if attributes != None:
            for k in attributes.keys():
                self.f.write(" " + k + '="' + attributes[k] + '"')
        self.f.write('>' + text + '</a>')

    def addText(self, text):
        self.f.write(text)

    def addTextEx(self, text, attributes):
        self.f.write("<span")
        for k in attributes.keys():
            self.f.write(" " + k + '="' + attributes[k] + '"')
        self.f.write(">" + text + "</span>")

    def startNoBreak(self):
        self.f.write("<nobr>")

    def endNoBreak(self):
        self.f.write("</nobr>")

    def beginTable(self, spalten, kopf, border = 1):
        self.f.write('<table border="' + str(border) + '">\n')
        self.tablecolumn = spalten
        self.addTableLine(kopf)

    def addTableLine(self, cellText):
        self.f.write('<tr>\n')
        for i in range(self.tablecolumn):
            self.f.write('<th>'+cellText[i]+'</th>\n')
        self.f.write('</tr>\n')

    def endTable(self):
        self.f.write('</table>\n')
        self.tablecolumn = 0
