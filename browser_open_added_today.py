# -*- coding: utf-8 -*-
"""
Adds a menu item into the "History" menu of the "Add" notes dialog that
   opens a Browser on the 'Added Today' view.

   https://ankiweb.net/shared/info/4168112055

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Support: Use at your own risk. If you do find a problem please email me
or use one the following forums, however there are certain periods
throughout the year when I will not have time to do any work on
these addons.

Github page:  https://github.com/steveaw/anki_addons
Anki addons: https://groups.google.com/forum/?hl=en#!forum/anki-addons

Changes:
20130715: After opening the browser, change the sort order to "Created"
    and select the most recent (top) card

"""
from anki.lang import _

from aqt.qt import *
from aqt.addcards import AddCards
from anki.hooks import wrap, runHook, addHook
import aqt


def onHistory(self):
    m = QMenu(self)
    for nid, txt in self.history:
        a = m.addAction(_("Edit %s") % txt)
        a.connect(a, SIGNAL("triggered()"),
                  lambda nid=nid: self.editHistory(nid))
    runHook("AddCards.onHistory", self, m)
    m.exec_(self.historyButton.mapToGlobal(QPoint(0, 0)))


def insert_open_browser_action(self, m):
    m.addSeparator()
    a = m.addAction("Open Browser on 'Added Today'")
    a.connect(a, SIGNAL("triggered()"),
              lambda self=self: show_browser_on_added_today(self))


def show_browser_on_added_today(self):
    browser = aqt.dialogs.open("Browser", self.mw)
    browser.form.searchEdit.lineEdit().setText("added:1")
    browser.onSearch()
    if u'noteCrt' in browser.model.activeCols:
        col_index = browser.model.activeCols.index(u'noteCrt')
        browser.onSortChanged(col_index, True)
    browser.form.tableView.selectRow(0)


def mySetupButtons(self):
    self.historyButton.setEnabled(True)

# from distutils.version import LooseVersion
# if LooseVersion (aqt.appVersion) < LooseVersion ("2.0.12"):
def versiontuple(v):
    #http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
    return tuple(map(int, (v.split("."))))

if versiontuple (aqt.appVersion) < versiontuple ("2.0.12"):
    AddCards.onHistory = onHistory
AddCards.showBrowserOnAddedToday = show_browser_on_added_today
AddCards.setupButtons = wrap(AddCards.setupButtons, mySetupButtons, "after")
addHook("AddCards.onHistory", insert_open_browser_action)