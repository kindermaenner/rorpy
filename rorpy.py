#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: rorpy.py,v 2.2 2005/05/12 22:22:17 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Hauptskript von Rorpy.
#
# ---------------------------------------------------------------------------

__all__ = ["rorpyMainFunction"]

import os
import sys
import imp
import stat
import fnmatch

from scripts.startup import parse_args, getRorObjects, init_kb, readCommands, patchKB

def runScripts(rorObj, dir, scriptToRun = None):
    if not os.access(dir, os.F_OK):
        return
    status = os.stat(dir)
    if not stat.S_ISDIR(status.st_mode):
        return
    filelist = os.listdir(dir)
    scripts = fnmatch.filter(filelist, "*.py")
    for script in scripts:
        scriptName = script[:-3]
        if not scriptToRun is None:
            if (scriptName != scriptToRun):
                continue
        if (scriptName == "__init__") or (scriptName == "startup"):
            continue
        m = imp.load_source(scriptName, dir + "/"+script)
        procName = scriptName + "Main"
        if not m.__dict__.has_key(procName):
            print "Funktion '" + procName + "' nicht gefunden in Skript '" + scriptName + "'"
        else:
            m.__dict__[procName](rorObj, not scriptToRun is None)
    return

def rorpyMainFunction():
    ret = parse_args()
    if ret is None:
        return

    if not os.path.isfile(ret["cr"]):
        print "Angegebene CR-Datei existiert nicht!"
        sys.exit(0)
    if (ret["turn"] != "") and not os.path.isfile(ret["turn"]):
        print "Angegebene Zug-Datei existiert nicht!"
        sys.exit(0)

    init_kb()

    rorObj = getRorObjects(ret["cr"])
    rorObj = readCommands(rorObj, ret["turn"])

    patchKB(rorObj)

    # Skripte im Verzeichnis scripts ausfuehren
    runScripts(rorObj, "scripts", ret["script"])

    # Skripte im Verzeichnis user ausfuehren
    runScripts(rorObj, "user", ret["script"])

    # offenhalten des Fensters, wenn gewuenscht
    if ret["link"]:
        raw_input("Bitte Return druecken...")

if __name__ == "__main__":
    rorpyMainFunction()