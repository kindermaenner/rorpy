#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ---------------------------------------------------------------------------
#
# $Id: configure.py,v 2.2 2005/05/12 22:50:37 kdm Exp $
#
# ---------------------------------------------------------------------------
#
# wx-basierte Oberflaeche zur Konfiguration von Rorpy. Liest beim Start
# data/configuration.py ein und ueberschreibt diese Datei beim Speichern mit
# den aktualisierten Daten.
#
# ---------------------------------------------------------------------------

__all__ =  ["ConfDialog"]

import os
import sys
import wx
import wx.lib.mixins.listctrl as listmix
from data.configuration import *
from rorqual.constants  import MESSAGE_TEXT
from util.system        import relativepath

# Dateiendungen, die im Dateidialog als Filter angeboten werden
wildcardAW   = "Auswertung (*.aus)|*.aus|" \
               "Alle Dateien (*.*)|*.*"
wildcardCR   = "CR (*.cr)|*.cr|"     \
               "Alle Dateien (*.*)|*.*"
wildcardTurn = "Zug (*.zug)|*.zug|"    \
               "Alle Dateien (*.*)|*.*"

class EditListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.TextEditMixin.__init__(self)

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetBackgroundColour(wx.Colour(192, 192, 192))

        self.cmdSave       = wx.Button(self, -1, "Speichern")
        self.cmdExit       = wx.Button(self, -1, "Beenden")
        self.nbook         = wx.Notebook(self, -1, style=0)
        self.tabScripts    = wx.Panel(self.nbook, -1)
        self.tabOutput     = wx.Panel(self.nbook, -1)
        self.tabInput      = wx.Panel(self.nbook, -1)
