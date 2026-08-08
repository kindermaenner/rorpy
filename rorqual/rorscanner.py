#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: rorscanner.py,v 2.1 2005/02/24 19:36:07 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Wrapper fuer die native-Implementation des Zug-Scanners.
#
# ---------------------------------------------------------------------------

import sys

_pythonVersion = sys.version [:3]
if _pythonVersion == "2.2":
    from python22.rorscanner import *
elif _pythonVersion == "2.3":
    from python23.rorscanner import *
elif _pythonVersion == "2.4":
    from python24.rorscanner import *
else:
    raise ImportError("No module for python version " + sys.version [:3] + " available")
