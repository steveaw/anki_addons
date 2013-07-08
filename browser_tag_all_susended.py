# -*- coding: utf-8 -*-



import sys, csv, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from aqt.utils import getOnlyText, showWarning, showInfo
from aqt import mw


def tag_notes_with_all_cards_unsuspended(browser):
    browser.mw.checkpoint("Add AllSuspended Tags")
    browser.model.beginReset()
    for nid in browser.selectedNotes():
        note = mw.col.getNote(nid)
        cards = note.cards()
        if all(card.queue == -1 for card in cards):
            note.addTag(u'AllSuspended')
            note.flush()
    browser.model.endReset()
    browser.mw.requireReset()


def setupMenu(browser):
    a = QAction("Tag Notes With All Cards Suspended", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda b=browser: tag_notes_with_all_cards_unsuspended(b))
    browser.form.menuEdit.addAction(a)


addHook("browser.setupMenus", setupMenu)