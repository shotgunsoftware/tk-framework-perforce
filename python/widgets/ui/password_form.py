# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'password_form.ui'
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

class Ui_PasswordForm(object):
    def setupUi(self, PasswordForm):
        if not PasswordForm.objectName():
            PasswordForm.setObjectName(u"PasswordForm")
        PasswordForm.resize(345, 162)
        self.verticalLayout = QVBoxLayout(PasswordForm)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(12, 12, 12, -1)
        self.details_label = QLabel(PasswordForm)
        self.details_label.setObjectName(u"details_label")
        self.details_label.setMinimumSize(QSize(0, 32))
        self.details_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.details_label)

        self.password_edit = QLineEdit(PasswordForm)
        self.password_edit.setObjectName(u"password_edit")
        self.password_edit.setMinimumSize(QSize(0, 22))
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.verticalLayout_2.addWidget(self.password_edit)

        self.invalid_label = QLabel(PasswordForm)
        self.invalid_label.setObjectName(u"invalid_label")
        self.invalid_label.setStyleSheet(u"#invalid_label {\n"
"color: rgb(232,0,0);\n"
"}")
        self.invalid_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.invalid_label)

        self.verticalSpacer_2 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.verticalLayout_2.setStretch(3, 1)

        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.break_line = QFrame(PasswordForm)
        self.break_line.setObjectName(u"break_line")
        self.break_line.setFrameShape(QFrame.HLine)
        self.break_line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.break_line)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(12, 8, 12, 12)
        self.details_btn = QPushButton(PasswordForm)
        self.details_btn.setObjectName(u"details_btn")

        self.horizontalLayout_3.addWidget(self.details_btn)

        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.cancel_btn = QPushButton(PasswordForm)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(90, 0))

        self.horizontalLayout_3.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(PasswordForm)
        self.ok_btn.setObjectName(u"ok_btn")
        self.ok_btn.setMinimumSize(QSize(90, 0))

        self.horizontalLayout_3.addWidget(self.ok_btn)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(PasswordForm)

        self.ok_btn.setDefault(True)

        QMetaObject.connectSlotsByName(PasswordForm)
    # setupUi

    def retranslateUi(self, PasswordForm):
        PasswordForm.setWindowTitle(QCoreApplication.translate("PasswordForm", u"Form", None))
        self.details_label.setText(QCoreApplication.translate("PasswordForm", u"Please enter the password required for user '' to connect to the Perforce server ''", None))
        self.invalid_label.setText(QCoreApplication.translate("PasswordForm", u"Log-in failed: Password Incorrect", None))
        self.details_btn.setText(QCoreApplication.translate("PasswordForm", u"Show Details...", None))
        self.cancel_btn.setText(QCoreApplication.translate("PasswordForm", u"Cancel", None))
        self.ok_btn.setText(QCoreApplication.translate("PasswordForm", u"Connect", None))
    # retranslateUi
