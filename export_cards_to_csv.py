# -*- coding: utf-8 -*-
"""
Export the Browser's selected rows to a csv data file

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

This addon exports the contents of the Browser's selected rows to a csv
    file that is escaped/quoted etc to be compatible with MS Excel.
You can control which columns are exported by adding/removing
    columns from the Browser's list.

To use:
    1. Open the Browse window.
    2. Select the rows you want to export. (If you want all rows,
        click on the "Edit" menu, then click on "Select All".
    3. Click on the "Edit" menu, then click on "Export Selected to CSV".
    4. Select the file name/location where you want the file saved.

Note: I wrote this because I wanted access to the Due dates and intervals
    to analyze in another program. As far as I can see it exports the other types
    of fields, including the text fields, without any problems. But I have not
    looked closely at anything except for the date fields.

Warning: buyer beware ... The author is not a python, nor a qt programmer

Support: None. Use at your own risk. If you do find a problem please email me
    steveawa@gmail.com but no promises.

Version2 25Jun2013   Fix bug introduced in Anki2.09 due to change in getSaveFile()
"""

import sys, csv, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from aqt.utils import getSaveFile, showWarning
from aqt import mw



#I am not sure if I needed to do this, but I just wanted an object that could stand
#    in for the Index objects that browser.py DataModel>>columnData    was expecting
class RowAndColumn(object):
    def __init__(self, r, c):
        self.irow = r
        self.icolumn = c

    def row(self):
        return self.irow

    def column(self):
        return self.icolumn

#copied from Exporter class
#Possibly not necessary as the csv writer object is set to the excel dialect?
def escapeText(text):
    "Escape newlines and tabs, and strip Anki HTML."
    text = text.replace("\n", "<br>")
    text = text.replace("\t", " " * 8)
    return text


def onExportList(browser):
    # big reach!
    if not browser.form.tableView.selectionModel().hasSelection():
        showWarning("Please select 1 or more rows", browser, help="")
        return
    path = getSaveFile(browser, _("Export Browser List"), "exportcsv", _("Cards as CSV"), '.csv', 'exportcsv.csv')
    if not path:
        return
    file = open(path, "wb")
    writer = csv.writer(file, dialect='excel')

    for rowIndex in browser.form.tableView.selectionModel().selectedRows():
        #wasn't sure if I could modify the "Index" objects we get back from
        #  the selection model. Since the columnData function only accesses
        #  the row() and column() functions, seemed safer to create new
        #  instances.
        row = rowIndex.row()
        rowdata = []
        for column in range(browser.model.columnCount(0)):
            index = RowAndColumn(row, column)
            #let the browser model's columnData function do all the hard work
            answer = escapeText(browser.model.columnData(index))
            rowdata.append(answer.encode('utf8'))
        writer.writerow(rowdata)
    file.close()


def setupMenu(browser):
    a = QAction("Export Selected To CSV", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda b=browser: onExportList(b))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


addHook("browser.setupMenus", setupMenu)