# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import photoshop

from tank import Hook
from tank import TankError

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

class SceneOperation(Hook):
    """
    Hook called to perform an operation with the
    current scene
    """
    
    def execute(self, operation, file_path, context, parent_action, file_version, read_only, **kwargs):
        """
        Main hook entry point
        
        :operation:     String
                        Scene operation to perform
        
        :file_path:     String
                        File path to use if the operation
                        requires it (e.g. open)
                    
        :context:       Context
                        The context the file operation is being
                        performed in.
                    
        :parent_action: This is the action that this scene operation is
                        being executed for.  This can be one of: 
                        - open_file
                        - new_file
                        - save_file_as 
                        - version_up
                        
        :file_version:  The version/revision of the file to be opened.  If this is 'None'
                        then the latest version should be opened.
        
        :read_only:     Specifies if the file should be opened read-only or not
                            
        :returns:       Depends on operation:
                        'current_path' - Return the current scene
                                         file path as a String
                        'reset'        - True if scene was reset to an empty 
                                         state, otherwise False
                        all others     - None
        """
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        
        if operation == "current_path":
            # return the current script path
            doc = self._get_active_document()

            if doc.fullName is None:
                # new file?
                path = ""
            else:
                path = doc.fullName.nativePath
            
            return path

        elif operation == "open":
            # check that we have the correct version synced:
            p4 = p4_fw.connection.connect()
            if read_only:
                pass                
                ## just sync the file:
                ## (TODO) - move this to the framework
                #path_to_sync = file_path
                #if file_version:
                #    # sync specific version:
                #    path_to_sync = "%s#%s" % (path_to_sync, file_version)
                #try:
                #    p4.run_sync(path_to_sync)
                #except P4Exception, e:
                #    raise TankError("Failed to sync file '%s'" % path_to_sync)
            else:
                # open the file for edit:
                #p4_fw.util.open_file_for_edit(p4, file_path, add_if_new=False, version=file_version)
                p4_fw.util.open_file_for_edit(p4, file_path, add_if_new=False)
            
            # open the file
            f = photoshop.RemoteObject('flash.filesystem::File', file_path)
            photoshop.app.load(f)            
        
        elif operation == "save":
            # save the current script:
            doc = self._get_active_document()
            doc.save()
        
        elif operation == "save_as":
            doc = self._get_active_document()
            new_file = photoshop.RemoteObject('flash.filesystem::File', file_path)
            
            # and check out the file for edit:
            p4 = p4_fw.connection.connect()
            p4_fw.util.open_file_for_edit(p4, file_path, add_if_new=False)
            
            # no options and do not save as a copy
            # http://cssdk.host.adobe.com/sdk/1.5/docs/WebHelp/references/csawlib/com/adobe/photoshop/Document.html#saveAs()
            doc.saveAs(new_file, None, False)

        elif operation == "reset":
            # do nothing and indicate scene was reset to empty
            return True
        
        elif operation == "prepare_new":
            # file->new. Not sure how to pop up the actual file->new UI,
            # this command will create a document with default properties
            photoshop.app.documents.add()
        
    def _get_active_document(self):
        """
        Returns the currently open document in Photoshop.
        Raises an exeption if no document is active.
        """
        doc = photoshop.app.activeDocument
        if doc is None:
            raise TankError("There is no currently active document!")
        return doc