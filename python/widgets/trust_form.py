# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.trust_form import Ui_TrustForm
    
class TrustForm(QtGui.QWidget):
    """
    Dialog used to confirm with the user that the SSL fingerprint returned by the server is valid
    """
    @property
    def exit_code(self):
        # expose the exit code in an sgtk friendly way
        return self._exit_code

    @property
    def hide_tk_title_bar(self):
        # disable the sgtk dialog title bar
        return True

    # exit code returned when the 'show details' button is pressed
    SHOW_DETAILS = 2

    def __init__(self, server, fingerprint, fingerprint_changed, show_details_btn=False, parent=None):
        """
        Construction

        :param server:              The Perforce server we are trying to connect to
        :param fingerprint:         The SSL fingerprint returned for the server
        :param fingerprint_changed: True if the fingerprint differs from the one last used to connect to
                                    the server, False if there is no previously known fingerprint.  The
                                    fingerprint changing unexpectedly from a known good version is potentially 
                                    very bad as it could mean there is a security breach.
        :param show_details_btn:    True if the 'Show Details...' button should be visible or not
        :param parent:              The parent QWidget this form should be parented to.
        """
        QtGui.QWidget.__init__(self, parent)

        self._exit_code = QtGui.QDialog.Rejected

        # setup ui
        self._ui = Ui_TrustForm()
        self._ui.setupUi(self)

        self._ui.details_btn.setVisible(show_details_btn)

        self._ui.cancel_btn.clicked.connect(self._on_cancel)
        self._ui.ok_btn.clicked.connect(self._on_ok)
        self._ui.details_btn.clicked.connect(self._on_show_details)

        # if we have an icon then set up the warning icon:
        warning_icon = self._ui.warning_label.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning)
        if warning_icon:
            warning_pm = warning_icon.pixmap(64, 64)
            if warning_pm:
                self._ui.warning_label.setPixmap(warning_pm)
            else:
                self._ui.warning_label.hide()

        # ok is only enabled if 'trust' checkbox is checked:
        self._ui.ok_btn.setEnabled(False)
        self._ui.trust_cb.stateChanged.connect(self._ui.ok_btn.setEnabled)

        # update the message - the wording here largely matches the wording from the P4V dialog in the
        # two scenarios
        msg = ""
        if fingerprint_changed:
            # the serious one
            msg = ("<b><span style=\"color:rgb(226,146,0)\">WARNING: It is possible that someone is intercepting "
                   "your Perforce connection</span></b><br>"
                   "<br>"
                   "<b>The fingerprint sent by the Perforce server (%s) does not match the fingerprint you previously "
                   "trusted.</b><br>"
                   "<br>"
                   "The fingerprint of the public key sent by the server is:<br>"
                   "<br>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;%s"
                   % (server, fingerprint))
        else:
            # the less serious one!
            msg = ("<b>The authenticity of the Perforce server (%s) can't be established.</b><br>"
                   "<br>"
                   "The fingerprint of the public key sent by the server is:<br>"
                   "<br>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;%s"
                   % (server, fingerprint))
        self._ui.msg_label.setText(msg)

    def _on_cancel(self):
        """
        Slot triggered when the cancel button is clicked or the user presses the escape key/dismisses
        the dialog in another way.
        """
        self._exit_code = QtGui.QDialog.Rejected
        self.close()
        
    def _on_ok(self):
        """
        Slot triggered when the connect/ok button is clicked
        """
        self._exit_code = QtGui.QDialog.Accepted
        self.close()
        
    def _on_show_details(self):
        """
        Slot triggered when the 'Show Details...' button is clicked 
        """
        self._exit_code = TrustForm.SHOW_DETAILS
        self.close()

