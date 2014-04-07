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
Hook that gets called to return the Shotgun user for a specified Perforce user
"""

import sgtk
import os, sys
 
class GetShotgunUser(sgtk.Hook):
    
    def execute(self, p4_user, **kwargs):
        """
        Return the Shotgun user dictionary for the specified Perforce user
        
        :param p4_user:  String
                         The Perforce user name
                     
        :returns:        Dictionary
                         The Shotgun user dictionary for the specified Perforce user
        """
        
        if not p4_user:
            # can't determine Shotgun user if we don't know p4 user!
            return None
        
        # default implementation assumes the perforce user name matches the users login:
        sg_res =self.parent.shotgun.find_one('HumanUser', 
                                             [['login', 'is', p4_user]],
                                             ["id", "type", "email", "login", "name", "image"])
        return sg_res        
        
        