# -*- coding: utf-8 -*-
#
# Copyright: Steve AW <steveawa@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from aqt import mw
from aqt.browser import Browser
from anki.hooks import wrap
from anki.find import Finder


def mySetupTable(browser):
    browser.form.tableView.setAlternatingRowColors(False)


def myUpdateFont(browser):
    browser.form.tableView.verticalHeader().setDefaultSectionSize(17)


# The search string cord:0 will show the first card from a note
##########################################################################

def _findCOrd(self, (val, args)):
    try:
        num = int(val)
    except ValueError:
        return
    return "c.ord = %d" % num

def extend_finder_init(self,col ):
    self.search['cord'] = self._findCOrd

Finder._findCOrd = _findCOrd
Finder.__init__ = wrap(Finder.__init__ , extend_finder_init, "after")
Browser.setupTable = wrap(Browser.setupTable, mySetupTable, "after")
Browser.updateFont = wrap(Browser.updateFont, myUpdateFont, "after")