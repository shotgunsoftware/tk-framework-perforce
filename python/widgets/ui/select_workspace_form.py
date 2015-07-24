# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_workspace_form.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_SelectWorkspaceForm(object):
    def setupUi(self, SelectWorkspaceForm):
        SelectWorkspaceForm.setObjectName("SelectWorkspaceForm")
        SelectWorkspaceForm.resize(695, 374)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SelectWorkspaceForm)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setContentsMargins(12, 12, 12, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.details_label = QtGui.QLabel(SelectWorkspaceForm)
        self.details_label.setMinimumSize(QtCore.QSize(0, 32))
        self.details_label.setWordWrap(True)
        self.details_label.setObjectName("details_label")
        self.verticalLayout.addWidget(self.details_label)
        self.workspace_list = QtGui.QTableWidget(SelectWorkspaceForm)
        self.workspace_list.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.workspace_list.setTabKeyNavigation(False)
        self.workspace_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.workspace_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.workspace_list.setWordWrap(False)
        self.workspace_list.setCornerButtonEnabled(False)
        self.workspace_list.setObjectName("workspace_list")
        self.workspace_list.setColumnCount(0)
        self.workspace_list.setRowCount(0)
        self.workspace_list.horizontalHeader().setCascadingSectionResizes(False)
        self.workspace_list.horizontalHeader().setSortIndicatorShown(True)
        self.workspace_list.horizontalHeader().setStretchLastSection(True)
        self.workspace_list.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.workspace_list)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.break_line = QtGui.QFrame(SelectWorkspaceForm)
        self.break_line.setFrameShape(QtGui.QFrame.HLine)
        self.break_line.setFrameShadow(QtGui.QFrame.Sunken)
        self.break_line.setObjectName("break_line")
        self.verticalLayout_2.addWidget(self.break_line)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(12, 8, 12, 12)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.cancel_btn = QtGui.QPushButton(SelectWorkspaceForm)
        self.cancel_btn.setMinimumSize(QtCore.QSize(100, 0))
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_4.addWidget(self.cancel_btn)
        self.ok_btn = QtGui.QPushButton(SelectWorkspaceForm)
        self.ok_btn.setMinimumSize(QtCore.QSize(100, 0))
        self.ok_btn.setDefault(True)
        self.ok_btn.setObjectName("ok_btn")
        self.horizontalLayout_4.addWidget(self.ok_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.retranslateUi(SelectWorkspaceForm)
        QtCore.QMetaObject.connectSlotsByName(SelectWorkspaceForm)

    def retranslateUi(self, SelectWorkspaceForm):
        SelectWorkspaceForm.setWindowTitle(QtGui.QApplication.translate("SelectWorkspaceForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.details_label.setText(QtGui.QApplication.translate("SelectWorkspaceForm", "Please choose a Perforce Workspace for user \'\' on server \'\'", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("SelectWorkspaceForm", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("SelectWorkspaceForm", "Ok", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
