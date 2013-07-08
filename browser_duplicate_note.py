# -*- coding: utf-8 -*-
#
# Copyright: Steve AW <steveawa@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

import copy
from anki.hooks import runHook, addHook, wrap
from anki.notes import Note
from aqt import mw
from PyQt4.QtCore import SIGNAL

__author__ = 'Steve'




def duplicate_selected_note(browser):
    assert(len(browser.selectedNotes()) == 1)
    base_note = browser.card.note()
    base_did = browser.card.did
    new_note = Note(mw.col, base_note.model())
    #self.id = timestampID(col.db, "notes")
    t = base_note.id + 1
    while mw.col.db.scalar("select id from %s where id = ?" % "notes", t):
        t += 1
    new_note.id = t
    #No change needed: self.guid = guid64()
    #No change needed: self._model = model
    #No change needed: self.mid = model['id']
    new_note.tags = copy.copy(base_note.tags)  #self.tags = []
    new_note.fields = copy.copy(base_note.fields) #self.fields = [""] * len(self._model['flds'])
    new_note.flags = base_note.flags #self.flags = 0
    new_note.data = base_note.data #self.data = ""
    #No change needed: self._fmap = self.col.models.fieldMap(self._model)
    #No change needed: self.scm = self.col.scm

    new_note.addTag(u'Copied')
    browser.model.beginReset()
    #The cards will be added to the deck set into the current template.
    #Changing the template's deck would be unexpected,
    #   so change the decks manually
    cards = mw.col.addNote(new_note)
    for card in new_note.cards():
        if card.did != base_did:
            card.did = base_did
            card.flush()

    browser.model.endReset()


def insert_browser_toolbar_html(self,m):
    a = m.addAction('Duplicate Note')
    a.connect(a, SIGNAL("triggered()"),
         lambda s=self: duplicate_selected_note(s))

#requires /browser_ui_tweaks.py
addHook("Browser.tableViewContextMenuEvent", insert_browser_toolbar_html)
