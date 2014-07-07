# Copyright (c) 2013 Shotgun Software Inc.
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
from .ui.password_form import Ui_PasswordForm
    
class PasswordForm(QtGui.QWidget):
    """
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
    
    def __init__(self, server, user, show_details_btn=False, error_msg = None, parent=None):
        """
        Construction
        """
        QtGui.QWidget.__init__(self, parent)
        
        # setup ui
        self.__ui = Ui_PasswordForm()
        self.__ui.setupUi(self)
        
        self.__ui.details_label.setText(("Please enter the password required for user '%s' " 
                                        "to log in to the Perforce server '%s'") 
                                        % (user, server))
        
        self.__ui.details_btn.setVisible(show_details_btn)
        
        self.__ui.invalid_label.setVisible(error_msg is not None)
        self.__ui.invalid_label.setText(error_msg or "")
        
        self.__ui.cancel_btn.clicked.connect(self._on_cancel)
        self.__ui.ok_btn.clicked.connect(self._on_ok)
        self.__ui.details_btn.clicked.connect(self._on_show_details)
        
        self.__ui.password_edit.installEventFilter(self)
        
    @property
    def password(self):
        return str(self.__ui.password_edit.text())

    def eventFilter(self, q_object, event):
        """
        Custom event filter to filter enter-key press events from the password edit
        """
        if q_object == self.__ui.password_edit and event.type() == QtCore.QEvent.KeyPress:
            # handle key-press event in the workspace list control:
            if event.key() == QtCore.Qt.Key_Return:
                # same as pressing ok:
                self._on_ok()
                return True
                
        # let default handler handle the event:
        return QtCore.QObject.eventFilter(self, q_object, event)
    
    def _on_cancel(self):
        """
        """
        self._exit_code = QtGui.QDialog.Rejected
        self.close()
        
    def _on_ok(self):
        """
        """
        self._exit_code = QtGui.QDialog.Accepted
        self.close()
        
    def _on_show_details(self):
        """
        """
        self._exit_code = PasswordForm.SHOW_DETAILS
        self.close()
        
        #self.show_details_clicked.emit(self)
        
        
