# -*- coding: utf-8 -*-
"""
Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import time
from PyQt4.QtCore import SIGNAL, SLOT, Qt
from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox
from anki.hooks import addHook
from anki.lang import _
from anki.utils import fmtTimeSpan
from aqt.utils import restoreGeom, saveGeom
from aqt.webview import AnkiWebView

__author__ = 'Steve'


class CardStatShowDialog(object):
    def __init__(self, reviewer, card):
        self.card = card
        self.reviewer = reviewer
        self.mw = reviewer.mw
        self.col = self.mw.col


    #copy and paste from Browser
    #todo: Make this whole class a dialog subclass
    def showCardInfo(self):
        if not self.card:
            return
        info, cs = self._cardInfoData()
        reps = self._revlogData(cs)
        #was d = QDialog(self)
        d = QDialog()
        l = QVBoxLayout()
        l.setMargin(0)
        w = AnkiWebView()
        l.addWidget(w)
        w.stdHtml(info + "<p>" + reps)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        l.addWidget(bb)
        bb.connect(bb, SIGNAL("rejected()"), d, SLOT("reject()"))
        d.setLayout(l)
        d.setWindowModality(Qt.WindowModal)
        d.resize(500, 400)
        restoreGeom(d, "revlog")
        d.exec_()
        saveGeom(d, "revlog")

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
    #no changes made
    def _revlogData(self, cs):
        entries = self.mw.col.db.all(
            "select id/1000.0, ease, ivl, factor, time/1000.0, type "
            "from revlog where cid = ?", self.card.id)
        if not entries:
            return ""
        s = "<table width=100%%><tr><th align=left>%s</th>" % _("Date")
        s += ("<th align=right>%s</th>" * 5) % (
            _("Type"), _("Rating"), _("Interval"), _("Ease"), _("Time"))
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
            if ivl == 0:
                ivl = _("0d")
            elif ivl > 0:
                ivl = fmtTimeSpan(ivl * 86400, short=True)
            else:
                ivl = cs.time(-ivl)
            s += ("<td align=right>%s</td>" * 5) % (
                tstr,
                ease, ivl,
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
    dialog = CardStatShowDialog(self, card)
    dialog.showCardInfo()


def showinfo_this_card(self):
    _showinfo_of_card(self, self.card)


def showinfo_last_card(self):
    if self.lastCard():
        _showinfo_of_card(self, self.lastCard())


def insert_reviewer_more_action(self, m):
    #self is Reviewer
    a = m.addAction('Show Info For This Card')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: showinfo_this_card(s))
    a = m.addAction('Show Info For Last Card')
    a.connect(a, SIGNAL("triggered()"),
              lambda s=self: showinfo_last_card(s))


#hook added in /browse_card_creation.py
addHook("Reviewer.contextMenuEvent", insert_reviewer_more_action)