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
Hook that is used to retrieve the local file path for a single PublishedFile entity 
"""
from sgtk import Hook
from sgtk import TankError
from sgtk.platform.qt import QtGui, QtCore

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

class ResolvePublishPath(Hook):
    """
    Hook to find and return the local file path for a single PublishedFile entity
    """    
    
    def execute(self, sg_publish_data, **kwargs):
        """
        Main hook entry point
        
        :param sg_publish_data: The PublishedFile entity to find the local file
                                path for.

        :returns:               The local file path of the published file or None.
        """

        # find the url for the publish entity:
        url = sg_publish_data.get("path", {}).get("url")
        if not url:
            raise TankError("The path for the Published File entity does not contain a valid Perforce url!")
        
        # open a perforce connection:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        
        p4 = p4_fw.connection.connect()
        if not p4:
            raise TankError("Failed to connect to Perforce!")

        # convert the url to a local client path:
        path_and_revision = p4_fw.util.depot_path_from_url(url)
        depot_path = path_and_revision[0] if path_and_revision else None
        if not depot_path:
            raise TankError("Couldn't determine Perforce depot_path from url '%s'!" % url)
        local_path = p4_fw.util.depot_to_client_paths(p4, depot_path)[0]
        if not local_path:
            return local_path
        
        check_out_file = False
        if self.parent.engine.has_ui:
            # Ask the user if they want to open the file read-only or check it out for edit:
            msg_box = QtGui.QMessageBox()
            msg_box.setText("Open Published File?")
            msg_box.setInformativeText("Would you like to check out the Published File to edit or just open it read-only?")
            check_out_btn = msg_box.addButton("Check Out and Edit", QtGui.QMessageBox.YesRole)
            msg_box.addButton("Open Read-Only", QtGui.QMessageBox.NoRole)
            # ensure the window stays on top as this is running from the web UI:
            msg_box.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msg_box.exec_()
            if msg_box.clickedButton() == check_out_btn:
                check_out_file = True 
        
        if check_out_file:
            # make sure the file is opened for edit:
            p4_fw.util.open_file_for_edit(p4, local_path, add_if_new=False)
        else:
            # just make sure we have latest:
            try:
                p4.run_sync(local_path)
            except Exception, e:
                raise TankError("Failed to get latest for file: %s", e)

        return local_path