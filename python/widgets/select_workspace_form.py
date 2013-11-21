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
from .ui.select_workspace_form import Ui_SelectWorkspaceForm
    
class SelectWorkspaceForm(QtGui.QWidget):
    """
    """
    
    @property
    def exit_code(self):
        return self._exit_code
    
    @property
    def hide_tk_title_bar(self):
        return True    
    
    def __init__(self, server, user, workspace_details, current_workspace=None, parent=None):
        """
        Construction
        """
        QtGui.QWidget.__init__(self, parent)
        
        # setup UI:
        self.__ui = Ui_SelectWorkspaceForm()
        self.__ui.setupUi(self)
        
        self.__ui.details_label.setText("Please choose a Perforce Workspace for user '%s' on server '%s'" 
                                        % (user, server))
        
        self.__ui.cancel_btn.clicked.connect(self._on_cancel)
        self.__ui.ok_btn.clicked.connect(self._on_ok)
        
        self.__ui.workspace_list.clicked.connect(self._on_workspace_clicked)
        self.__ui.workspace_list.doubleClicked.connect(self._on_workspace_doubleclicked)
        self.__ui.workspace_list.currentCellChanged.connect(self._on_workspace_changed)
        self.__ui.workspace_list.installEventFilter(self)
        
        # init list:
        self._initialize(workspace_details, current_workspace)
        
        # update UI:
        self._update_ui()

    @property
    def workspace_name(self):
        """
        Return the name of the currently selected workspace: 
        """
        items = self.__ui.workspace_list.selectedItems()
        if not items:
            return None
        selected_row = items[0].row()
        
        item = self.__ui.workspace_list.item(selected_row, 0)
        return item.text()
    
    def eventFilter(self, q_object, event):
        """
        Custom event filter to filter enter-key press events from the workspace
        list control
        """
        if q_object == self.__ui.workspace_list and event.type() == QtCore.QEvent.KeyPress:
            # handle key-press event in the workspace list control:
            if event.key() == QtCore.Qt.Key_Return and self.__ui.workspace_list.selectedItems():
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
    
    def _on_workspace_doubleclicked(self, index):
        """
        """
        if self.__ui.workspace_list.selectedItems():
            self._on_ok()

    def _on_workspace_clicked(self, index):
        """
        """
        self._update_ui()
    
    def _on_workspace_changed(self, row, column, prev_row, prev_column):
        """
        """
        self._update_ui()
        
    def _update_ui(self):
        """
        """
        something_selected = bool(self.__ui.workspace_list.selectedItems())
        self.__ui.ok_btn.setEnabled(something_selected)
        
    def _initialize(self, workspace_details, current_workspace):
        """
        """
        column_labels = ["Workspace", "Description", "Location"]
        self.__ui.workspace_list.setColumnCount(len(column_labels))
        self.__ui.workspace_list.setHorizontalHeaderLabels(column_labels)
        
        self.__ui.workspace_list.setRowCount(len(workspace_details))
        
        selected_index = -1
        for wsi, ws in enumerate(workspace_details):
            ws_name = ws.get("client", "").strip()
            if ws_name == current_workspace:
                selected_index = wsi
            
            self.__ui.workspace_list.setItem(wsi, 0, QtGui.QTableWidgetItem(ws_name))
            self.__ui.workspace_list.setItem(wsi, 1, QtGui.QTableWidgetItem(ws.get("Description", "").strip()))
            self.__ui.workspace_list.setItem(wsi, 2, QtGui.QTableWidgetItem(ws.get("Root", "").strip()))
            
        if selected_index >= 0:
            self.__ui.workspace_list.selectRow(selected_index)
        else:
            self.__ui.workspace_list.clearSelection()
            
        self.__ui.workspace_list.setSortingEnabled(True)
        self.__ui.workspace_list.resizeColumnToContents(0)
    
    
    
    
    
    
    