##        self.tabMessages   = wx.Panel(self.nbook, -1)

        # Controls und Einstellungen fuer die auszufuehrenden Skripte
        self.cbCassandra   = wx.CheckBox(self.tabScripts, -1, "Cassandra")
        self.cbBuildings   = wx.CheckBox(self.tabScripts, -1, "Gebaeudeuebersicht")
        self.cbProduction  = wx.CheckBox(self.tabScripts, -1, "Gesamtproduktion")
        self.cbTrading     = wx.CheckBox(self.tabScripts, -1, "Handelsuebersicht")
        self.cbTaskmasters = wx.CheckBox(self.tabScripts, -1, "Lehrerliste")
        self.cbMagicians   = wx.CheckBox(self.tabScripts, -1, "Magierliste")
        self.cbInventory   = wx.CheckBox(self.tabScripts, -1, "Reischsinventur")
        self.cbPopulation  = wx.CheckBox(self.tabScripts, -1, "Volkszaehlung")
        self.cbScore       = wx.CheckBox(self.tabScripts, -1, "Auswertung")
        self.cbGunmen      = wx.CheckBox(self.tabScripts, -1, "Bewaffnete")

        self.cbBuildings.SetValue(DO_BUILDINGS == 1)
        self.cbCassandra.SetValue(DO_CASSANDRA == 1)
        self.cbInventory.SetValue(DO_INVENTORY == 1)
        self.cbMagicians.SetValue(DO_MAGICIANS == 1)
        self.cbPopulation.SetValue(DO_POPULATION == 1)
        self.cbProduction.SetValue(DO_PRODUCTION == 1)
        self.cbTaskmasters.SetValue(DO_TASKMASTERS == 1)
        self.cbTrading.SetValue(DO_TRADING == 1)
        self.cbScore.SetValue(DO_SCORE == 1)
        self.cbGunmen.SetValue(DO_GUNMEN == 1)

        # Controls und Einstellungen fuer die Ausgabedateien
        self.lblBuildings  = wx.StaticText(self.tabOutput, -1, "Gebaeudeuebersicht ")
        self.lblCassandra  = wx.StaticText(self.tabOutput, -1, "Cassandra ")
        self.lblInventory  = wx.StaticText(self.tabOutput, -1, "Reichsinventur ")
        self.lblMagicians  = wx.StaticText(self.tabOutput, -1, "Magierliste ")
        self.lblPopulation = wx.StaticText(self.tabOutput, -1, "Volkszaehlung ")
        self.lblProduction = wx.StaticText(self.tabOutput, -1, "Gesamtproduktion ")
        self.lblTaskmaster = wx.StaticText(self.tabOutput, -1, "Lehrerliste ")
        self.lblTrading    = wx.StaticText(self.tabOutput, -1, "Handelsuebersicht ")
        self.lblScore      = wx.StaticText(self.tabOutput, -1, "Auswertung ")
        self.lblGunmen     = wx.StaticText(self.tabOutput, -1, "Bewaffnete ")

        self.txtBuildings  = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtCassandra  = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtProduction = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtTrading    = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtTaskmaster = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtMagicians  = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtInventory  = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtPopulation = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtScore      = wx.TextCtrl(self.tabOutput, -1, "")
        self.txtGunmen     = wx.TextCtrl(self.tabOutput, -1, "")

        self.txtCassandra.SetValue(FILE_CASSANDRA)
        self.txtBuildings.SetValue(FILE_BUILDINGS)
        self.txtInventory.SetValue(FILE_INVENTORY)
        self.txtMagicians.SetValue(FILE_MAGICIANS)
        self.txtPopulation.SetValue(FILE_POPULATION)
        self.txtProduction.SetValue(FILE_PRODUCTION)
        self.txtTaskmaster.SetValue(FILE_TASKMASTERS)
        self.txtTrading.SetValue(FILE_TRADING)
        self.txtScore.SetValue(FILE_SCORE)
        self.txtGunmen.SetValue(FILE_GUNMEN)

        # Controls und Einstellungen fuer die Eingabedateien
        self.lblAW   = wx.StaticText(self.tabInput, -1, "Auswertung ")
        self.lblCR   = wx.StaticText(self.tabInput, -1, "CR ")
        self.lblTurn = wx.StaticText(self.tabInput, -1, "Zug ")

        self.txtAW   = wx.TextCtrl(self.tabInput, -1, "")
        self.txtCR   = wx.TextCtrl(self.tabInput, -1, "")
        self.txtTurn = wx.TextCtrl(self.tabInput, -1, "")

        self.txtAW.SetValue(FILE_AW)
        self.txtCR.SetValue(FILE_CR)
        self.txtTurn.SetValue(FILE_TURN)

        self.cmdOpenAW   = wx.BitmapButton(self.tabInput, 3, wx.Bitmap("data\\graphixs\\input.ico", wx.BITMAP_TYPE_ANY))
        self.cmdOpenCR   = wx.BitmapButton(self.tabInput, 4, wx.Bitmap("data\\graphixs\\input.ico", wx.BITMAP_TYPE_ANY))
        self.cmdOpenTurn = wx.BitmapButton(self.tabInput, 5, wx.Bitmap("data\\graphixs\\input.ico", wx.BITMAP_TYPE_ANY))

        # Controls und Einstellungen fuer die Nachrichtenverwaltung
##        self.txtMsgText  = wx.TextCtrl(self.tabMessages, -1, "")
##        self.lstMessages = EditListCtrl(self.tabMessages, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
##        self.lstMessages.InsertColumn(0, "ID")
##        self.lstMessages.InsertColumn(1, "ERR")
##        self.lstMessages.InsertColumn(2, "WARN")
##        self.lstMessages.InsertColumn(3, "HINT")
##        self.lstMessages.InsertColumn(4, "IGN")
##        self.lstMessages.InsertColumn(5, "Nachrichtentext")
##        msgTextIDs = MESSAGE_TEXT.keys()
##        for x in msgTextIDs:
##            index = self.lstMessages.InsertStringItem(sys.maxint, str(x))
##            self.lstMessages.SetStringItem(index, 0, str(x))
##            if x in MOVE_TO_ERR:
##                self.lstMessages.SetStringItem(index, 1, "x")
##            else:
##                self.lstMessages.SetStringItem(index, 1, "")
##            if x in MOVE_TO_WARN:
##                self.lstMessages.SetStringItem(index, 2, "x")
##            else:
##                self.lstMessages.SetStringItem(index, 2, "")
##            if x in MOVE_TO_HINT:
##                self.lstMessages.SetStringItem(index, 3, "x")
##            else:
##                self.lstMessages.SetStringItem(index, 3, "")
##            if x in IGNORE_MESSAGE:
##                self.lstMessages.SetStringItem(index, 4, "x")
##            else:
##                self.lstMessages.SetStringItem(index, 4, "")
##            self.lstMessages.SetStringItem(index, 5, MESSAGE_TEXT[x])
##            self.lstMessages.SetItemData(index, x)
##        self.lstMessages.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
##        self.lstMessages.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
##        self.lstMessages.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
##        self.lstMessages.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
##        self.lstMessages.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
##        self.lstMessages.SetColumnWidth(5, wx.LIST_AUTOSIZE)

        # Zuordnung der Events
        self.Bind(wx.EVT_BUTTON, self.OnCmdSaveClick, self.cmdSave)
        self.Bind(wx.EVT_BUTTON, self.OnCmdExitClick, self.cmdExit)
        self.Bind(wx.EVT_BUTTON, self.OnCmdOpenAWClick, self.cmdOpenAW)
        self.Bind(wx.EVT_BUTTON, self.OnCmdOpenCRClick, self.cmdOpenCR)
        self.Bind(wx.EVT_BUTTON, self.OnCmdOpenTurnClick, self.cmdOpenTurn)

        # Anordnung der Controls innerhalb des Notebooks
        sizerScripts     = wx.BoxSizer(wx.VERTICAL)
        sizerOutput      = wx.FlexGridSizer(10,2,0,0)
        sizerInput       = wx.FlexGridSizer(3,3,0,0)
