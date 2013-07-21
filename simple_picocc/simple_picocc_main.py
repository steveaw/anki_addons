# -*- coding: utf-8 -*-
"""
Simple Picture Occlusion
Based on the fantastic Image Occlusion addon by  tmbb@campus.ul.pt

I started work on this when imgocc2 was broken, but since then Tiago has released a fix
so there is no need for this addon to be made shared/public.

Notes (and difference to image occlusion 2)
 -This doesn't setup note types etc, so it won't work in a fresh anki install.
    I have included a sample deck that includes the model (not tested)
 -svg-edit a fresh install. No changes or files are added to /svg-edit-2.5.1
 -The original image is loaded as a background image, so it can not be edited.
    This simplifies the code greatly as the addon needs only to manipulate
    svg xml, not bitmaps
 -The dialog is opened modally to add cards, and uses the AddCards dialog's
    current settings for deck/tags etc. In addition, it is optimized for my
    work flow and will copy across other fields I commonly use.
 -Instead of toolbar buttons to add the notes, this uses standard dialog buttons

"""
import os
import datetime
import random
import string
import copy
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QDialog, QVBoxLayout, QApplication
from PyQt4.QtWebKit import QWebView
import svg_edit_dialog
from PyQt4 import QtCore, QtGui, QtWebKit
from aqt import mw, utils, webview
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
#svg.wv.page().mainFrame().evaluateJavaScript("svgCanvas.svgCanvasToString()")
# "C:\Python27\python.exe" "C:\Python27\Lib\site-packages\PyQt4\uic\pyuic.py" svg_edit_dialog.ui > svg_edit_dialog.py
###############################################################################
class PicOccSVGEditDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=None)
        self.ui = svg_edit_dialog.Ui_SimplePicOccQDialog()
        self.ui.setupUi(self)
        self.web_view_widget = QWebView()
        l = QVBoxLayout()
        l.setMargin(0)
        l.addWidget(self.web_view_widget)
        # self.setLayout(l)
        self.ui.centralWidget.setLayout(l)
        self.connect(self.ui.singleCardButton, SIGNAL("clicked()"), self.add_notes_single_mask)
        self.connect(self.ui.multiButton, SIGNAL("clicked()"), self.add_notes_multiple_masks)
        self.connect(self.ui.multiMaskedButton, SIGNAL("clicked()"), self.add_notes_multiple_hiding_masks)
        restoreGeom(self, "PicOccSVGEditDialog")

    def initialize_webview_for(self, path, size, ed, kybd):
        #image_path  is fully qualified path + filename
        self.image_path = path
        self.image_size = size
        self.current_editor = ed
        #Keep hold of this so we can pass it to the NoteGenerator instance
        self.kbd_modifiers = kybd

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

    def add_note_mask_style(self, using_subclass):
        svg_contents = self.web_view_widget.page().mainFrame().evaluateJavaScript("svgCanvas.svgCanvasToString()")
        gen = using_subclass(self.image_path, self.current_editor, self.kbd_modifiers, svg_contents)
        gen.generate_notes()
        saveGeom(self, "PicOccSVGEditDialog")
        self.accept()


    def add_notes_multiple_masks(self):
        self.add_note_mask_style(PicOccNoteGeneratorSeparate)


    def add_notes_multiple_hiding_masks(self):
        self.add_note_mask_style(PicOccNoteGeneratorHiding)


    def add_notes_single_mask(self):
        self.add_note_mask_style(PicOccNoteGeneratorSingle)


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
        tooltip(("Cards added: %s" % len(masks) ), period=1500, parent=self.current_editor.parentWindow)

    def _generate_mask_svgs(self):
        #Note this gets reimplemented by PicOccNoteGeneratorSingle
        #which returns the original mask unmodofied
        mask_doc = minidom.parseString(self.masks_svg)
        svg_node = mask_doc.documentElement
        layer_nodes = self._layer_nodes_from(svg_node)
        #assume all masks are on a single layer
        layer_node = layer_nodes[0]
        mask_node_indexes = []
        #todo: iter
        for i in range(len(layer_node.childNodes)):
            node = layer_node.childNodes[i]
            if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName != 'title'):
                mask_node_indexes.append(i)
                # mask_node_indexes contains the indexes of the childNodes that are elements
            # assume that all are masks. Different subclasses do different things with them
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
        #This is all highly specific to my own workflow/note models etc
        #but it should not break
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


