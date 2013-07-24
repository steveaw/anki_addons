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

QUEUE_SIZE = 15


class NoteFieldPreClozeHistory(object):
    def __init__(self):
        object.__init__(self)
        self.queue = [None] * (QUEUE_SIZE)
        self.set_restore_point_To_end()


    def set_restore_point_To_end(self):
        self.restore_point = len(self.queue) - 1

    def store_content(self, content):
        if content == self.queue[self.restore_point]:
            return False
        if content:
            self.queue.append(content)
            self.queue.pop(0)
            self.set_restore_point_To_end()
            return True
        return False

    def store_state(self, editor):
        """
    answer if anything was added to the queue
        """
        content = editor.note.fields[editor.currentField]
        return self.store_content(content)

    def store_state_if_at_end(self, editor):
        if self.restore_point == (len(self.queue) - 1):
            self.store_state(editor)


    def item_stored_undoing(self):
        """
        None indicates end of queue etc
        :return:
        """
        if not self.restore_point:
            return None
        answer = self.queue[self.restore_point]
        self.restore_point -=  1
        return answer

    def item_stored_undoing_add_first(self,editor):
        """
       If we are at the end, take a copy first
        """
        #todo: Always add/insert current state checking first if in queue?
        did_add = False
        #Are we still at the end? If so, add current to the end
        if self.restore_point == (len(self.queue) - 1):
            did_add = self.store_state(editor)
        #Need to move back one
        if did_add:
            self.restore_point -=  1
        if not self.restore_point:
            return None
        answer = self.queue[self.restore_point]
        self.restore_point -=  1
        return answer


    def item_stored_redoing(self):
        self.restore_point +=  1
        if self.restore_point >= QUEUE_SIZE:
            self.set_restore_point_To_end()
            return None
        answer = self.queue[self.restore_point]

        return answer


class NoteFieldEditState(object):
    def __init__(self):
        object.__init__(self)
        self.note_guid = ""
        self.note_unaltered_src = ""
        self.note_src_index = 0

    def store_state(self, editor):
        self.note_src_index = editor.currentField
        self.note_unaltered_src = editor.note.fields[self.note_src_index]
        self.note_guid = editor.note.guid

    def store_state_if_empty(self, editor):
        self.note_src_index = editor.currentField
        if not editor.note.guid == self.note_guid:
            #This is the first useof cloze, replace clip
            self.note_unaltered_src = editor.note.fields[self.note_src_index]
            self.note_guid = editor.note.guid

    def check_and_set_editor_new_note(self, oldNote, add_cards):
        if oldNote:
            if oldNote.guid == self.note_guid:
                #We have a match!
                add_cards.editor.note.fields[self.note_src_index] = self.note_unaltered_src
                add_cards.editor.loadNote()

    def is_state_stored_for(self, note):
        return note.guid == self.note_guid

    def forget_note(self):
        self.note_guid = ""
        self.note_unaltered_src = ""
        self.note_src_index = 0


current_note_state = NoteFieldEditState()
cloze_history_state = NoteFieldPreClozeHistory()


def onCloze_capture_field_before(editor):
    current_note_state.store_state_if_empty(editor)
    cloze_history_state.store_state(editor)


def onReset_around(add_cards, _old, model=None, keep=False):
    oldNote = add_cards.editor.note
    ret = _old(add_cards, model, keep)
    current_note_state.check_and_set_editor_new_note(oldNote, add_cards)
    return ret


def onAddNote_before(self, note):
    if not current_note_state.is_state_stored_for(note):
        # A card has been added since the last note that was stored.
        #   Therefore our stored note is stale ... drop it.
        current_note_state.forget_note()


Editor.onCloze = wrap(Editor.onCloze, onCloze_capture_field_before, "before")
AddCards.onReset = wrap(AddCards.onReset, onReset_around, "around")
AddCards.addNote = wrap(AddCards.addNote, onAddNote_before, "before")
#Not used anymore?
#addHook("aboutToAlterFieldSelection", storeSrcIfFirstAlteration)