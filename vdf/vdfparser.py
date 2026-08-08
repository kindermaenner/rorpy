#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: vdfparser.py,v 2.1 2005/02/24 18:16:32 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# Wrapper fuer die native-Implementation des VDF-Parsers.
#
# ---------------------------------------------------------------------------


import sys
_pythonVersion = sys.version [:3]
if _pythonVersion == "2.2":
    from python22.vdfparser import *
elif _pythonVersion == "2.3":
    from python23.vdfparser import *
elif _pythonVersion == "2.4":
    from python24.vdfparser import *
else:
    raise ImportError("No module for python version " + sys.version [:3] + " available")
