# -*- coding: utf-8 -*-
#
# Copyright: Steve AW <steveawa@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QMenu, QCursor, QApplication, QHeaderView
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


def set_search_text_to(self, txt):
    if self.mw.app.keyboardModifiers() & Qt.ControlModifier:
            cur = unicode(self.form.searchEdit.lineEdit().text())
            if cur:
                txt = cur + " " + txt
    self.form.searchEdit.lineEdit().setText(txt)
    self.onSearch()



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


def setColumnSizes(self):
    hh = self.form.tableView.horizontalHeader()
    for i in range(len(self.model.activeCols)):
         hh.setResizeMode(i, QHeaderView.Interactive)
        # if hh.visualIndex(i) == len(self.model.activeCols) - 1:
        #     hh.setResizeMode(i, QHeaderView.Stretch)
        # else:
        #     hh.setResizeMode(i, QHeaderView.Interactive)

def set_column_size_to_default(self):
    for i in range(len(self.model.activeCols)):
         self.form.tableView.setColumnWidth(i,75)

def change_min_section_size(self):
    self.form.tableView.horizontalHeader().setMinimumSectionSize(75)

def onTableViewContextMenu(self, pos):
    m = QMenu()
    a = m.addAction('Copy Selected cid')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: QApplication.clipboard().setText(str(s.selectedCards()[0])))
    a = m.addAction('Copy Selected nid')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: QApplication.clipboard().setText(str(s.selectedNotes()[0])))

    preset_search_menu = m.addMenu("Preset Searches")
    a = preset_search_menu.addAction('Review cards due soon with long interval')
    a.connect(a, SIGNAL("triggered()"),
              lambda b=self: set_search_text_to(b, "prop:due>5 prop:due<7 prop:ivl>=10 is:review"))
    a = preset_search_menu.addAction('Unseen cards')
    a.connect(a, SIGNAL("triggered()"),
              lambda b=self: set_search_text_to(b, "tag:ns*"))

    a = m.addAction('Set Columns to Min Size')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: set_column_size_to_default(s))

    runHook("Browser.tableViewContextMenuEvent", self, m)
    #m.popup(QCursor.pos())
    m.exec_(QCursor.pos())



##########################################################################
Finder._findCOrd = _findCOrd
Finder.__init__ = wrap(Finder.__init__, extend_finder_init, "after")
Browser.setupTable = wrap(Browser.setupTable, setup_table_changing_row_colors, "after")
Browser.setupTable = wrap(Browser.setupTable, setup_table_with_context_menu, "after")
Browser.updateFont = wrap(Browser.updateFont, setup_table_changing_row_height, "after")
Browser.onTableViewContextMenu = onTableViewContextMenu
Browser.setColumnSizes = setColumnSizes
Browser.onRowChanged = wrap(Browser.onRowChanged, change_editor_colour_suspended, "after")
Browser.setupHeaders=wrap(Browser.setupHeaders, change_min_section_size,"after")