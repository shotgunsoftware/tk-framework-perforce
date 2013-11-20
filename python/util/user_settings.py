# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Per-user setting management
"""

from sgtk.platform.qt import QtGui, QtCore

class UserSettings(object):
    """
    """
    
    ORGANIZATION = "Shotgun Software"
    APPLICATION =  "tk-framework-perforce"
    
    def __init__(self, prefix=""):
        
        self._prefix = prefix
        self._settings = None
        
    def get_client(self, project_id):
        """
        """
        if self._settings == None:
            self._settings = self._load_settings()
        
        project_settings = self._settings.get(project_id)
        if project_settings:
            return project_settings.get("client")
            
        return None
    
    def set_client(self, project_id, client):
        """
        """
        if self._settings == None:
            self._settings = self._load_settings()
        
        project_settings = self._settings.setdefault(project_id, {})
        project_settings["client"] = client

        self._save_settings(self._settings)
        
    def _load_settings(self):
        """
        """
        q_settings = QtCore.QSettings(UserSettings.ORGANIZATION, UserSettings.APPLICATION)
        
        settings = {}
        array_sz = q_settings.beginReadArray(self._prefix)
        
        for ai in range(0, array_sz):
            q_settings.setArrayIndex(ai)
            project_id = int(q_settings.value("project_id"))
            client = str(q_settings.value("client"))
            settings[project_id] = {"client":client}
            
        q_settings.endArray()
        
        return settings

    def _save_settings(self, settings):
        """
        """
        q_settings = QtCore.QSettings(UserSettings.ORGANIZATION, UserSettings.APPLICATION)
        
        q_settings.beginWriteArray(self._prefix)
        
        for ai, (project_id, details) in enumerate(settings.iteritems()):
            q_settings.setArrayIndex(ai)
            q_settings.setValue("project_id", project_id)
            q_settings.setValue("client", details.get("client", ""))
            
        q_settings.endArray()