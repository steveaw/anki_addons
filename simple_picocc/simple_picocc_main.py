# -*- coding: utf-8 -*-
#Based on the fantastic Image Occlusion addon by  tmbb@campus.ul.pt
#Note this doesn't setup note types etc, so it won't work in a fresh anki install
#svg-edit a fresh install +
#  svg-edit-2.5.1\extensions\ext-picocc.js
#  svg-edit-2.5.1\extensions\picocc-icon.xml

import os
import datetime
import random
import string
import copy
from PyQt4 import QtCore, QtGui, QtWebKit
from aqt import mw, utils, webview
from aqt.qt import *
from anki import hooks
from aqt.utils import showInfo, showWarning
from aqt.utils import saveGeom, restoreGeom
from xml.dom import minidom
from anki.notes import Note
from aqt.utils import tooltip



addons_folder = mw.pm.addonFolder()
svg_edit_dir = os.path.join(addons_folder, 'simple_picocc', 'svg-edit-2.5.1')
svg_edit_path = os.path.join(svg_edit_dir, 'svg-editor.html')

###############################################################################
# Add
###############################################################################
#svg.wv.page().mainFrame().evaluateJavaScript("svgCanvas.svgCanvasToString()")
###############################################################################
class PicOccSVGEditDialog(QDialog):
    def __init__(self, parent=None):
        super(PicOccSVGEditDialog, self).__init__(parent)
        self.web_view_widget = QWebView()
        l = QVBoxLayout()
        l.setMargin(0)
        l.addWidget(self.web_view_widget)
        self.setLayout(l)
        restoreGeom(self, "PicOccSVGEditDialog")

    def initialize_webview_for(self, path, size, ed, kybd):
        #image_path  is fully qualified path + filename
        self.image_path = path
        self.image_size = size
        self.current_editor = ed
        #Keep hold of this so we can pass it to the NoteGenerator instance
        self.kbd_modifiers=kybd

        url = QtCore.QUrl.fromLocalFile(svg_edit_path)
        url.setQueryItems([('initStroke[opacity]', '0'),
                           ('initStroke[width]', '0'),
                           ('initTool', 'rect'),
                           ('extensions', 'ext-picocc.js'),
                           ('initFill[color]', 'FF0000')])

        url.addQueryItem('dimensions', '{0},{1}'.format(self.image_size.width(), self.image_size.height()))
        url.addQueryItem('bkgd_url', QtCore.QUrl.fromLocalFile(self.image_path).toString())
        self.web_view_widget.setUrl(url)
        self.web_view_widget.page().mainFrame().addToJavaScriptWindowObject("pyObj", self)

    def add_note_mask_style(self, svg_contents, using_subclass):
        saveGeom(self, "PicOccSVGEditDialog")
        self.close()
        gen = using_subclass(self.image_path, self.current_editor, self.kbd_modifiers , svg_contents)
        gen.generate_notes()

    @QtCore.pyqtSlot(str)
    def add_notes_separating_masks(self, svg_contents):
        self.add_note_mask_style(svg_contents, PicOccNoteGeneratorSeparate)


    @QtCore.pyqtSlot(str)
    def add_notes_all_masks(self, svg_contents):
        self.add_note_mask_style(svg_contents, PicOccNoteGeneratorHiding)

    @QtCore.pyqtSlot(str)
    def add_notes_progressive_masks(self, svg_contents):
        self.add_note_mask_style(svg_contents, PicOccNoteGeneratorProgressive)

    @QtCore.pyqtSlot(str)
    def add_notes_single_mask(self, svg_contents):
        self.add_note_mask_style(svg_contents, PicOccNoteGeneratorSingle)


