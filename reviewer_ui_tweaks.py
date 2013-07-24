# -*- coding: utf-8 -*-
"""
Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

from anki.hooks import  wrap
from aqt.reviewer import Reviewer

__author__ = 'Steve'

Reviewer._bottomCSS += """
#defease {font-weight: bold; }"""

def	review_title(self):
    #This title is used by AutoHotKey
    self.mw.setWindowTitle(u'AnkiReview')
    #This doesnt really belong here, but it sets focus into the webview
    #after a card has been suspended
    self.web.setFocus()


def change_background_color(self):
#self is reviewer
#$("#f"+i).css("background", cols[i]
    #todo: this relies on /reviewer_track_unseen.py:53 to chnage the colour back
    if self.card.queue == 1:
        self.web.eval('document.body.style.backgroundColor = "#FFE0C0"')
    if self.card.queue == 3:
        self.web.eval('document.body.style.backgroundColor = "#E0FFD0"')


def _defaultEase(self):
    num_buttons = self.mw.col.sched.answerButtons(self.card)
    if (num_buttons == 3) and self.mw.col.sched._cardConf(self.card)['dyn']:
        return 3
    if num_buttons == 4:
        return 3
    else:
        return 2



Reviewer._defaultEase = _defaultEase
Reviewer.show	=	wrap(Reviewer.show,	review_title)
Reviewer._showQuestion = wrap(Reviewer._showQuestion, change_background_color, "after")
