#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: wwriter.py,v 2.2 2005/02/24 18:18:15 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Klasse WrapedPrinter:
#    Erzeugt neues Printout Objekt mit den u.a. Eigenschaften.
#    Benoetigt Parameter out (Dateihandle), wrap (max. Zeilenlaenge)
#    und indent Einrueckung bei Wordwrap)
#    defaults: wrap = 72, indent = 2
#
# WrapedPrinter.write:
#    Der String str wird in den Output-Stream out geschrieben.
#    Dabei werden folgende Bedingungen eingehalten:
#    1. Das LF Zeichen (\n) bewirkt, dass der String in eine neue Zeile um-
#       gebrochen wird.
#    2. Ist der String laenger als wrap Zeichen, wird versucht vor dem
#       wrap-ten Zeichen eine neue Zeile zu beginnen.
#    3. Strings werden nur an Wortgrenzen umgebrochen.
#    4. Bei einem Word-Wrap beginnt der neue String jeweils mit einem Nicht-
#       Whitespace.
#    5. Nach einem erfolgeten Wordwrap werden dem nachfolgendem String
#       indent Whitespaces vorangestellt (d.h. er wird entsprechend
#       eingerueckt.)
#    6. Die Einruecktiefe (Indent) wird bei der Stringlaenge beruecksichtigt.
#    7. Existiert vor der Wrap-ten Stelle im String keine Wortgrenze, so
#       wird die naechste Wortgrenze gesucht. (d.h. der String ist dann
#       laenger als wrap Zeichen).
#    Ist der String str leer, so wird keine Ausgabe getaetigt.
#    wrap muss immer groesser als indent sein!
#    wprint liefert keinen Rueckgabewert.
#
# WrapedPrinter.flush:
#    interner Puffer wird geleert und mit newline abgeschlossen in den
#    Ausgabestream geschrieben. Der Puffer ist danach leer.
#
# WrapedPrinter.seek:
#    Fuehrt zunaechst ein flush aus und setzt dann den Filepointer der zuge-
#    hoerigen Datei. Semantik wie bei File.seek.
#
# WrapedPrinter.setIndent:
#    Fuehrt zunaechst ein flush aus und setzt dann den Indent neu.
# ---------------------------------------------------------------------------

__all__  = ["WrapedPrinter"]

def wprint(out, str, wrap, indent):
    tz = " "
    pos = wrap
    if len(str) > wrap :
        while pos >= 0 and not str[pos] in tz:
            pos = pos - 1
        if pos < 0:
            pos = wrap+1
            while pos < len(str) and not str[pos] in tz:
                pos = pos + 1
        if pos < 0 or pos >= len(str):
            out.write(str + "\n")
            return ""
        out.write(str[:pos] + "\n") # links von pos einschl. pos
        str = " " * indent + str[pos+1:].lstrip() # rest
    while len(str) > wrap:
        pos = wrap
        while pos >= indent and not str[pos] in tz:
            pos = pos - 1
        if pos < indent:
            pos = wrap+1
            while pos < len(str) and not str[pos] in tz:
                pos = pos + 1
        if pos < indent or pos >= len(str):
            out.write(str + "\n")
            return ""
        out.write(str[:pos] + "\n") # links von pos einschl. pos
        str = " " * indent + str[pos+1:].lstrip() # rest
    return str

class WrapedPrinter:
    def __init__(self, out, wrap = 70, indent = 2):
        self.out = out
        self.wrap = wrap
        self.indent = indent
        self.b = ""

    def write(self, str):
        self.b += str
        while 1:
            pos = self.b.find("\n")
            if pos != -1:
               s = self.b[:pos] # alles VOR "\n"
               s = wprint(self.out, s, self.wrap, self.indent)
               self.out.write(s+"\n")
               self.b = self.b[pos+1:] # alles nach "\n"
               continue
            else:
                break
        if len(self.b) > self.wrap:
            self.b = wprint(self.out, self.b, self.wrap, self.indent)

    def flush(self):
        if len(self.b) > 0:
            self.out.write(self.b + "\n")
            self.b = ""
        self.out.flush()

    def seek(self, offs, whence = 0):
        self.flush()
        self.out.seek(offs, whence)

    def setIndent(self, indent):
        self.flush()
        self.indent = indent