##        sizerMsgHandling = wx.BoxSizer(wx.VERTICAL)
        sizerAW          = wx.BoxSizer(wx.HORIZONTAL)
        sizerCR          = wx.BoxSizer(wx.HORIZONTAL)
        sizerTurn        = wx.BoxSizer(wx.HORIZONTAL)

        sizerScripts.Add(self.cbCassandra, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbBuildings, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbProduction, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbTrading, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbTaskmasters, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbMagicians, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbInventory, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbPopulation, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbScore, 0, wx.FIXED_MINSIZE, 0)
        sizerScripts.Add(self.cbGunmen, 0, wx.FIXED_MINSIZE, 0)
        self.tabScripts.SetAutoLayout(True)
        self.tabScripts.SetSizer(sizerScripts)
        sizerScripts.Fit(self.tabScripts)
        sizerScripts.SetSizeHints(self.tabScripts)

        sizerInput.AddGrowableCol(1)
        sizerInput.Add(self.lblAW, 0, wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.txtAW, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.cmdOpenAW, 0, wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.lblCR, 0, wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.txtCR, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.cmdOpenCR, 0, wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.lblTurn, 0, wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.txtTurn, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerInput.Add(self.cmdOpenTurn, 0, wx.FIXED_MINSIZE, 0)
        self.tabInput.SetAutoLayout(True)
        self.tabInput.SetSizer(sizerInput)
        sizerInput.Fit(self.tabInput)
        sizerInput.SetSizeHints(self.tabInput)

        sizerOutput.AddGrowableCol(1)
        sizerOutput.Add(self.lblBuildings, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtBuildings, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblCassandra, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtCassandra, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblProduction, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtProduction, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblTrading, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtTrading, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblTaskmaster, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtTaskmaster, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblMagicians, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtMagicians, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblInventory, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtInventory, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblPopulation, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtPopulation, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblScore, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtScore, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.lblGunmen, 0, wx.FIXED_MINSIZE, 0)
        sizerOutput.Add(self.txtGunmen, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        self.tabOutput.SetAutoLayout(True)
        self.tabOutput.SetSizer(sizerOutput)
        sizerOutput.Fit(self.tabOutput)
        sizerOutput.SetSizeHints(self.tabOutput)

##        sizerMsgHandling.Add(self.txtMsgText, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
##        sizerMsgHandling.Add(self.lstMessages, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
##        self.tabMessages.SetAutoLayout(True)
##        self.tabMessages.SetSizer(sizerMsgHandling)
##        sizerMsgHandling.Fit(self.tabMessages)
##        sizerMsgHandling.SetSizeHints(self.tabMessages)

        self.nbook.AddPage(self.tabScripts, "Skripte")
        self.nbook.AddPage(self.tabOutput, "Ausgabe")
        self.nbook.AddPage(self.tabInput, "Eingabe")
##        self.nbook.AddPage(self.tabMessages, "Nachrichten")

        # Anordnung der Buttons
        cmdSizer = wx.BoxSizer(wx.HORIZONTAL)
        cmdSizer.Add(self.cmdSave, 0, wx.LEFT|wx.ALIGN_LEFT, 0)
        cmdSizer.Add((1, 1), 1)
        cmdSizer.Add(self.cmdExit, 0, wx.LEFT|wx.ALIGN_RIGHT, 0)

        # Anordnung von Button-Sizer und Notebook-Control
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.NotebookSizer(self.nbook), 1, wx.EXPAND, 1)
        sizer.Add(cmdSizer, 0, wx.EXPAND, 0)
        sizer.Fit(self)

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()

    def OnCmdOpenAWClick(self, evt):
        # FileOpen-Dialog erzeugen
        dlg = wx.FileDialog(self, message="Datei waehlen...", defaultDir=os.getcwd(), defaultFile="", wildcard=wildcardAW, style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            # Python-Liste der ausgewaehlten Dateien
            self.txtAW.SetValue(dlg.GetPaths()[0])

        # Dialog freigeben
        dlg.Destroy()
        pass

    def OnCmdOpenCRClick(self, evt):
        # FileOpen-Dialog erzeugen
        dlg = wx.FileDialog(self, message="Datei waehlen...", defaultDir=os.getcwd(), defaultFile="", wildcard=wildcardCR, style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            # Python-Liste der ausgewaehlten Dateien
            self.txtCR.SetValue(dlg.GetPaths()[0])

        # Dialog freigeben
        dlg.Destroy()
        pass

    def OnCmdOpenTurnClick(self, evt):
        # FileOpen-Dialog erzeugen
        dlg = wx.FileDialog(self, message="Datei waehlen...", defaultDir=os.getcwd(), defaultFile="", wildcard=wildcardTurn, style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            # Python-Liste der ausgewaehlten Dateien
            self.txtTurn.SetValue(dlg.GetPaths()[0])

        # Dialog freigeben
        dlg.Destroy()
        pass

    def OnCmdSaveClick(self, evt):
        try:
            workingDirectory = os.getcwd()
            output = open ('data/configuration.py', 'w+')
            output.write('#! /usr/bin/env python\n# -*- coding: iso-8859-1 -*-\n\n\n')

            output.write('# Auszufuehrende Skripte\n# Die Skripte, die durch den Aufruf von Rorpy ausgefuehrt werden.\n# 1 = ausfuehren, 0 = nicht ausfuehren\n')
            if (self.cbBuildings.GetValue() == True):   output.write('DO_BUILDINGS   = 1\n')
            else:                                       output.write('DO_BUILDINGS   = 0\n')
            if (self.cbCassandra.GetValue() == True):   output.write('DO_CASSANDRA   = 1\n')
            else:                                       output.write('DO_CASSANDRA   = 0\n')
            if (self.cbInventory.GetValue() == True):   output.write('DO_INVENTORY   = 1\n')
            else:                                       output.write('DO_INVENTORY   = 0\n')
            if (self.cbMagicians.GetValue() == True):   output.write('DO_MAGICIANS   = 1\n')
            else:                                       output.write('DO_MAGICIANS   = 0\n')
            if (self.cbPopulation.GetValue() == True):  output.write('DO_POPULATION  = 1\n')
            else:                                       output.write('DO_POPULATION  = 0\n')
            if (self.cbProduction.GetValue() == True):  output.write('DO_PRODUCTION  = 1\n')
            else:                                       output.write('DO_PRODUCTION  = 0\n')
            if (self.cbTaskmasters.GetValue() == True): output.write('DO_TASKMASTERS = 1\n')
            else:                                       output.write('DO_TASKMASTERS = 0\n')
            if (self.cbTrading.GetValue() == True):     output.write('DO_TRADING     = 1\n')
            else:                                       output.write('DO_TRADING     = 0\n')
            if (self.cbScore.GetValue() == True):       output.write('DO_SCORE       = 1\n')
            else:                                       output.write('DO_SCORE       = 0\n')
            if (self.cbGunmen.GetValue() == True):      output.write('DO_GUNMEN      = 1\n')
            else:                                       output.write('DO_GUNMEN      = 0\n')

            output.write('\n\n# Eingabedateien\n# Die hier angegebenen Dateinamen werden durch per Parameter uebergebene\n# Dateinamen ueberschrieben. Bitte beachten, dass \\ fuer Python als\n# Sonderzeichen (\\\\) dargestellt werden muss.\n')
            output.write('FILE_AW   = \"' + relativepath(workingDirectory, self.txtAW.GetValue()).replace("\\", "\\\\") + '\"\n')
            output.write('FILE_CR   = \"' + relativepath(workingDirectory, self.txtCR.GetValue()).replace("\\", "\\\\") + '\"\n')
            output.write('FILE_TURN = \"' + relativepath(workingDirectory, self.txtTurn.GetValue()).replace("\\", "\\\\") + '\"\n')

            output.write('\n\n# Ausgabedateien\n# Die Ausgaben erfolgen immer in das Unterverzeichnis out.\n')
            output.write('FILE_BUILDINGS   = \"' + self.txtBuildings.GetValue() + '\"\n')
            output.write('FILE_CASSANDRA   = \"' + self.txtCassandra.GetValue() + '\"\n')
            output.write('FILE_INVENTORY   = \"' + self.txtInventory.GetValue() + '\"\n')
            output.write('FILE_MAGICIANS   = \"' + self.txtMagicians.GetValue() + '\"\n')
            output.write('FILE_POPULATION  = \"' + self.txtPopulation.GetValue() + '\"\n')
            output.write('FILE_PRODUCTION  = \"' + self.txtProduction.GetValue() + '\"\n')
            output.write('FILE_TASKMASTERS = \"' + self.txtTaskmaster.GetValue() + '\"\n')
            output.write('FILE_TRADING     = \"' + self.txtTrading.GetValue() + '\"\n')
            output.write('FILE_SCORE       = \"' + self.txtScore.GetValue() + '\"\n')
            output.write('FILE_GUNMEN      = \"' + self.txtGunmen.GetValue() + '\"\n')

            output.write('\n\n# Boolsche Variable, die angibt, ob in der Cassandra-Ausgabe die Nachrichten-ID\n# mit ausgegeben werden soll. Dieses ist sinnvoll, wenn man eine Nachricht\n# unterdruecken oder sie einer anderen Kategorie zuordnen moechte.\n')
            if SHOW_MESSAGE_ID: output.write('SHOW_MESSAGE_ID = 1\n')
            else:               output.write('SHOW_MESSAGE_ID = 0\n')

##            ignoredMessages = []
##            movedToError    = []
##            movedToWarning  = []
##            movedToHint     = []
##            for x in range(self.lstMessages.GetItemCount()):
##                if self.lstMessages.GetItem(x,1).GetText() != "": movedToError += [x + 1]
##                if self.lstMessages.GetItem(x,2).GetText() != "": movedToWarning += [x + 1]
##                if self.lstMessages.GetItem(x,3).GetText() != "": movedToHint += [x + 1]
##                if self.lstMessages.GetItem(x,4).GetText() != "": ignoredMessages += [x + 1]

            output.write('\n\n# ID-Liste der nicht auszugebenden Meldungen\n')
            output.write('IGNORE_MESSAGE = ' + str(IGNORE_MESSAGE))
            output.write('\n\n# Listen, die die Nachrichten enthalten, die vom Benutzer der entsprechenden\n# Kategorie zugeordnet wurden.\n')
            output.write('MOVE_TO_ERR  = ' + str(MOVE_TO_ERR) + '\n')
            output.write('MOVE_TO_WARN = ' + str(MOVE_TO_WARN) + '\n')
            output.write('MOVE_TO_HINT = ' + str(MOVE_TO_HINT) + '\n')
            output.write('MOVE_TO_INFO = ' + str(MOVE_TO_INFO))

        except IOError:
            dlg_m = wxMessageDialog (self, 'Es ist ein Fehler beim Speichern der konfiguration aufgetreten!', 'Fehler!', wxOK)
            dlg_m.ShowModal()
            dlg_m.Destroy()

    def OnCmdExitClick(self, evt):
        self.Close()

class ConfDialog(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "Rorpy-Konfigurationsdialog")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True


if __name__ == "__main__":
    app = ConfDialog(redirect=True)
    app.MainLoop()
