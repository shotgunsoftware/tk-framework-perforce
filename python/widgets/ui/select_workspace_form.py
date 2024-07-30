# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_workspace_form.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from tank.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from tank.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from  . import resources_rc

class Ui_SelectWorkspaceForm(object):
    def setupUi(self, SelectWorkspaceForm):
        if not SelectWorkspaceForm.objectName():
            SelectWorkspaceForm.setObjectName(u"SelectWorkspaceForm")
        SelectWorkspaceForm.resize(695, 374)
        self.verticalLayout_2 = QVBoxLayout(SelectWorkspaceForm)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, 12, 12, -1)
        self.details_label = QLabel(SelectWorkspaceForm)
        self.details_label.setObjectName(u"details_label")
        self.details_label.setMinimumSize(QSize(0, 32))
        self.details_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.details_label)

        self.workspace_list = QTableWidget(SelectWorkspaceForm)
        self.workspace_list.setObjectName(u"workspace_list")
        self.workspace_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.workspace_list.setTabKeyNavigation(False)
        self.workspace_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.workspace_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.workspace_list.setWordWrap(False)
        self.workspace_list.setCornerButtonEnabled(False)
        self.workspace_list.horizontalHeader().setCascadingSectionResizes(False)
        self.workspace_list.horizontalHeader().setProperty("showSortIndicator", True)
        self.workspace_list.horizontalHeader().setStretchLastSection(True)
        self.workspace_list.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.workspace_list)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.break_line = QFrame(SelectWorkspaceForm)
        self.break_line.setObjectName(u"break_line")
        self.break_line.setFrameShape(QFrame.HLine)
        self.break_line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.break_line)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(12, 8, 12, 12)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.cancel_btn = QPushButton(SelectWorkspaceForm)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_4.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(SelectWorkspaceForm)
        self.ok_btn.setObjectName(u"ok_btn")
        self.ok_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_4.addWidget(self.ok_btn)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.retranslateUi(SelectWorkspaceForm)

        self.ok_btn.setDefault(True)

        QMetaObject.connectSlotsByName(SelectWorkspaceForm)
    # setupUi

    def retranslateUi(self, SelectWorkspaceForm):
        SelectWorkspaceForm.setWindowTitle(QCoreApplication.translate("SelectWorkspaceForm", u"Form", None))
        self.details_label.setText(QCoreApplication.translate("SelectWorkspaceForm", u"Please choose a Perforce Workspace for user '' on server ''", None))
        self.cancel_btn.setText(QCoreApplication.translate("SelectWorkspaceForm", u"Cancel", None))
        self.ok_btn.setText(QCoreApplication.translate("SelectWorkspaceForm", u"Ok", None))
    # retranslateUi
