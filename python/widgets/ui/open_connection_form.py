# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'open_connection_form.ui'
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

class Ui_OpenConnectionForm(object):
    def setupUi(self, OpenConnectionForm):
        if not OpenConnectionForm.objectName():
            OpenConnectionForm.setObjectName(u"OpenConnectionForm")
        OpenConnectionForm.resize(461, 238)
        self.verticalLayout = QVBoxLayout(OpenConnectionForm)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(12, 12, 12, 0)
        self.label_6 = QLabel(OpenConnectionForm)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_2.addWidget(self.label_6)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, -1, 0, -1)
        self.label_8 = QLabel(OpenConnectionForm)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_4.addWidget(self.label_8, 0, 0, 1, 1)

        self.server_label = QLabel(OpenConnectionForm)
        self.server_label.setObjectName(u"server_label")
        self.server_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout_4.addWidget(self.server_label, 0, 1, 1, 1)

        self.label_9 = QLabel(OpenConnectionForm)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_4.addWidget(self.label_9, 1, 0, 1, 1)

        self.user_label = QLabel(OpenConnectionForm)
        self.user_label.setObjectName(u"user_label")
        self.user_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout_4.addWidget(self.user_label, 1, 1, 1, 1)

        self.gridLayout_4.setColumnStretch(1, 1)
        self.gridLayout_4.setColumnMinimumWidth(0, 80)

        self.verticalLayout_2.addLayout(self.gridLayout_4)

        self.verticalSpacer_2 = QSpacerItem(1, 12, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.label_12 = QLabel(OpenConnectionForm)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_2.addWidget(self.label_12)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, -1, 0, -1)
        self.workspace_edit = QLineEdit(OpenConnectionForm)
        self.workspace_edit.setObjectName(u"workspace_edit")

        self.gridLayout_3.addWidget(self.workspace_edit, 0, 1, 1, 1)

        self.label_7 = QLabel(OpenConnectionForm)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_7, 0, 0, 1, 1)

        self.workspace_browse_btn = QPushButton(OpenConnectionForm)
        self.workspace_browse_btn.setObjectName(u"workspace_browse_btn")

        self.gridLayout_3.addWidget(self.workspace_browse_btn, 0, 2, 1, 1)

        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setColumnMinimumWidth(0, 80)

        self.verticalLayout_2.addLayout(self.gridLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout_2.setStretch(5, 1)

        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.break_line = QFrame(OpenConnectionForm)
        self.break_line.setObjectName(u"break_line")
        self.break_line.setFrameShape(QFrame.HLine)
        self.break_line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.break_line)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(12, 8, 12, 12)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.cancel_btn = QPushButton(OpenConnectionForm)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(OpenConnectionForm)
        self.ok_btn.setObjectName(u"ok_btn")
        self.ok_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.ok_btn)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        QWidget.setTabOrder(self.cancel_btn, self.ok_btn)

        self.retranslateUi(OpenConnectionForm)

        self.ok_btn.setDefault(True)

        QMetaObject.connectSlotsByName(OpenConnectionForm)
    # setupUi

    def retranslateUi(self, OpenConnectionForm):
        OpenConnectionForm.setWindowTitle(QCoreApplication.translate("OpenConnectionForm", u"Form", None))
        self.label_6.setText(QCoreApplication.translate("OpenConnectionForm", u"<html><head/><body><p><span style=\" font-size:large;\">Your Perforce connection settings are:</span></p></body></html>", None))
        self.label_8.setText(QCoreApplication.translate("OpenConnectionForm", u"Server:", None))
        self.server_label.setText(QCoreApplication.translate("OpenConnectionForm", u"[server]:[port]", None))
        self.label_9.setText(QCoreApplication.translate("OpenConnectionForm", u"User:", None))
        self.user_label.setText(QCoreApplication.translate("OpenConnectionForm", u"[user]", None))
        self.label_12.setText(QCoreApplication.translate("OpenConnectionForm", u"<html><head/><body><p><span style=\" font-size:large;\">Choose the Workspace to use for this connection:</span></p></body></html>", None))
        self.label_7.setText(QCoreApplication.translate("OpenConnectionForm", u"Workspace:", None))
        self.workspace_browse_btn.setText(QCoreApplication.translate("OpenConnectionForm", u"Browse...", None))
        self.cancel_btn.setText(QCoreApplication.translate("OpenConnectionForm", u"Cancel", None))
        self.ok_btn.setText(QCoreApplication.translate("OpenConnectionForm", u"Connect", None))
    # retranslateUi
