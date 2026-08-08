#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
# $Id: bugreport.py,v 2.1 2005/04/04 17:49:43 kdm Exp $                       #
#                                                                             #
# --------------------------------------------------------------------------- #
#                                                                             #
#                                                                             #
#                                                                             #
# --------------------------------------------------------------------------- #

import os
import sys
import time
import traceback

def main():
    f = file('out/bugreport.txt', "w")
    writeBugreportHeader(f)
    writeBugreportFileinfo(f)

    try:
        from rorpy import rorpyMainFunction
        rorpyMainFunction()
    except:
        f.write('Aufgetretene Exception:\n')
        traceback.print_exc(file=f)

    f.close()

def writeBugreportHeader(f):
    # Zeit und Datum ermitteln
    (year, month, day, hour, min, sec) = time.localtime()[0:6]

    f.write('Rorpy-Bugreport vom %02i.%02i.%04i, %02i:%02i:%02i\n' % (day, month, year, hour, min, sec))
    f.write('Diese Datei bitte an rorpy@rorqual.de senden.\n\n')
    f.write('Allgemeine Informationen\n')
    f.write('Verwendetes Betriebssystem: ' + os.name + ', ' + sys.platform + '\n')
    f.write('Verwendete Python-Version: ' + sys.version + '\n')
    f.write('Vertreiber der Python-Version: ' + sys.copyright.split('\n')[0] + '\n')
    try:
        import wx
        f.write('Verwendete wx-Version: %i.%i.%i.%i\n' % wx.VERSION[0:4])
    except ImportError:
        pass
    f.write('\n')

def writeBugreportFileinfo(f):
    f.write('Informationen zu Rorpy\n')
    f.write('Datengrundlage:\n')
    f.write('   common.vdf:       ' + time.ctime(os.path.getmtime('data/common.vdf')) + '\n')
    f.write('   user.vdf:         ' + time.ctime(os.path.getmtime('data/user.vdf')) + '\n')
    f.write('   configuration.py: ' + time.ctime(os.path.getmtime('data/configuration.py')) + '\n')
    f.write('Pythonskripte:\n')
    f.write('   bugreport.py:     ' + time.ctime(os.path.getmtime('bugreport.py')) + '\n')
    f.write('   configure.py:     ' + time.ctime(os.path.getmtime('configure.py')) + '\n')
    f.write('   rorpy.py:         ' + time.ctime(os.path.getmtime('rorpy.py')) + '\n')
    f.write('   commands.py:      ' + time.ctime(os.path.getmtime('rorqual/commands.py')) + '\n')
    f.write('   constants.py:     ' + time.ctime(os.path.getmtime('rorqual/constants.py')) + '\n')
    f.write('   cr.py:            ' + time.ctime(os.path.getmtime('rorqual/cr.py')) + '\n')
    f.write('   kb.py:            ' + time.ctime(os.path.getmtime('rorqual/kb.py')) + '\n')
    f.write('   objects.py:       ' + time.ctime(os.path.getmtime('rorqual/objects.py')) + '\n')
    f.write('   references.py:    ' + time.ctime(os.path.getmtime('rorqual/references.py')) + '\n')
    f.write('   rorparser.py:     ' + time.ctime(os.path.getmtime('rorqual/rorparser.py')) + '\n')
    f.write('   rorparserutil.py: ' + time.ctime(os.path.getmtime('rorqual/rorparserutil.py')) + '\n')
    f.write('   rorscanner.py:    ' + time.ctime(os.path.getmtime('rorqual/rorscanner.py')) + '\n')
    f.write('   buildings.py:     ' + time.ctime(os.path.getmtime('scripts/buildings.py')) + '\n')
    f.write('   cassandra.py:     ' + time.ctime(os.path.getmtime('scripts/cassandra.py')) + '\n')
    f.write('   inventory.py:     ' + time.ctime(os.path.getmtime('scripts/inventory.py')) + '\n')
    f.write('   magicians.py:     ' + time.ctime(os.path.getmtime('scripts/magicians.py')) + '\n')
    f.write('   population.py:    ' + time.ctime(os.path.getmtime('scripts/population.py')) + '\n')
    f.write('   production.py:    ' + time.ctime(os.path.getmtime('scripts/production.py')) + '\n')
    f.write('   startup.py:       ' + time.ctime(os.path.getmtime('scripts/startup.py')) + '\n')
    f.write('   taskmasters.py:   ' + time.ctime(os.path.getmtime('scripts/taskmasters.py')) + '\n')
    f.write('   trading.py:       ' + time.ctime(os.path.getmtime('scripts/trading.py')) + '\n')
    f.write('   dictionaries.py:  ' + time.ctime(os.path.getmtime('util/dictionaries.py')) + '\n')
    f.write('   htmloutput.py:    ' + time.ctime(os.path.getmtime('util/htmloutput.py')) + '\n')
    f.write('   messages.py:      ' + time.ctime(os.path.getmtime('util/messages.py')) + '\n')
    f.write('   system.py:        ' + time.ctime(os.path.getmtime('util/system.py')) + '\n')
    f.write('   wwriter.py:       ' + time.ctime(os.path.getmtime('util/wwriter.py')) + '\n')
    f.write('   vdf.py:           ' + time.ctime(os.path.getmtime('vdf/vdf.py')) + '\n')
    f.write('   vdfparser.py:     ' + time.ctime(os.path.getmtime('vdf/vdfparser.py')) + '\n')
    f.write('Bibliotheken:\n')
    f.write('   rorscanner.dll:          ' + time.ctime(os.path.getmtime('rorscanner.dll')) + '\n')
    f.write('   vdfparser.dll:           ' + time.ctime(os.path.getmtime('vdfparser.dll')) + '\n')
    f.write('   python22/rorscanner.pyd: ' + time.ctime(os.path.getmtime('rorqual/python22/rorscanner.pyd')) + '\n')
    f.write('   python23/rorscanner.pyd: ' + time.ctime(os.path.getmtime('rorqual/python23/rorscanner.pyd')) + '\n')
    f.write('   python24/rorscanner.pyd: ' + time.ctime(os.path.getmtime('rorqual/python24/rorscanner.pyd')) + '\n')
    f.write('   python22/vdfparser.pyd:  ' + time.ctime(os.path.getmtime('vdf/python22/vdfparser.pyd')) + '\n')
    f.write('   python23/vdfparser.pyd:  ' + time.ctime(os.path.getmtime('vdf/python23/vdfparser.pyd')) + '\n')
    f.write('   python24/vdfparser.pyd:  ' + time.ctime(os.path.getmtime('vdf/python24/vdfparser.pyd')) + '\n')
    f.write('\n')

if __name__ == "__main__":
    main()