# -*- coding: utf-8 -*-
"""
Show Card Info dialog for current and last card.

This differs from the Card Info During Review addon in that it
also shows the review log table (as does the Browser "info" command)

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Support: Use at your own risk. If you do find a problem please email me
or use one the following forums, however there are certain periods
throughout the year when I will not have time to do any work on
these addons.

Github page:  https://github.com/steveaw/anki_addons
Anki addons: https://groups.google.com/forum/?hl=en#!forum/anki-addons
"""

import time
from PyQt4.QtCore import SIGNAL, SLOT, Qt
from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox, QCursor, QKeySequence, QMenu, QApplication
import datetime
from anki.hooks import addHook, runHook
from anki.lang import _
from anki.utils import fmtTimeSpan
import aqt
from aqt.reviewer import Reviewer
from aqt.utils import restoreGeom, saveGeom
from aqt.webview import AnkiWebView

__author__ = 'Steve'


class CardStatShowDialog(QDialog):
    def __init__(self, reviewer, card, parent=None):
        QDialog.__init__(self, parent=None)
        self.card = card
        self.reviewer = reviewer
        self.mw = reviewer.mw
        self.col = self.mw.col
        info, cs = self._cardInfoData()
        reps = self._revlogData(cs)
        l = QVBoxLayout()
        l.setMargin(0)
        w = AnkiWebView()
        l.addWidget(w)
        w.stdHtml(info + "<p>" + reps)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        l.addWidget(bb)
        bb.connect(bb, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.setLayout(l)
        self.setWindowModality(Qt.WindowModal)
        self.resize(500, 400)
        restoreGeom(self, "CardStatShowDialog")


    #copy and paste from Browser
    #no changes made
    #todo: Ask for this and _revlogData to be extracted to CardStats?
    def _cardInfoData(self):
        from anki.stats import CardStats

        cs = CardStats(self.col, self.card)
        rep = cs.report()
        m = self.card.model()
        rep = """
    <div style='width: 400px; margin: 0 auto 0;
    border: 1px solid #000; padding: 3px; '>%s</div>""" % rep
        return rep, cs

    #copy and paste from Browser
    #Added IntDate column
    def _revlogData(self, cs):
        entries = self.mw.col.db.all(
            "select id/1000.0, ease, ivl, factor, time/1000.0, type "
            "from revlog where cid = ?", self.card.id)
        if not entries:
            return ""
        s = "<table width=100%%><tr><th align=left>%s</th>" % _("Date")
        s += ("<th align=right>%s</th>" * 6) % (
            _("Type"), _("Rating"), _("Interval"), "IntDate", _("Ease"), _("Time"))
        cnt = 0
        for (date, ease, ivl, factor, taken, type) in reversed(entries):
            cnt += 1
            s += "<tr><td>%s</td>" % time.strftime(_("<b>%Y-%m-%d</b> @ %H:%M"),
                                                   time.localtime(date))
            tstr = [_("Learn"), _("Review"), _("Relearn"), _("Filtered"),
                    _("Resched")][type]
            import anki.stats as st

            fmt = "<span style='color:%s'>%s</span>"
            if type == 0:
                tstr = fmt % (st.colLearn, tstr)
            elif type == 1:
                tstr = fmt % (st.colMature, tstr)
            elif type == 2:
                tstr = fmt % (st.colRelearn, tstr)
            elif type == 3:
                tstr = fmt % (st.colCram, tstr)
            else:
                tstr = fmt % ("#000", tstr)
            if ease == 1:
                ease = fmt % (st.colRelearn, ease)
                ####################
            int_due = "na"
            if ivl > 0:
                int_due_date = time.localtime(date + (ivl * 24 * 60 * 60))
                int_due = time.strftime(_("%Y-%m-%d"), int_due_date)
                ####################
            if ivl == 0:
                ivl = _("0d")
            elif ivl > 0:
                ivl = fmtTimeSpan(ivl * 86400, short=True)
            else:
                ivl = cs.time(-ivl)

            s += ("<td align=right>%s</td>" * 6) % (
                tstr,
                ease, ivl,
                int_due
                ,
                "%d%%" % (factor / 10) if factor else "",
                cs.time(taken)) + "</tr>"
        s += "</table>"
        if cnt < self.card.reps:
            s += _("""\
Note: Some of the history is missing. For more information, \
please see the browser documentation.""")
        return s


def _showinfo_of_card(self, card):
    #self is reviewer
    if card:
        dialog = CardStatShowDialog(self, card)
        dialog.exec_()
        saveGeom(dialog, "CardStatShowDialog")


def showinfo_this_card(self):
    _showinfo_of_card(self, self.card)


def showinfo_last_card(self):
    if self.lastCard():
        _showinfo_of_card(self, self.lastCard())
    else:
         QApplication.beep()


def insert_reviewer_more_action(self, m):
    #self is Reviewer
    a = m.addAction('Show Info For This Card')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: showinfo_this_card(s))
    a = m.addAction('Show Info For Last Card')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: showinfo_last_card(s))

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


# from distutils.version import LooseVersion
# if LooseVersion (aqt.appVersion) < LooseVersion ("2.0.12"):
def versiontuple(v):
    #http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
    return tuple(map(int, (v.split("."))))

if versiontuple (aqt.appVersion) < versiontuple ("2.0.12"):
    Reviewer.showContextMenu = showContextMenu
addHook("Reviewer.contextMenuEvent", insert_reviewer_more_action)