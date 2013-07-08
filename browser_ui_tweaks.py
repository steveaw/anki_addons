# -*- coding: utf-8 -*-
#
# Copyright: Steve AW <steveawa@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QMenu, QCursor
import json
from aqt import mw
from aqt.browser import Browser
from anki.hooks import wrap, addHook, runHook
from anki.find import Finder


def setup_table_changing_row_colors(browser):
    browser.form.tableView.setAlternatingRowColors(False)


def setup_table_changing_row_height(browser):
    browser.form.tableView.verticalHeader().setDefaultSectionSize(17)


# Add some extra search options
##########################################################################

def _findCOrd(self, (val, args)):
    """
    The search string cord:x (x=0,1,2 etc) will show the xth card from a note
    """
    try:
        num = int(val)
    except ValueError:
        return
    return "c.ord = %d" % num

def extend_finder_init(self, col):
    self.search['cord'] = self._findCOrd


# Add a context menu and hook
##########################################################################

def setup_table_with_context_menu(self):
    self.form.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
    self.form.tableView.connect(self.form.tableView, SIGNAL("customContextMenuRequested(QPoint)"),
                                lambda pos: self.onTableViewContextMenu(pos))


def onTableViewContextMenu(self, pos):
    m = QMenu()
    # a = m.addAction('Test')
    # a.connect(a, SIGNAL("triggered()"),
    #      lambda s=self: list([]))
    runHook("Browser.tableViewContextMenuEvent", self, m)
    #m.popup(QCursor.pos())
    m.exec_(QCursor.pos())

# Change editor
##########################################################################
def change_editor_colour_suspended(self, current, previous):
    #Need to do this in the browser as we need access to the card
    if self.singleCard:
        if self.card and self.card.queue == -1:
            cols = []
            for f in self.card.note().fields:
                cols.append("#FFFFB2")
            self.editor.web.eval("setBackgrounds(%s);" % json.dumps(cols))





##########################################################################
Finder._findCOrd = _findCOrd
Finder.__init__ = wrap(Finder.__init__, extend_finder_init, "after")
Browser.setupTable = wrap(Browser.setupTable, setup_table_changing_row_colors, "after")
Browser.setupTable = wrap(Browser.setupTable, setup_table_with_context_menu, "after")
Browser.updateFont = wrap(Browser.updateFont, setup_table_changing_row_height, "after")
Browser.onTableViewContextMenu = onTableViewContextMenu

Browser.onRowChanged = wrap(Browser.onRowChanged, change_editor_colour_suspended, "after")
