# -*- coding: utf-8 -*-
"""
Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

"""

from anki.hooks	import wrap, addHook
from aqt.addcards import AddCards
import aqt.editor as theeditor

def after_init(self, mw):
    self.setWindowTitle("AnkiAdd")

rep = """
.field {
  border: 1px solid #aaa; background:#fff; color:#000; padding: 5px;
"""
theeditor._html = theeditor._html.replace (rep , rep + 'padding-left: 15px;')


AddCards.__init__ = wrap(AddCards.__init__, after_init,'after')



