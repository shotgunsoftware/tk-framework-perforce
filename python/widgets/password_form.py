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
        return self._exit_code
    
    @property
    def hide_tk_title_bar(self):
        return True    
    
    show_details_clicked = QtCore.Signal(QtGui.QWidget)
    
    def __init__(self, server, port, user, show_details_btn=False, error_msg = None, parent=None):
        """
        Construction
        """
        QtGui.QWidget.__init__(self, parent)
        
        self.__ui = Ui_PasswordForm()
        self.__ui.setupUi(self)
        
        self.__ui.details_label.setText(("Please enter the password required for user '%s' " 
                                        "to log in to the Perforce server '%s:%d'") 
                                        % (user, server, port))
        
        self.__ui.details_btn.setVisible(show_details_btn)
        
        self.__ui.invalid_label.setVisible(error_msg is not None)
        self.__ui.invalid_label.setText(error_msg)
        
        self.__ui.cancel_btn.clicked.connect(self._on_cancel)
        self.__ui.ok_btn.clicked.connect(self._on_ok)
        self.__ui.details_btn.clicked.connect(self._on_show_details)
        
    
    @property
    def password(self):
        return str(self.__ui.password_edit.text())
    
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
        self.show_details_clicked.emit(self)
        
        
