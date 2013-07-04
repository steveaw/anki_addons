# -*- coding: utf-8 -*-

"""

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

"""

__author__ = 'Steve'
from aqt.reviewer import Reviewer
from aqt.qt import QMenu, QKeySequence, QCursor, SIGNAL
from anki.hooks import wrap, runHook, addHook
from aqt import aqt

#todo: ask for hook
def showContextMenu(self):
    opts = [
        [_("Mark Note"), "*", self.onMark],
        [_("Bury Note"), "-", self.onBuryNote],
        [_("Suspend Card"), "@", self.onSuspendCard],
        [_("Suspend Note"), "!", self.onSuspend],
        [_("Delete Note"), "Delete", self.onDelete],
        [_("Options"), "O", self.onOptions],
        None,
        [_("Replay Audio"), "R", self.replayAudio],
        [_("Record Own Voice"), "Shift+V", self.onRecordVoice],
        [_("Replay Own Voice"), "V", self.onReplayRecorded],
    ]
    m = QMenu(self.mw)
    for row in opts:
        if not row:
            m.addSeparator()
            continue
        label, scut, func = row
        a = m.addAction(label)
        a.setShortcut(QKeySequence(scut))
        a.connect(a, SIGNAL("triggered()"), func)
    #Only change is the following statement
    runHook("Reviewer.contextMenuEvent",self,m)
    m.exec_(QCursor.pos())

def insert_reviewer_more_action(self,m):
    #self is Reviewer
    a = m.addAction('Browse Creation of This Card')
    a.connect(a, SIGNAL("triggered()"),
         lambda s=self: browse_this_card(s))
    a = m.addAction('Browse Creation of Last Card')
    a.connect(a, SIGNAL("triggered()"),
         lambda s=self: browse_last_card(s))
    a = m.addAction('Inspect')
    a.connect(a, SIGNAL("triggered()"),
         lambda s=self: excuse_for_breakpoint(s))


def browse_last_card(self):
    #self is Reviewer
    if self.lastCard():
        browse_creation_of_card(self,self.lastCard())

def browse_this_card(self):
    #self is Reviewer
    browse_creation_of_card(self,self.card)


def browse_creation_of_card(self,target_card):
    #self is Reviewer
    #Follow pattern in AddCards.editHistory()
    browser = aqt.dialogs.open("Browser", self.mw)
    deck_name = self.card.col.decks.get(target_card.did)['name']
    browser.form.searchEdit.lineEdit().setText("deck:'%s'" % deck_name)
    browser.onSearch()
    if u'noteCrt' in  browser.model.activeCols:
        col_index = browser.model.activeCols.index(u'noteCrt')
        browser.onSortChanged(col_index,False)
    browser.focusCid(target_card.id)

def onSuspendCard_appendId(self, _old, ):
    """This will enable the browsing of a suspended "Last" card"""
    suspended_id = self.card.id
    ret = _old(self)
    self._answeredIds.append(suspended_id)
    return ret

def excuse_for_breakpoint(self):
    self

Reviewer.onSuspendCard = wrap(Reviewer.onSuspendCard, onSuspendCard_appendId, "around")
Reviewer.showContextMenu = showContextMenu
addHook("Reviewer.contextMenuEvent", insert_reviewer_more_action)