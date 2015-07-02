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
import maya.cmds as cmds

import tank
from tank import Hook
from tank import TankError
from tank.platform.qt import QtGui

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
        # TODO - grab implementation from maya hook (in same directory as this file)
        # and update to work with motionbuilder by looking at the default hook:
        # https://github.com/shotgunsoftware/tk-multi-workfiles/blob/master/hooks/scene_operation_tk-motionbuilder.py 