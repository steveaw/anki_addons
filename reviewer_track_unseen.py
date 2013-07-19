# -*- coding: utf-8 -*-
"""
Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""
from PyQt4.QtCore import SIGNAL
from anki.hooks import addHook, wrap
from anki.sched import Scheduler
from aqt.reviewer import Reviewer


__author__ = 'Steve'


def add_unseen_tags_to_selected(self):
    #self is browser
    selected_cids = self.selectedCards()
    #self.mw.progress.start()
    self.mw.checkpoint("Add Unseen Tags")
    self.model.beginReset()
    for cid in selected_cids:
        unseen_card = self.col.getCard(cid)
        unseen_note = unseen_card.note()
        unseen_note.addTag("nsN")
        unseen_note.addTag("ns%s" % unseen_card.ord)
        unseen_note.flush()
    self.model.endReset()
    self.mw.requireReset()
    #self.mw.progress.finish()


def remove_unseen_tags_from_selected(self):
    #self is browser
    #There is a chance this will miss some if card numbers have changed
    selected_cids = self.selectedCards()
    for cid in selected_cids:
        unseen_card = self.col.getCard(cid)
        unseen_note = unseen_card.note()
        # unseen_note.delTag("nsN")
        # unseen_note.delTag("ns%s" % unseen_card.ord)
        # unseen_note.flush()
        self._remove_unseen_tags_for_card_and_note(unseen_card, unseen_note)


def change_background_color(self):
#self is reviewer
#$("#f"+i).css("background", cols[i]
    pot_unseen_card = self.card
    pot_unseen_note = pot_unseen_card.note()
    if pot_unseen_note.hasTag("nsN") or pot_unseen_note.hasTag("ns%s" % pot_unseen_card.ord):
        #We have to remove this, and play nicely with other addons that may fiddle with background
        self.web.eval('document.body.style.backgroundColor = "#DCDCFF"')

def wipe_background_for_nextCard(self):
    #do this early enough so that any addon applying colour changes
    #does it after
    self.web.eval('document.body.style.backgroundColor = "#FFFFFF"')

def _remove_unseen_tags_for_card_and_note(pot_unseen_card, pot_unseen_note):
    if pot_unseen_note.hasTag("nsN") or pot_unseen_note.hasTag("ns%s" % pot_unseen_card.ord):
        pot_unseen_note.delTag("nsN")
        pot_unseen_note.delTag("ns%s" % pot_unseen_card.ord)
        pot_unseen_note.flush()


def _remove_unseen_tags(self):
    pot_unseen_card = self.card
    pot_unseen_note = pot_unseen_card.note()
    _remove_unseen_tags_for_card_and_note(pot_unseen_card, pot_unseen_note)


def answer_card_removing_unseen_tags(self, ease):
    #self is reviewer
    #Keep these guards in place ... not sure why?
    if self.mw.state != "review":
        return
    if self.state != "answer":
        return
    _remove_unseen_tags(self)


def suspend_cards_removing_unseen_tags(self, ids):
    #self is Scheduler
    for cid in ids:
        sus_card = self.col.getCard(cid)
        sus_note = sus_card.note()
        _remove_unseen_tags_for_card_and_note(sus_card, sus_note)


def show_all_unseen_cards(self):
    #self is browser
    self.form.searchEdit.lineEdit().setText("tag:ns*")
    self.onSearch()


def setup_browser_menu(browser):
    unseen_menu = browser.form.menuEdit.addMenu("Unseen Card Tracking")
    a = unseen_menu.addAction('Add Unseen ("ns*") Tags To Selected Cards')
    browser.connect(a, SIGNAL("triggered()"), lambda b=browser: add_unseen_tags_to_selected(b))
    a = unseen_menu.addAction('Remove Unseen ("ns*") Tags From Selected Cards')
    browser.connect(a, SIGNAL("triggered()"), lambda b=browser: remove_unseen_tags_from_selected(b))
    a = unseen_menu.addAction('Show All Unseen Cards')
    browser.connect(a, SIGNAL("triggered()"), lambda b=browser: show_all_unseen_cards(b))



#todo: menu action to set search string to show all
addHook("browser.setupMenus", setup_browser_menu)
Reviewer._answerCard = wrap(Reviewer._answerCard, answer_card_removing_unseen_tags, "before")
Reviewer._showQuestion = wrap(Reviewer._showQuestion, change_background_color, "after")




Reviewer.nextCard = wrap(Reviewer.nextCard, wipe_background_for_nextCard, "before")

#By wrapping this, we cover suspending cards/notes etc
Scheduler.suspendCards = wrap(Scheduler.suspendCards, suspend_cards_removing_unseen_tags, "before")
