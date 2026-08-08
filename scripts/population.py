#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: population.py,v 2.4 2005/02/26 00:38:37 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# def populationMain(aw, filename = None):
#    aw       - das RorAW-Objekt
#    explicit - Gibt an, ob das Skript unabhaengig von der Konfiguration
#               ausgefuehrt werden soll.
#    Das Skript erstellt eine kleine Zusammenfassung ueber finanzielle
#    Resourcen der Partei.
#    Es werden nur Regionen beachtet, die zum eigenen Reich gehoeren.
#
# ---------------------------------------------------------------------------

__all__ = ["populationMain"]

from data.configuration import FILE_POPULATION, DO_POPULATION

def populationMain(aw, explicit):
    if not DO_POPULATION and not explicit: # benutzerdefinierte Einstellungen beachten
        return

    f = file(FILE_POPULATION, "w")

    print "creating " + FILE_POPULATION + "."*3 ,

    regions             = aw.getSortedRegionsAsList()
    Servants            = aw.quantityLeaders + aw.quantityRegulars
    Peasants            = 0
    IncomeTaxes         = 0
    IncomeWork          = 0
    IncomeEntertainment = 0

    for region in regions:
        if region.isShortReport:
            continue
        if not region.isTerritory(aw.partynumber):
            continue
        IncomeTaxes         += region.IncomeTaxes
        IncomeWork          += region.IncomeWork
        IncomeEntertainment += region.IncomeEntertainment
        Peasants            += region.peasants * 1000
    f.write("Im %s des Jahres %d durchquerten tausende Buerokraten Euer Reich,\n" %(aw.month, aw.year))
    f.write("welches als %s bekannt und vieleicht gefuerchtet ist.\n\n" %(aw.partyname))
    f.write("Folgendes Wissen haben sie in unermuedlichen 15-Stunden-Wochen zusammengetragen:\n\n")
    f.write("Sie herrschen ueber ein Volk von %d Wesen unterschiedlichster Voelker.\n" %(Peasants + Servants))
    f.write("Stolze %d ihrer Untertanen haben sich in Ihre Dienste gestellt und Leben\n" %(Servants))
    f.write("steuerfrei auf Staatskosten\n")
    f.write("--------------------------------------------------\n")
    f.write("Steuerpflicht aller Buerger           : %d\n" %(IncomeTaxes))
    f.write("Arbeitslohn fuer soziale Dienste      : %d\n" %(IncomeWork))
    f.write("Unterhaltungsausgaben fuer Kultur     : %d\n" %(IncomeEntertainment))
    f.write("--------------------------------------------------\n")
    f.write("Aus ihrem Volk herauszupressendes Vermoegen: %d\n\n" %(IncomeTaxes + IncomeWork + IncomeEntertainment))
    f.write("Leider war es aus versicherungstechnischen Gruenden nur moeglich, Euer eigenes Reichsgebiet zu durchqueren.")

    f.close()

    print "done."