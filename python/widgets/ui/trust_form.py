# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trust_form.ui'
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


class Ui_TrustForm(object):
    def setupUi(self, TrustForm):
        if not TrustForm.objectName():
            TrustForm.setObjectName(u"TrustForm")
        TrustForm.resize(500, 178)
        self.verticalLayout_3 = QVBoxLayout(TrustForm)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(12, 12, 12, 8)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.warning_label = QLabel(TrustForm)
        self.warning_label.setObjectName(u"warning_label")
        self.warning_label.setMinimumSize(QSize(0, 0))
        self.warning_label.setMaximumSize(QSize(64, 64))

        self.verticalLayout_2.addWidget(self.warning_label)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(-1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.msg_label = QLabel(TrustForm)
        self.msg_label.setObjectName(u"msg_label")
        self.msg_label.setWordWrap(True)
        self.msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.msg_label)

        self.trust_cb = QCheckBox(TrustForm)
        self.trust_cb.setObjectName(u"trust_cb")

        self.verticalLayout.addWidget(self.trust_cb)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.break_line = QFrame(TrustForm)
        self.break_line.setObjectName(u"break_line")
        self.break_line.setFrameShape(QFrame.HLine)
        self.break_line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.break_line)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(12, 8, 12, 12)
        self.details_btn = QPushButton(TrustForm)
        self.details_btn.setObjectName(u"details_btn")

        self.horizontalLayout_3.addWidget(self.details_btn)

        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.cancel_btn = QPushButton(TrustForm)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(90, 0))

        self.horizontalLayout_3.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(TrustForm)
        self.ok_btn.setObjectName(u"ok_btn")
        self.ok_btn.setMinimumSize(QSize(90, 0))

        self.horizontalLayout_3.addWidget(self.ok_btn)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.verticalLayout_3.setStretch(1, 1)

        self.retranslateUi(TrustForm)

        self.ok_btn.setDefault(True)

        QMetaObject.connectSlotsByName(TrustForm)
    # setupUi

    def retranslateUi(self, TrustForm):
        TrustForm.setWindowTitle(QCoreApplication.translate("TrustForm", u"Form", None))
        self.warning_label.setText("")
        self.msg_label.setText(QCoreApplication.translate("TrustForm", u"<html><head/><body><p><span style=\" font-weight:600;\">The authenticity of the server &lt;server&gt; can't be established.</span></p><p>The fingerprint of the public key sent by the server is:</p><p>&lt;fingerprint&gt;</p></body></html>", None))
        self.trust_cb.setText(QCoreApplication.translate("TrustForm", u"Trust this fingerprint for future connections to this server?", None))
        self.details_btn.setText(QCoreApplication.translate("TrustForm", u"Show Details...", None))
        self.cancel_btn.setText(QCoreApplication.translate("TrustForm", u"Cancel", None))
        self.ok_btn.setText(QCoreApplication.translate("TrustForm", u"Connect", None))
    # retranslateUi
