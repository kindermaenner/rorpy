#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: system.py,v 2.2 2005/02/24 19:25:54 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def relativepath(fromPath, toPath):
#    If it's possible the function returns an relaitve path from fromPath to
#    toPath. Otherwise it returns the unchanged toPath.
#
# def isRelativePath(path):
#    Checks whether path is a relative path or not.
#
# ---------------------------------------------------------------------------

__all__ = ["relativepath"]

import os

def relativepath(fromPath, toPath):
    # parameter check
    if (toPath == "") or (toPath is None):
        return ""

    # parameter check
    if (fromPath == "") or (fromPath is None):
        return toPath

    # if either is already a relative path it's impossible to generate one
    if isRelativePath(fromPath) or isRelativePath(toPath):
        return toPath

    # speciality for dos and windows: it's not possible to generate a relative
    # path if the paths belong to different partitons.
    if (os.name == 'dos') or (os.name == 'nt'):
        if fromPath[0:3] != toPath[0:3]:
            return toPath

    fromPath = fromPath.replace("\\", "/").split('/')
    toPath   = toPath.replace("\\", "/").split('/')
    for i in range(min(len(toPath),len(fromPath))):
        if toPath[i] != fromPath[i]: break
    else:
        i+=1
    return ("../" * len(fromPath[i:]) + "/".join(toPath[i:])).strip('/')

def isRelativePath(path):
    if os.name == 'posix':
        return (path[0] != '/')
    elif (os.name == 'dos') or (os.name == 'nt'):
        return (path[1] != ':')
    else:
        return True