# -*- coding: utf-8 -*-
#
# Copyright: Steve AW <steveawa@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
###########################################

from aqt import mw
from aqt.editor import Editor
from aqt.addcards import AddCards
from anki.hooks import wrap, addHook



class NoteFieldEditState(object):
    def __init__(self):
        object.__init__(self)
        self.noteGuid = ""
        self.noteUnalteredSrc = ""
        self.noteSrcIndex = 0

    def store_state(self,editor):
        self.noteSrcIndex = editor.currentField
        self.noteUnalteredSrc = editor.note.fields[self.noteSrcIndex]
        self.noteGuid = editor.note.guid

    def store_state_if_empty(self,editor):
        self.noteSrcIndex = editor.currentField
        if not editor.note.guid == self.noteGuid:
            #This is the first useof cloze, replace clip
            self.noteUnalteredSrc = editor.note.fields[self.noteSrcIndex]
            self.noteGuid = editor.note.guid

    def check_and_set_editor_new_note(self,oldNote,add_cards):
        if oldNote:
            if oldNote.guid == self.noteGuid:
                #We have a match!
                add_cards.editor.note.fields[self.noteSrcIndex] = self.noteUnalteredSrc
                add_cards.editor.loadNote()

    def is_state_stored_for(self, note):
         return note.guid == self.noteGuid

    def forget_note(self):
        self.noteGuid = ""
        self.noteUnalteredSrc = ""
        self.noteSrcIndex = 0



current_note_state = NoteFieldEditState()



def onMyCloze (editor):
	current_note_state.store_state_if_empty(editor)


def onMyReset (add_cards, _old, model=None, keep=False):
	oldNote = add_cards.editor.note
	ret = _old(add_cards,model,keep)
	current_note_state.check_and_set_editor_new_note(oldNote, add_cards)
	return ret

def onMyAddNote(self, note):
	if not current_note_state.is_state_stored_for(note):
		# A card has been added since the last note that was stored.
		#   Therefore our stored note is stale ... drop it.
		current_note_state.forget_note()




Editor.onCloze = wrap(Editor.onCloze, onMyCloze, "before")
AddCards.onReset = wrap(AddCards.onReset, onMyReset, "around")
AddCards.addNote = wrap(AddCards.addNote, onMyAddNote, "before")
#Not used anymore?
#addHook("aboutToAlterFieldSelection", storeSrcIfFirstAlteration)