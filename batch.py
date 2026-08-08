#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

def MainFunction():
    f = open("test.bat", "wt")
    i = 91
    while i < 163:
        string = "rorpy.py cr=\"../../games/rorqual/aw/aus/A%dP826.CR zug=\"../../games/rorqual/aw/aus/A%dP826.AUS\n" % (i, i)
        f.write(string)
        i += 1
    f.close()

if __name__ == "__main__":
    MainFunction()