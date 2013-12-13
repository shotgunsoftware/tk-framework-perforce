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
Hook that gets called to store publish data for a path being submitted to Perforce
"""

import sgtk
import os, sys
 
class StorePublishData(sgtk.Hook):
    
    def execute(self, local_path, user, workspace, data, **kwargs):
        """
        Store the specified publish data so that it can be retrieved lated by
        the corresponding load_publish_data hook
        
        :local_path:    String
                        Local path to the file being published
                        
        :user:          Dictionary
                        Shotgun HumanUser entity dictionary
                        
        :workspace:     String
                        The Perforce workspace/client that path is being published in                     

        :data:          Dictionary
                        Dictionary of data to store for the published file.  This data will match the
                        parameters expected by the 'sgtk.util.register_publish()' function.
        """
        fw = self.parent
        
        # the default implementation does nothing!
        pass
        