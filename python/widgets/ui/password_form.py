# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'password_form.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_PasswordForm(object):
    def setupUi(self, PasswordForm):
        PasswordForm.setObjectName("PasswordForm")
        PasswordForm.resize(381, 162)
        self.verticalLayout = QtGui.QVBoxLayout(PasswordForm)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setContentsMargins(12, 12, 12, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.details_label = QtGui.QLabel(PasswordForm)
        self.details_label.setMinimumSize(QtCore.QSize(0, 32))
        self.details_label.setWordWrap(True)
        self.details_label.setObjectName("details_label")
        self.verticalLayout_2.addWidget(self.details_label)
        self.password_edit = QtGui.QLineEdit(PasswordForm)
        self.password_edit.setMinimumSize(QtCore.QSize(0, 22))
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_edit.setObjectName("password_edit")
        self.verticalLayout_2.addWidget(self.password_edit)
        self.invalid_label = QtGui.QLabel(PasswordForm)
        self.invalid_label.setStyleSheet("#invalid_label {\n"
"color: rgb(232,0,0);\n"
"}")
        self.invalid_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.invalid_label.setObjectName("invalid_label")
        self.verticalLayout_2.addWidget(self.invalid_label)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.setStretch(3, 1)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.break_line = QtGui.QFrame(PasswordForm)
        self.break_line.setFrameShape(QtGui.QFrame.HLine)
        self.break_line.setFrameShadow(QtGui.QFrame.Sunken)
        self.break_line.setObjectName("break_line")
        self.verticalLayout.addWidget(self.break_line)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(12, 8, 12, 12)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.details_btn = QtGui.QPushButton(PasswordForm)
        self.details_btn.setObjectName("details_btn")
        self.horizontalLayout_3.addWidget(self.details_btn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.cancel_btn = QtGui.QPushButton(PasswordForm)
        self.cancel_btn.setMinimumSize(QtCore.QSize(90, 0))
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_3.addWidget(self.cancel_btn)
        self.ok_btn = QtGui.QPushButton(PasswordForm)
        self.ok_btn.setMinimumSize(QtCore.QSize(90, 0))
        self.ok_btn.setDefault(True)
        self.ok_btn.setObjectName("ok_btn")
        self.horizontalLayout_3.addWidget(self.ok_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(PasswordForm)
        QtCore.QMetaObject.connectSlotsByName(PasswordForm)

    def retranslateUi(self, PasswordForm):
        PasswordForm.setWindowTitle(QtGui.QApplication.translate("PasswordForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.details_label.setText(QtGui.QApplication.translate("PasswordForm", "Please enter the password required for user \'\' to connect to the Perforce server \'\'", None, QtGui.QApplication.UnicodeUTF8))
        self.invalid_label.setText(QtGui.QApplication.translate("PasswordForm", "Log-in failed: Password Incorrect", None, QtGui.QApplication.UnicodeUTF8))
        self.details_btn.setText(QtGui.QApplication.translate("PasswordForm", "Show Details...", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("PasswordForm", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("PasswordForm", "Ok", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
