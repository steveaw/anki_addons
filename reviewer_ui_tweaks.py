# -*- coding: utf-8 -*-
"""
Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

from anki.hooks import  wrap
from aqt.reviewer import Reviewer

__author__ = 'Steve'


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


Reviewer.show	=	wrap(Reviewer.show,	review_title)
Reviewer._showQuestion = wrap(Reviewer._showQuestion, change_background_color, "after")
