# -*- coding: utf-8 -*-
"""
Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

"""

from anki.hooks	import wrap, addHook
from aqt.addcards import AddCards

def after_init(self, mw):
    self.setWindowTitle("AnkiAdd")


AddCards.__init__ = wrap(AddCards.__init__, after_init,'after')