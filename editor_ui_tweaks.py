import json
from anki.hooks import wrap
from aqt.editor import Editor

__author__ = 'Steve'


# def check_valid_colour_suspend(self):
#     if self.card and self.card.queue == -1:
#         cols = []
#         for f in self.note.fields:
#             cols.append("#FFFFB2")
#         self.web.eval("setBackgrounds(%s);" % json.dumps(cols))
#
#
# Editor.checkValid=wrap(Editor.checkValid,check_valid_colour_suspend,"after")