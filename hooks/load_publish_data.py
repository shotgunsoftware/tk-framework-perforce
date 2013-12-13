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
Hook that gets called to load publish data for a path submitted to Perforce
"""

import sgtk
import os, sys
 
class LoadPublishData(sgtk.Hook):
    
    def execute(self, path, user, workspace, revision, **kwargs):
        """
        Load the specified publish data so that was previously stored by
        the corresponding save_publish_data hook
        
        :publish_path:  String
                        Path to the file being published
                        
        :user:          Dictionary
                        Shotgun HumanUser entity dictionary
                        
        :workspace:     String
                        The Perforce workspace/client that path is being published in
                        
        :revision:      Int
                        Revision of the published file
                     
        :returns:       Dictionary
                        Dictionary of data loaded for the published file.  This data should match 
                        the parameters expected by the 'sgtk.util.register_publish()' function.
        """
        fw = self.parent
        
        # the default implementation does nothing!
        return {}
        
        
        