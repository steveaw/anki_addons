# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'svg_edit_dialog.ui'
#
# Created: Mon Jul 22 07:08:17 2013
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SimplePicOccQDialog(object):
    def setupUi(self, SimplePicOccQDialog):
        SimplePicOccQDialog.setObjectName(_fromUtf8("SimplePicOccQDialog"))
        SimplePicOccQDialog.resize(496, 398)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SimplePicOccQDialog.sizePolicy().hasHeightForWidth())
        SimplePicOccQDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(SimplePicOccQDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.centralWidget = QtGui.QWidget(SimplePicOccQDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.setMinimumSize(QtCore.QSize(400, 100))
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout.addWidget(self.centralWidget, 0, 0, 1, 1)
        self.widget_2 = QtGui.QWidget(SimplePicOccQDialog)
        self.widget_2.setMinimumSize(QtCore.QSize(0, 40))
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.singleCardButton = QtGui.QPushButton(self.widget_2)
        self.singleCardButton.setDefault(True)
        self.singleCardButton.setObjectName(_fromUtf8("singleCardButton"))
        self.horizontalLayout.addWidget(self.singleCardButton)
        self.multiButton = QtGui.QPushButton(self.widget_2)
        self.multiButton.setObjectName(_fromUtf8("multiButton"))
        self.horizontalLayout.addWidget(self.multiButton)
        self.multiMaskedButton = QtGui.QPushButton(self.widget_2)
        self.multiMaskedButton.setObjectName(_fromUtf8("multiMaskedButton"))
        self.horizontalLayout.addWidget(self.multiMaskedButton)
        self.cancelButton = QtGui.QPushButton(self.widget_2)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)

        self.retranslateUi(SimplePicOccQDialog)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SimplePicOccQDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SimplePicOccQDialog)

    def retranslateUi(self, SimplePicOccQDialog):
        SimplePicOccQDialog.setWindowTitle(_translate("SimplePicOccQDialog", "Simple PicOcc Dialog", None))
        self.singleCardButton.setText(_translate("SimplePicOccQDialog", "Add Single Card", None))
        self.multiButton.setText(_translate("SimplePicOccQDialog", "Add Multi Cards", None))
        self.multiMaskedButton.setText(_translate("SimplePicOccQDialog", "Add MultiMasked Cards", None))
        self.cancelButton.setText(_translate("SimplePicOccQDialog", "Cancel", None))

