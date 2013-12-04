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
from .ui.open_connection_form import Ui_OpenConnectionForm
    
class OpenConnectionForm(QtGui.QWidget):
    """
    """
    
    # signals:
    browse_workspace_clicked = QtCore.Signal(QtGui.QWidget)
    open_clicked = QtCore.Signal(QtGui.QWidget)
    
    @property
    def exit_code(self):
        return self._exit_code
    
    def __init__(self, server, user, sg_user, workspace="", setup_proc = None, parent=None):
        """
        Construction
        """
        QtGui.QWidget.__init__(self, parent)
        
        self._exit_code = QtGui.QDialog.Rejected
        self._server = server
        self._user = user
        self._sg_user = sg_user
        
        # create the UI:
        self.__ui = Ui_OpenConnectionForm()
        self.__ui.setupUi(self)
        
        # hook up the UI:
        self.__ui.ok_btn.clicked.connect(self._on_ok)
        self.__ui.cancel_btn.clicked.connect(self._on_cancel)
        self.__ui.workspace_browse_btn.clicked.connect(self._on_browse_workspace)
        self.__ui.workspace_edit.textEdited.connect(self._on_edit_changed)

        self.__ui.workspace_edit.installEventFilter(self)
        
        self.__ui.server_label.setText(self._server)
        self.__ui.user_label.setText(self._user or "<b><font color=\"orange\">Warning, user unknown!</font></b>")
        if not self._user:
            # add tooltip for the user!
            self.__ui.user_label.setToolTip(("Unable to determine Perforce username for the\n"
                                            "current Shotgun user '%s'!") 
                                            % (self._sg_user["name"] if self._sg_user else "Unknown"))
        self.__ui.workspace_edit.setText(workspace)
        
        if setup_proc:
            setup_proc(self)
        
        self._update_ui()
        
    # server property
    @property
    def server(self):
        return self._server
    
    # user property:
    @property
    def user(self):
        return self._user
    
    # workspace property:
    def _get_workspace(self):
        return str(self.__ui.workspace_edit.text())
    def _set_workspace(self, workspace):
        self.__ui.workspace_edit.setText(workspace)
        self._update_ui()
    workspace = property(_get_workspace, _set_workspace)
    
    def eventFilter(self, q_object, event):
        """
        Custom event filter to filter enter-key press events from the workspace edit
        """
        if q_object == self.__ui.workspace_edit and event.type() == QtCore.QEvent.KeyPress:
            # handle key-press event in the workspace list control:
            if event.key() == QtCore.Qt.Key_Return and self.workspace:
                # same as pressing ok:
                self._on_ok()
                return True
                
        # let default handler handle the event:
        return QtCore.QObject.eventFilter(self, q_object, event)    
    
    def _on_cancel(self):
        """
        Called when the cancel button is clicked
        """
        self._exit_code = QtGui.QDialog.Rejected
        self.close()

    def _on_ok(self):
        """
        Called when the ok button is clicked
        """
        self._exit_code = QtGui.QDialog.Accepted
        self.open_clicked.emit(self)
        self._exit_code = QtGui.QDialog.Rejected
        
    def _on_browse_workspace(self):
        """
        """
        self.browse_workspace_clicked.emit(self)
        
    def _on_edit_changed(self):
        self._update_ui()
        
    def _update_ui(self):
        """
        """
        have_workspace = bool(self.workspace)
        self.__ui.ok_btn.setEnabled(have_workspace)        
        
        
        
        
        
        
        
        