class PicOccNoteGenerator(object):
    def __init__(self, path, ed, kbd, svg):
        #image_path  is fully qualified path + filename
        self.image_path = path
        self.current_editor = ed
        self.masks_svg = svg
        self.kbd_modifiers = kbd


    def generate_notes(self):
        masks = self._generate_mask_svgs()
        #todo: if no notes, delete the image?
        for i in range(len(masks)):
            self._save_mask_and_add_note(i, masks[i])
        tooltip(("Cards added: %s" % len(masks) ), period=1000)

    def _generate_mask_svgs(self):
        #Note this gets reimplemented by PicOccNoteGeneratorSingle
        #which returns the original mask unmodofied
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        layer_nodes = self._layer_nodes_from(svg_node)
        #assume all masks are on a single layer
        layer_node = layer_nodes[0]
        mask_node_indexes = []
        for i in range(len(layer_node.childNodes)):
            node = layer_node.childNodes[i]
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != 'title'):
                mask_node_indexes.append(i)
            # mask_node_indexes contains the indexes of the childNodes that are elements
        # assume that all are masks. Different subclasses do diffeent thigns with them
        masks = self._generate_mask_svgs_for(mask_node_indexes)
        return masks

    def _generate_mask_svgs_for(self, mask_node_indexes):
        masks = [self._create_mask(node_index, mask_node_indexes) for node_index in mask_node_indexes]
        return masks

    def _create_mask(self, mask_node_index, all_mask_node_indexes):
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        layer_nodes = self._layer_nodes_from(svg_node)
        layer_node = layer_nodes[0]
        #This methods get implemented different by subclasses
        self._create_mask_at_layernode(mask_node_index, all_mask_node_indexes, layer_node)
        return svg_node.toxml()

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        raise NotImplementedError

    def _layer_nodes_from(self, svg_node):
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_nodes = [node for node in svg_node.childNodes if node.nodeType == node.ELEMENT_NODE]
        assert (len(layer_nodes) == 1)
        assert (layer_nodes[0].nodeName == 'g')
        return layer_nodes

    def _save_mask(self, mask, note_number):
        mask_path = self.image_path + ('%s.svg' % note_number)
        mask_file = open(mask_path, 'w')
        mask_file.write(mask)
        mask_file.close()
        return mask_path

    def _save_mask_and_add_note(self, note_number, mask):
        mask_path = self._save_mask(mask, note_number)
        editor_note = self.current_editor.note
        #see anki.collection._Collection#_newCard
        model = mw.col.models.byName('PicOcc')
        #Have to do this as not corrent if first card
        # editor_note.model()['did']
        did = self.current_editor.parentWindow.deckChooser.selectedId()
        model['did'] = did

        def field_content(field_name):
            return editor_note[field_name] if field_name in editor_note else u''

        new_note = Note(mw.col, model)

        def fname2img(path):
            return '<img src="%s" />' % os.path.split(path)[1]

        extra_field = field_content(u'Extra') if self.kbd_modifiers["ctrl"] else u''
        intro_field = editor_note.fields[0] if self.kbd_modifiers["shift"] else u''
        new_note.fields = [('%s' % new_note.id), fname2img(self.image_path), extra_field,
                           field_content(u'Context'), intro_field, field_content(u'RefLink'),
                           fname2img(mask_path)]
        new_note.tags = copy.copy(editor_note.tags)
        mw.col.addNote(new_note)


class PicOccNoteGeneratorSeparate(PicOccNoteGenerator):
    """Each top level element of the layer becomes a separate mask"""

    def __init__(self, path, ed, kbd, svg):
        PicOccNoteGenerator.__init__(self, path, ed, kbd, svg)

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        #Delete all child nodes except for mask_node_index
        for i in reversed(all_mask_node_indexes):
            if not i == mask_node_index:
                layer_node.removeChild(layer_node.childNodes[i])


class PicOccNoteGeneratorHiding(PicOccNoteGenerator):
    """Each top level element of the layer becomes a separate mask
    + the other elements are hidden"""

    def __init__(self, path, ed, kbd, svg):
        PicOccNoteGenerator.__init__(self, path, ed, kbd, svg)

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        def modify_fill_recursively(node):
            if (node.nodeType == node.ELEMENT_NODE):
                if node.hasAttribute("fill"):
                    node.setAttribute("fill", "#aaffff")
                map(modify_fill_recursively, node.childNodes)

        for i in all_mask_node_indexes:
            if not i == mask_node_index:
                modify_fill_recursively(layer_node.childNodes[i])


class PicOccNoteGeneratorProgressive(PicOccNoteGenerator):
    def __init__(self, path, ed, kbd, svg):
        PicOccNoteGenerator.__init__(self, path, ed, kbd, svg)

    def _create_mask_at_layernode(self, mask_node_index, all_mask_node_indexes, layer_node):
        showWarning("Not yet implemented")
        #todo: do this (when needed)


class PicOccNoteGeneratorSingle(PicOccNoteGenerator):
    def __init__(self, path, ed, kbd, svg):
        PicOccNoteGenerator.__init__(self, path, ed, kbd, svg)

    def _generate_mask_svgs(self):
        return [self.masks_svg]


def show_picocc_dialog(ed):
    #Shift down => Copy editor's note's first field into header field
    #Ctrl down => Copy Extra field across
    modifiers = ed.mw.app.queryKeyboardModifiers()
    # & would just return the same modifier? I think it is broken
    shift_and_click = modifiers == (Qt.ShiftModifier | Qt.ControlModifier)
    kbd_modifiers = {"shift": shift_and_click or (modifiers == Qt.ShiftModifier)
        , "ctrl": shift_and_click or (modifiers == Qt.ControlModifier)
        , "alt": (modifiers == Qt.AltModifier)}

    clip = QApplication.clipboard()
    if clip.mimeData().hasImage():
        #Makes things easier to save it directly into media folder"
        image = clip.image()
        image_size = image.size()
        mediadir = mw.col.media.dir()
        random_tag = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
        unique_fn = "picocc_%s_%s.png" % (datetime.datetime.now().strftime("%y%m%d_%H%M%S"), random_tag)
        image_path = os.path.join(mediadir, unique_fn)
        image.save(image_path)
        dialog = PicOccSVGEditDialog(ed.parentWindow)
        dialog.initialize_webview_for(image_path, image_size, ed, kbd_modifiers)
        #http://stackoverflow.com/questions/8772595/how-to-check-if-a-key-modifier-is-pressed-shift-ctrl-alt

        dialog.show()
        dialog.exec_()


def add_picocc_button(ed):
    ed._addButton("picocc", lambda o=ed: show_picocc_dialog(o),
                  size=False, text="Pic Occ", canDisable=False, tip="Shift=Add Intro from first field, Ctrl=Copy Extra")


hooks.addHook('setupEditorButtons', add_picocc_button)


