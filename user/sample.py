#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: sample.py,v 2.1 2005/05/12 21:47:04 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Dieses Skript dient als Beispiel fuer die Einbindung eigener Skripte in
# Rorpy. 
#
# ---------------------------------------------------------------------------

__all__ = ["sampleMain"]

# Dieser Import ist immer notwendig, wenn man auf dem rorObj arbeiten moechte.
from rorqual.objects import *

def sampleMain(rorObj, explicit):
    # Wenn in eigenen Skripten etwas am rorObj veraendert wird, dann bitte
    # das rorObj kopieren. Damit wird verhindert, dass die Skripte sich gegen-
    # seitig beeinflussen.
    # rorObjClone = rorObj.clone()
    
    # Die print-Anweisung einkommentieren, damit auch zu sehen ist, dass
    # dieses Skript ausgefuehrt wird.
    # print "Dieses Skript wurde ausgefuehrt."
    return