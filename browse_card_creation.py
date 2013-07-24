# -*- coding: utf-8 -*-

"""
Browse Card creation.

https://ankiweb.net/shared/info/3466942638

Adds commands to the Reviewer "More" menu to open the browser on the selected card.
The browser is configured to sort based on creation date, and select the card.
Enables the card to be viewed in its  "creation context" ie notes that were created
before/after in the same deck

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Support: Use at your own risk. If you do find a problem please email me
or use one the following forums, however there are certain periods
throughout the year when I will not have time to do any work on
these addons.

Github page:  https://github.com/steveaw/anki_addons
Anki addons: https://groups.google.com/forum/?hl=en#!forum/anki-addons

"""
from PyQt4.QtGui import QApplication
from anki.lang import _
from aqt.reviewer import Reviewer
from aqt.qt import QMenu, QKeySequence, QCursor, SIGNAL
from anki.hooks import wrap, runHook, addHook
from aqt import aqt


def insert_reviewer_more_action(self, m):
    #self is Reviewer
    a = m.addAction('Browse Creation of This Card')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: browse_this_card(s))
    a = m.addAction('Browse Creation of Last Card')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: browse_last_card(s))


def browse_last_card(self):
    #self is Reviewer
    if self.lastCard():
        browse_creation_of_card(self, self.lastCard())
    else:
         QApplication.beep()


def browse_this_card(self):
    #self is Reviewer
    browse_creation_of_card(self, self.card)


def browse_creation_of_card(self, target_card):
    #self is Reviewer
    #Follow pattern in AddCards.editHistory()
    browser = aqt.dialogs.open("Browser", self.mw)
    deck_name = self.card.col.decks.get(target_card.did)['name']
    browser.form.searchEdit.lineEdit().setText("deck:'%s'" % deck_name)
    browser.onSearch()
    if u'noteCrt' in browser.model.activeCols:
        col_index = browser.model.activeCols.index(u'noteCrt')
        browser.onSortChanged(col_index, False)
    browser.focusCid(target_card.id)


#Not enabled in public version
def onSuspendCard_appendId(self, _old, ):
    """This will enable the browsing of a suspended "Last" card"""
    suspended_id = self.card.id
    ret = _old(self)
    self._answeredIds.append(suspended_id)
    return ret

########################################################3
#Only change is to add hook
#The hook is now in the main anki code base
#This is now only used  in versions prior to 2.0.12
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
    runHook("Reviewer.contextMenuEvent", self, m)
    m.exec_(QCursor.pos())

################################################################

#Reviewer.onSuspendCard = wrap(Reviewer.onSuspendCard, onSuspendCard_appendId, "around")
addHook("Reviewer.contextMenuEvent", insert_reviewer_more_action)

# from distutils.version import LooseVersion
# if LooseVersion (aqt.appVersion) < LooseVersion ("2.0.12"):
def versiontuple(v):
    #http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
    return tuple(map(int, (v.split("."))))

if versiontuple (aqt.appVersion) < versiontuple ("2.0.12"):
    Reviewer.showContextMenu = showContextMenu